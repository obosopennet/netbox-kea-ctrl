from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from netbox_kea_ctrl.forms import KeaHAGroupForm
from netbox_kea_ctrl.models import KeaHAGroup


class KeaHAGroupListView(ListView):
    model = KeaHAGroup
    template_name = "netbox_kea_ctrl/hagroup_list.html"
    context_object_name = "object_list"


class KeaHAGroupView(DetailView):
    model = KeaHAGroup
    template_name = "netbox_kea_ctrl/hagroup.html"


class KeaHAGroupEditView(CreateView, UpdateView):
    model = KeaHAGroup
    form_class = KeaHAGroupForm
    template_name = "netbox_kea_ctrl/object_edit.html"
    success_url = reverse_lazy("plugins:netbox_kea_ctrl:keahagroup_list")


class HARefreshStatusView(View):
    def post(self, request, pk):
        obj = get_object_or_404(KeaHAGroup, pk=pk)
        return JsonResponse({
            "status": "not-implemented",
            "ha_group": obj.name,
        })


class HASetMaintenanceView(View):
    def post(self, request, pk):
        obj = get_object_or_404(KeaHAGroup, pk=pk)
        return JsonResponse({
            "status": "not-implemented",
            "action": "set-maintenance",
            "ha_group": obj.name,
        })


class HAClearMaintenanceView(View):
    def post(self, request, pk):
        obj = get_object_or_404(KeaHAGroup, pk=pk)
        return JsonResponse({
            "status": "not-implemented",
            "action": "clear-maintenance",
            "ha_group": obj.name,
        })
