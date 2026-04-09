from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from netbox_kea_ctrl.forms import KeaSharedNetworkForm
from netbox_kea_ctrl.models import KeaSharedNetwork


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
    form_class = KeaSharedNetworkForm
    template_name = "netbox_kea_ctrl/object_edit.html"
    success_url = reverse_lazy("plugins:netbox_kea_ctrl:keasharednetwork_list")


class KeaSharedNetworkEditView(UpdateView):
    model = KeaSharedNetwork
    form_class = KeaSharedNetworkForm
    template_name = "netbox_kea_ctrl/object_edit.html"
    success_url = reverse_lazy("plugins:netbox_kea_ctrl:keasharednetwork_list")
