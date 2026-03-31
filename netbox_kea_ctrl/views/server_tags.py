from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy

from netbox_kea_ctrl.forms import KeaServerTagForm
from netbox_kea_ctrl.models import KeaServerTag


class KeaServerTagListView(ListView):
    model = KeaServerTag
    template_name = "netbox_kea_ctrl/servertag_list.html"
    context_object_name = "object_list"


class KeaServerTagView(DetailView):
    model = KeaServerTag
    template_name = "netbox_kea_ctrl/servertag.html"


class KeaServerTagEditView(CreateView, UpdateView):
    model = KeaServerTag
    form_class = KeaServerTagForm
    template_name = "netbox_kea_ctrl/object_edit.html"
    success_url = reverse_lazy("plugins:netbox_kea_ctrl:keaservertag_list")
