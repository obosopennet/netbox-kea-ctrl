from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView

from ipam.models import Prefix

from netbox_kea_ctrl.forms import KeaPrefixPoolForm
from netbox_kea_ctrl.models import KeaPrefixPool, KeaPublishJob, KeaSharedNetwork
from netbox_kea_ctrl.services.subnet_publisher import SubnetPublisher


class KeaPrefixPoolCreateView(CreateView):
    model = KeaPrefixPool
    form_class = KeaPrefixPoolForm
    template_name = "netbox_kea_ctrl/object_edit.html"

    def get_initial(self):
        initial = super().get_initial()
        prefix_id = self.kwargs.get("prefix_id")
        if prefix_id:
            initial["prefix"] = get_object_or_404(Prefix, pk=prefix_id)
        return initial

    def get_success_url(self):
        return reverse_lazy(
            "plugins:netbox_kea_ctrl:keasharednetwork",
            kwargs={"pk": self.kwargs["pk"]},
        )


class KeaPrefixPoolEditView(UpdateView):
    model = KeaPrefixPool
    form_class = KeaPrefixPoolForm
    template_name = "netbox_kea_ctrl/object_edit.html"

    def get_success_url(self):
        return reverse_lazy(
            "plugins:netbox_kea_ctrl:keasharednetwork",
            kwargs={"pk": self.kwargs["pk"]},
        )


class KeaPrefixPoolRemoveView(View):
    def post(self, request, pk, pool_id):
        shared_network = get_object_or_404(KeaSharedNetwork, pk=pk)
        pool = get_object_or_404(KeaPrefixPool, pk=pool_id)

        prefix = pool.prefix
        pool_string = pool.pool_string

        targets = list(shared_network.get_publish_targets())
        if not targets:
            messages.error(
                request,
                "No publish targets resolved for this Shared Network. Pool was not removed."
            )
            return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=shared_network.pk)

        target = targets[0]

        job = KeaPublishJob.objects.create(
            created_by=request.user,
            server_tag_name=shared_network.server_tag.name if shared_network.server_tag else "",
            status="running",
            summary=f"Remove Pool '{pool_string}' from Prefix '{prefix.prefix}'",
            validation_output={
                "shared_network": shared_network.name,
                "prefix": str(prefix.prefix),
                "pool": pool_string,
                "selected_target": target.name,
                "resolved_targets": [server.name for server in targets],
            },
        )

        try:
            # 1. Remove pool in NetBox
            pool.delete()

            # 2. Repush prefix to Kea with remaining pools
            publisher = SubnetPublisher()
            outcome = publisher.push(shared_network, prefix, target)

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
                    f"Pool {pool_string} removed from NetBox and prefix {prefix.prefix} updated in Kea."
                )
            else:
                job.status = "failed"
                job.error_log = "\n".join(filter(None, kea_errors))
                messages.error(
                    request,
                    f"Pool removed in NetBox, but failed to update Kea: {job.error_log or 'Kea returned an error'}"
                )

            job.save()

        except Exception as exc:
            job.status = "failed"
            job.error_log = str(exc)
            job.save()
            messages.error(request, f"Pool removal failed: {exc}")

        return redirect("plugins:netbox_kea_ctrl:keapublishjob", pk=job.pk)
