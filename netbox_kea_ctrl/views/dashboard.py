from django.views.generic import TemplateView

from netbox_kea_ctrl.models import KeaHAGroup, KeaPublishJob, KeaServerTag, KeaSharedNetwork


class DashboardView(TemplateView):
    template_name = "netbox_kea_ctrl/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["shared_network_count"] = KeaSharedNetwork.objects.count()
        context["server_tag_count"] = KeaServerTag.objects.count()
        context["ha_group_count"] = KeaHAGroup.objects.count()
        context["recent_jobs"] = KeaPublishJob.objects.all()[:10]
        return context
