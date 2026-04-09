from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from netbox_kea_ctrl.forms import KeaServerForm
from netbox_kea_ctrl.models import KeaServer
from netbox_kea_ctrl.services.server_discovery import KeaDiscoveryService
from netbox_kea_ctrl.services.server_formatter import KeaServerFormatter


class KeaServerListView(ListView):
    model = KeaServer
    template_name = "netbox_kea_ctrl/server_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        return (
            KeaServer.objects.all()
            .select_related("ha_group")
            .order_by("name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = context["object_list"]

        context["server_count"] = qs.count()
        context["enabled_count"] = qs.filter(enabled=True).count()
        context["error_count"] = qs.exclude(last_error="").count()
        context["discovered_count"] = qs.exclude(last_seen__isnull=True).count()
        return context


class KeaServerView(DetailView):
    model = KeaServer
    template_name = "netbox_kea_ctrl/server.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formatter = KeaServerFormatter()

        server = self.object
        context["status_summary"] = formatter.build_status_summary(server)
        context["ha_summary"] = formatter.build_ha_summary(server)
        context["config_summary"] = formatter.build_config_summary(server)
        return context


class KeaServerCreateView(CreateView):
    model = KeaServer
    form_class = KeaServerForm
    template_name = "netbox_kea_ctrl/object_edit.html"
    success_url = reverse_lazy("plugins:netbox_kea_ctrl:keaserver_list")


class KeaServerEditView(UpdateView):
    model = KeaServer
    form_class = KeaServerForm
    template_name = "netbox_kea_ctrl/object_edit.html"
    success_url = reverse_lazy("plugins:netbox_kea_ctrl:keaserver_list")


class KeaServerDiscoverView(View):
    def post(self, request, pk):
        obj = get_object_or_404(KeaServer, pk=pk)
        service = KeaDiscoveryService()
        result = service.discover(obj)

        if result["errors"]:
            messages.warning(request, f"Discovery completed with errors for {obj.name}")
        else:
            messages.success(request, f"Discovery successful for {obj.name}")

        return redirect("plugins:netbox_kea_ctrl:keaserver", pk=obj.pk)


class KeaServerTestConnectionView(View):
    def post(self, request, pk):
        obj = get_object_or_404(KeaServer, pk=pk)
        service = KeaDiscoveryService()
        result = service.discover(obj)
        return JsonResponse(result, safe=False)
