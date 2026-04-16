from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView

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
