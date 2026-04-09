from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from netbox_kea_ctrl.forms import KeaServerTagForm
from netbox_kea_ctrl.models import KeaPublishJob, KeaServerTag
from netbox_kea_ctrl.services.server_tag_publisher import ServerTagPublisher, ServerTagPublishError


class KeaServerTagListView(ListView):
    model = KeaServerTag
    template_name = "netbox_kea_ctrl/servertag_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        return (
            KeaServerTag.objects.all()
            .select_related("ha_group")
            .order_by("name")
        )


class KeaServerTagView(DetailView):
    model = KeaServerTag
    template_name = "netbox_kea_ctrl/servertag.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object

        if obj.ha_group:
            context["mapped_servers"] = obj.ha_group.servers.all().order_by("name")
        else:
            context["mapped_servers"] = []

        return context


class KeaServerTagCreateView(CreateView):
    model = KeaServerTag
    form_class = KeaServerTagForm
    template_name = "netbox_kea_ctrl/object_edit.html"
    success_url = reverse_lazy("plugins:netbox_kea_ctrl:keaservertag_list")


class KeaServerTagEditView(UpdateView):
    model = KeaServerTag
    form_class = KeaServerTagForm
    template_name = "netbox_kea_ctrl/object_edit.html"
    success_url = reverse_lazy("plugins:netbox_kea_ctrl:keaservertag_list")


class KeaServerTagPushView(View):
    def post(self, request, pk):
        obj = get_object_or_404(KeaServerTag, pk=pk)

        if not obj.ha_group:
            messages.error(request, "Server Tag must be mapped to an HA Group before it can be registered in CB.")
            return redirect("plugins:netbox_kea_ctrl:keaservertag", pk=obj.pk)

        targets = list(obj.ha_group.servers.filter(enabled=True).order_by("name"))
        if not targets:
            messages.error(request, "No enabled Kea Servers found in the mapped HA Group.")
            return redirect("plugins:netbox_kea_ctrl:keaservertag", pk=obj.pk)

        target = targets[0]

        job = KeaPublishJob.objects.create(
            created_by=request.user,
            server_tag_name=obj.name,
            status="running",
            summary=f"Register Server Tag '{obj.name}' in CB",
            validation_output={
                "server_tag": obj.name,
                "ha_group": obj.ha_group.name if obj.ha_group else "",
                "selected_target": target.name,
                "resolved_targets": [server.name for server in targets],
            },
        )

        try:
            publisher = ServerTagPublisher()
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
                messages.success(request, f"Server Tag '{obj.name}' registered successfully in CB.")
            else:
                job.status = "failed"
                job.error_log = "\n".join(filter(None, kea_errors))
                messages.error(request, f"Server Tag registration failed: {job.error_log or 'Kea returned an error'}")

            job.save()

        except ServerTagPublishError as exc:
            job.status = "failed"
            job.error_log = str(exc)
            job.save()
            messages.error(request, f"Server Tag registration failed: {exc}")

        except Exception as exc:
            job.status = "failed"
            job.error_log = str(exc)
            job.save()
            messages.error(request, f"Server Tag registration failed: {exc}")

        return redirect("plugins:netbox_kea_ctrl:keapublishjob", pk=job.pk)
