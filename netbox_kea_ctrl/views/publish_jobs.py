from django.views.generic import ListView, DetailView

from netbox_kea_ctrl.models import KeaPublishJob


class KeaPublishJobListView(ListView):
    model = KeaPublishJob
    template_name = "netbox_kea_ctrl/publishjob_list.html"
    context_object_name = "object_list"


class KeaPublishJobView(DetailView):
    model = KeaPublishJob
    template_name = "netbox_kea_ctrl/publishjob.html"
