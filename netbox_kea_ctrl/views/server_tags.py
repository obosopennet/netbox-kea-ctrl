from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from netbox_kea_ctrl.forms import KeaServerTagForm
from netbox_kea_ctrl.models import KeaServerTag


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
