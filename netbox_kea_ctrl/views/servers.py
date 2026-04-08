from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from netbox_kea_ctrl.forms import KeaServerForm
from netbox_kea_ctrl.models import KeaServer
from netbox_kea_ctrl.services.server_discovery import KeaDiscoveryService


class KeaServerListView(ListView):
    model = KeaServer
    template_name = "netbox_kea_ctrl/server_list.html"
    context_object_name = "object_list"


class KeaServerView(DetailView):
    model = KeaServer
    template_name = "netbox_kea_ctrl/server.html"


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
