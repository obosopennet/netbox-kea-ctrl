from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from netbox_kea_ctrl.forms import KeaHAGroupForm
from netbox_kea_ctrl.models import KeaHAGroup


class KeaHAGroupListView(ListView):
    model = KeaHAGroup
    template_name = "netbox_kea_ctrl/hagroup_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        return (
            KeaHAGroup.objects.all()
            .select_related("primary_server", "secondary_server")
            .order_by("name")
        )


class KeaHAGroupView(DetailView):
    model = KeaHAGroup
    template_name = "netbox_kea_ctrl/hagroup.html"


class KeaHAGroupCreateView(CreateView):
    model = KeaHAGroup
    form_class = KeaHAGroupForm
    template_name = "netbox_kea_ctrl/object_edit.html"
    success_url = reverse_lazy("plugins:netbox_kea_ctrl:keahagroup_list")


class KeaHAGroupEditView(UpdateView):
    model = KeaHAGroup
    form_class = KeaHAGroupForm
    template_name = "netbox_kea_ctrl/object_edit.html"
    success_url = reverse_lazy("plugins:netbox_kea_ctrl:keahagroup_list")


class HARefreshStatusView(View):
    """
    Midlertidig placeholder for URL-er som allerede finnes i pluginen.
    Senere kan denne hente faktisk HA-status fra Kea.
    """

    def post(self, request, pk):
        obj = get_object_or_404(KeaHAGroup, pk=pk)
        messages.info(request, f"HA status refresh is not implemented yet for '{obj.name}'.")
        return redirect("plugins:netbox_kea_ctrl:keahagroup", pk=obj.pk)

    def get(self, request, pk):
        obj = get_object_or_404(KeaHAGroup, pk=pk)
        return JsonResponse(
            {
                "ha_group": obj.name,
                "status": "not_implemented",
                "detail": "HA status refresh is not implemented yet.",
            }
        )


class HAFailoverView(View):
    """
    Placeholder for manual failover action.
    """

    def post(self, request, pk):
        obj = get_object_or_404(KeaHAGroup, pk=pk)
        messages.warning(request, f"Manual failover is not implemented yet for '{obj.name}'.")
        return redirect("plugins:netbox_kea_ctrl:keahagroup", pk=obj.pk)


class HAMaintenanceView(View):
    """
    Placeholder for maintenance mode actions.
    """

    def post(self, request, pk):
        obj = get_object_or_404(KeaHAGroup, pk=pk)
        messages.warning(request, f"Maintenance mode action is not implemented yet for '{obj.name}'.")
        return redirect("plugins:netbox_kea_ctrl:keahagroup", pk=obj.pk)
