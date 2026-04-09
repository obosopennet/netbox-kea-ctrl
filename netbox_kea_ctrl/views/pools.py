from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView

from ipam.models import Prefix

from netbox_kea_ctrl.forms import KeaPrefixPoolForm
from netbox_kea_ctrl.models import KeaPrefixPool, KeaSharedNetwork


class KeaPrefixPoolCreateView(CreateView):
    model = KeaPrefixPool
    form_class = KeaPrefixPoolForm
    template_name = "netbox_kea_ctrl/object_edit.html"

    def get_initial(self):
        initial = super().get_initial()
        prefix_id = self.kwargs.get("prefix_id")
        if prefix_id:
            initial["prefix"] = get_object_or_404(Prefix, pk=prefix_id)
        return initial

    def get_success_url(self):
        return reverse_lazy(
            "plugins:netbox_kea_ctrl:keasharednetwork",
            kwargs={"pk": self.kwargs["pk"]},
        )


class KeaPrefixPoolEditView(UpdateView):
    model = KeaPrefixPool
    form_class = KeaPrefixPoolForm
    template_name = "netbox_kea_ctrl/object_edit.html"

    def get_success_url(self):
        return reverse_lazy(
            "plugins:netbox_kea_ctrl:keasharednetwork",
            kwargs={"pk": self.kwargs["pk"]},
        )


class KeaPrefixPoolRemoveView(View):
    def post(self, request, pk, pool_id):
        shared_network = get_object_or_404(KeaSharedNetwork, pk=pk)
        pool = get_object_or_404(KeaPrefixPool, pk=pool_id)

        pool.delete()
        messages.success(request, f"Pool {pool.start_address} - {pool.end_address} removed from NetBox.")
        return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=shared_network.pk)
