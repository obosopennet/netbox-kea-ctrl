from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from netbox_kea_ctrl.forms import KeaSharedNetworkCreateForm, KeaSharedNetworkEditForm
from netbox_kea_ctrl.models import KeaPublishJob, KeaSharedNetwork
from netbox_kea_ctrl.services.shared_network_publisher import (
    SharedNetworkPublisher,
    SharedNetworkPublishError,
)


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
        context["publish_targets"] = self.object.get_publish_targets()
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
            job.status = "success"
            job.save()

            messages.success(
                request,
                f"Shared Network '{obj.name}' pushed successfully to {target.name}."
            )

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
