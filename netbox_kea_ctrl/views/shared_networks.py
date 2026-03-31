from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy

from netbox_kea_ctrl.forms import KeaSharedNetworkForm
from netbox_kea_ctrl.models import KeaSharedNetwork


class KeaSharedNetworkListView(ListView):
    model = KeaSharedNetwork
    template_name = "netbox_kea_ctrl/sharednetwork_list.html"
    context_object_name = "object_list"


class KeaSharedNetworkView(DetailView):
    model = KeaSharedNetwork
    template_name = "netbox_kea_ctrl/sharednetwork.html"


class KeaSharedNetworkEditView(CreateView, UpdateView):
    model = KeaSharedNetwork
    form_class = KeaSharedNetworkForm
    template_name = "netbox_kea_ctrl/object_edit.html"
    success_url = reverse_lazy("plugins:netbox_kea_ctrl:keasharednetwork_list")
