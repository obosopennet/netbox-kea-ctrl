from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from ipam.models import Prefix

from netbox_kea_ctrl.forms import (
    KeaSharedNetworkCreateForm,
    KeaSharedNetworkEditForm,
    PrefixAssignForm,
)
from netbox_kea_ctrl.models import KeaPublishJob, KeaSharedNetwork
from netbox_kea_ctrl.services.prefix_assignment import PrefixAssignmentService
from netbox_kea_ctrl.services.shared_network_publisher import (
    SharedNetworkPublisher,
    SharedNetworkPublishError,
)
from netbox_kea_ctrl.services.shared_network_verifier import SharedNetworkVerifier
from netbox_kea_ctrl.services.subnet_publisher import SubnetPublisher
from netbox_kea_ctrl.services.subnet_verifier import SubnetVerifier


class KeaSharedNetworkListView(ListView):
    model = KeaSharedNetwork
    template_name = "netbox_kea_ctrl/sharednetwork_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        return (
            KeaSharedNetwork.objects.all()
            .select_related("server_tag", "ha_group")
            .prefetch_related("manual_servers")
            .order_by("name")
        )


class KeaSharedNetworkView(DetailView):
    model = KeaSharedNetwork
    template_name = "netbox_kea_ctrl/sharednetwork.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = PrefixAssignmentService()

        context["publish_targets"] = self.object.get_publish_targets()
        context["assigned_prefixes"] = service.get_prefixes_for_shared_network(self.object)
        context["prefix_verification"] = self.request.session.get(
            f"kea_verify_prefixes_{self.object.pk}"
        )
        return context


class KeaSharedNetworkCreateView(CreateView):
    model = KeaSharedNetwork
    form_class = KeaSharedNetworkCreateForm
    template_name = "netbox_kea_ctrl/object_edit.html"
    success_url = reverse_lazy("plugins:netbox_kea_ctrl:keasharednetwork_list")


class KeaSharedNetworkEditView(UpdateView):
    model = KeaSharedNetwork
    form_class = KeaSharedNetworkEditForm
    template_name = "netbox_kea_ctrl/object_edit.html"
    success_url = reverse_lazy("plugins:netbox_kea_ctrl:keasharednetwork_list")


class KeaSharedNetworkPushView(View):
    def post(self, request, pk):
        obj = get_object_or_404(KeaSharedNetwork, pk=pk)

        targets = list(obj.get_publish_targets())
        if not targets:
            messages.error(request, "No publish targets resolved for this Shared Network.")
            return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=obj.pk)

        target = targets[0]

        job = KeaPublishJob.objects.create(
            created_by=request.user,
            server_tag_name=obj.server_tag.name if obj.server_tag else "",
            status="running",
            summary=f"Push Shared Network '{obj.name}'",
            validation_output={
                "shared_network": obj.name,
                "publish_strategy": obj.publish_strategy,
                "resolved_targets": [server.name for server in targets],
                "selected_target": target.name,
            },
        )

        try:
            publisher = SharedNetworkPublisher()
            outcome = publisher.push(obj, target)

            job.generated_payload = outcome["payload"]
            job.publish_output = outcome["result"]

            kea_ok = False
            kea_errors = []

            result = outcome["result"]
            if isinstance(result, list) and result:
                kea_ok = all(item.get("result") == 0 for item in result)
                kea_errors = [item.get("text", "") for item in result if item.get("result") != 0]
            elif isinstance(result, dict):
                kea_ok = result.get("result") == 0
                if not kea_ok:
                    kea_errors = [result.get("text", "Unknown Kea error")]
            else:
                kea_errors = ["Unexpected Kea response format"]

            if kea_ok:
                job.status = "success"
                messages.success(
                    request,
                    f"Shared Network '{obj.name}' pushed successfully to {target.name}."
                )
            else:
                job.status = "failed"
                job.error_log = "\n".join(filter(None, kea_errors))
                messages.error(
                    request,
                    f"Push failed: {job.error_log or 'Kea returned an error'}"
                )

            job.save()

        except SharedNetworkPublishError as exc:
            job.status = "failed"
            job.error_log = str(exc)
            job.save()
            messages.error(request, f"Push failed: {exc}")

        except Exception as exc:
            job.status = "failed"
            job.error_log = str(exc)
            job.save()
            messages.error(request, f"Push failed: {exc}")

        return redirect("plugins:netbox_kea_ctrl:keapublishjob", pk=job.pk)


class KeaSharedNetworkVerifyView(View):
    def post(self, request, pk):
        obj = get_object_or_404(KeaSharedNetwork, pk=pk)

        targets = list(obj.get_publish_targets())
        if not targets:
            messages.error(request, "No publish targets resolved for this Shared Network.")
            return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=obj.pk)

        target = targets[0]

        try:
            verifier = SharedNetworkVerifier()
            verification = verifier.verify(obj, target)

            if verification["exists"]:
                messages.success(
                    request,
                    f"Shared Network '{obj.name}' exists in Kea on {target.name}."
                )
            else:
                messages.warning(
                    request,
                    f"Shared Network '{obj.name}' was not found in Kea on {target.name}."
                )

        except Exception as exc:
            messages.error(request, f"Verification failed: {exc}")

        return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=obj.pk)


class KeaSharedNetworkAssignPrefixView(View):
    template_name = "netbox_kea_ctrl/sharednetwork_assign_prefix.html"

    def get(self, request, pk):
        obj = get_object_or_404(KeaSharedNetwork, pk=pk)
        service = PrefixAssignmentService()

        assigned_ids = {
            prefix.id for prefix in service.get_prefixes_for_shared_network(obj)
        }

        candidates = [
            prefix for prefix in service.get_candidate_prefixes()
            if prefix.id not in assigned_ids
        ]

        choices = [
            (prefix.id, str(prefix.prefix))
            for prefix in candidates
        ]

        form = PrefixAssignForm(prefix_choices=choices)

        return render(
            request,
            self.template_name,
            {
                "object": obj,
                "form": form,
                "candidate_count": len(choices),
            },
        )

    def post(self, request, pk):
        obj = get_object_or_404(KeaSharedNetwork, pk=pk)
        service = PrefixAssignmentService()

        choices = [
            (prefix.id, str(prefix.prefix))
            for prefix in service.get_candidate_prefixes()
        ]
        form = PrefixAssignForm(request.POST, prefix_choices=choices)

        if form.is_valid():
            prefix = get_object_or_404(Prefix, pk=form.cleaned_data["prefix_id"])
            service.assign_prefix_to_shared_network(prefix, obj)
            messages.success(
                request,
                f"Prefix {prefix.prefix} assigned to Shared Network '{obj.name}'."
            )
            return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=obj.pk)

        return render(
            request,
            self.template_name,
            {
                "object": obj,
                "form": form,
                "candidate_count": len(choices),
            },
        )


class KeaSharedNetworkRemovePrefixView(View):
    def post(self, request, pk, prefix_id):
        obj = get_object_or_404(KeaSharedNetwork, pk=pk)
        prefix = get_object_or_404(Prefix, pk=prefix_id)

        targets = list(obj.get_publish_targets())
        if not targets:
            messages.error(request, "No publish targets resolved for this Shared Network.")
            return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=obj.pk)

        target = targets[0]

        job = KeaPublishJob.objects.create(
            created_by=request.user,
            server_tag_name=obj.server_tag.name if obj.server_tag else "",
            status="running",
            summary=f"Remove Prefix '{prefix.prefix}' from Shared Network '{obj.name}'",
            validation_output={
                "shared_network": obj.name,
                "prefix": str(prefix.prefix),
                "selected_target": target.name,
                "resolved_targets": [server.name for server in targets],
            },
        )

        try:
            from netbox_kea_ctrl.services.subnet_remover import SubnetRemover

            remover = SubnetRemover()
            outcome = remover.remove(obj, prefix, target)

            job.generated_payload = outcome["payload"]
            job.publish_output = outcome["result"]

            kea_ok = False
            kea_errors = []

            result = outcome["result"]
            if isinstance(result, list) and result:
                kea_ok = all(item.get("result") == 0 for item in result)
                kea_errors = [item.get("text", "") for item in result if item.get("result") != 0]
            elif isinstance(result, dict):
                kea_ok = result.get("result") == 0
                if not kea_ok:
                    kea_errors = [result.get("text", "Unknown Kea error")]
            else:
                kea_errors = ["Unexpected Kea response format"]

            if kea_ok:
                service = PrefixAssignmentService()
                service.remove_prefix_from_shared_network(prefix, obj)

                job.status = "success"
                messages.success(
                    request,
                    f"Prefix {prefix.prefix} removed from Shared Network '{obj.name}' and deleted from Kea."
                )
            else:
                job.status = "failed"
                job.error_log = "\n".join(filter(None, kea_errors))
                messages.error(
                    request,
                    f"Prefix removal failed in Kea: {job.error_log or 'Kea returned an error'}"
                )

            job.save()

        except Exception as exc:
            job.status = "failed"
            job.error_log = str(exc)
            job.save()
            messages.error(request, f"Prefix removal failed: {exc}")

        return redirect("plugins:netbox_kea_ctrl:keapublishjob", pk=job.pk)


class KeaSharedNetworkPushPrefixView(View):
    def post(self, request, pk, prefix_id):
        obj = get_object_or_404(KeaSharedNetwork, pk=pk)
        prefix = get_object_or_404(Prefix, pk=prefix_id)

        targets = list(obj.get_publish_targets())
        if not targets:
            messages.error(request, "No publish targets resolved for this Shared Network.")
            return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=obj.pk)

        target = targets[0]

        job = KeaPublishJob.objects.create(
            created_by=request.user,
            server_tag_name=obj.server_tag.name if obj.server_tag else "",
            status="running",
            summary=f"Push Prefix '{prefix.prefix}' to Shared Network '{obj.name}'",
            validation_output={
                "shared_network": obj.name,
                "prefix": str(prefix.prefix),
                "selected_target": target.name,
                "resolved_targets": [server.name for server in targets],
            },
        )

        try:
            publisher = SubnetPublisher()
            outcome = publisher.push(obj, prefix, target)

            job.generated_payload = outcome["payload"]
            job.publish_output = outcome["result"]

            kea_ok = False
            kea_errors = []

            result = outcome["result"]
            if isinstance(result, list) and result:
                kea_ok = all(item.get("result") == 0 for item in result)
                kea_errors = [item.get("text", "") for item in result if item.get("result") != 0]
            elif isinstance(result, dict):
                kea_ok = result.get("result") == 0
                if not kea_ok:
                    kea_errors = [result.get("text", "Unknown Kea error")]
            else:
                kea_errors = ["Unexpected Kea response format"]

            if kea_ok:
                job.status = "success"
                messages.success(
                    request,
                    f"Prefix {prefix.prefix} pushed successfully to {target.name}."
                )
            else:
                job.status = "failed"
                job.error_log = "\n".join(filter(None, kea_errors))
                messages.error(
                    request,
                    f"Prefix push failed: {job.error_log or 'Kea returned an error'}"
                )

            job.save()

        except Exception as exc:
            job.status = "failed"
            job.error_log = str(exc)
            job.save()
            messages.error(request, f"Prefix push failed: {exc}")

        return redirect("plugins:netbox_kea_ctrl:keapublishjob", pk=job.pk)


class KeaSharedNetworkPushAllPrefixesView(View):
    def post(self, request, pk):
        obj = get_object_or_404(KeaSharedNetwork, pk=pk)

        targets = list(obj.get_publish_targets())
        if not targets:
            messages.error(request, "No publish targets resolved for this Shared Network.")
            return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=obj.pk)

        target = targets[0]

        service = PrefixAssignmentService()
        prefixes = service.get_prefixes_for_shared_network(obj)

        if not prefixes:
            messages.warning(
                request,
                "No assigned active managed prefixes found for this Shared Network."
            )
            return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=obj.pk)

        job = KeaPublishJob.objects.create(
            created_by=request.user,
            server_tag_name=obj.server_tag.name if obj.server_tag else "",
            status="running",
            summary=f"Push all Prefixes for Shared Network '{obj.name}'",
            validation_output={
                "shared_network": obj.name,
                "selected_target": target.name,
                "resolved_targets": [server.name for server in targets],
                "prefixes": [str(prefix.prefix) for prefix in prefixes],
            },
        )

        publisher = SubnetPublisher()
        outputs = []
        errors = []

        for prefix in prefixes:
            try:
                outcome = publisher.push(obj, prefix, target)
                outputs.append(
                    {
                        "prefix": str(prefix.prefix),
                        "result": outcome["result"],
                        "payload": outcome["payload"],
                    }
                )

                result = outcome["result"]
                if isinstance(result, list) and result:
                    for item in result:
                        if item.get("result") != 0:
                            errors.append(
                                f"{prefix.prefix}: {item.get('text', 'Unknown error')}"
                            )
                elif isinstance(result, dict):
                    if result.get("result") != 0:
                        errors.append(
                            f"{prefix.prefix}: {result.get('text', 'Unknown error')}"
                        )
                else:
                    errors.append(f"{prefix.prefix}: Unexpected response format")

            except Exception as exc:
                errors.append(f"{prefix.prefix}: {exc}")

        job.publish_output = outputs

        if errors:
            job.status = "failed"
            job.error_log = "\n".join(errors)
            messages.error(
                request,
                f"Push all prefixes completed with errors. See job {job.pk}."
            )
        else:
            job.status = "success"
            messages.success(
                request,
                f"All prefixes for Shared Network '{obj.name}' pushed successfully."
            )

        job.save()
        return redirect("plugins:netbox_kea_ctrl:keapublishjob", pk=job.pk)


class KeaSharedNetworkVerifyPrefixesView(View):
    def post(self, request, pk):
        obj = get_object_or_404(KeaSharedNetwork, pk=pk)

        targets = list(obj.get_publish_targets())
        if not targets:
            messages.error(request, "No publish targets resolved for this Shared Network.")
            return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=obj.pk)

        target = targets[0]

        try:
            verifier = SubnetVerifier()
            verification = verifier.verify_shared_network_prefixes(obj, target)

            runtime_prefixes = verification["prefixes"]

            service = PrefixAssignmentService()
            assigned_prefixes = [
                str(prefix.prefix) for prefix in service.get_prefixes_for_shared_network(obj)
            ]

            present = [prefix for prefix in assigned_prefixes if prefix in runtime_prefixes]
            missing = [prefix for prefix in assigned_prefixes if prefix not in runtime_prefixes]
            extra = [prefix for prefix in runtime_prefixes if prefix not in assigned_prefixes]

            if missing:
                messages.warning(
                    request,
                    f"Verification complete. Present: {len(present)}, Missing: {len(missing)}, Extra: {len(extra)}."
                )
            else:
                messages.success(
                    request,
                    f"Verification complete. All {len(present)} assigned prefixes are present in Kea."
                )

            request.session[f"kea_verify_prefixes_{obj.pk}"] = {
                "target_server": target.name,
                "present": present,
                "missing": missing,
                "extra": extra,
            }

        except Exception as exc:
            messages.error(request, f"Prefix verification failed: {exc}")

        return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=obj.pk)
