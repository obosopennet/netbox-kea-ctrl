from django.views.generic import TemplateView

from netbox_kea_ctrl.models import (
    KeaHAGroup,
    KeaPublishJob,
    KeaServer,
    KeaServerTag,
    KeaSharedNetwork,
)


class DashboardView(TemplateView):
    template_name = "netbox_kea_ctrl/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        servers = KeaServer.objects.select_related("ha_group").all()
        ha_groups = KeaHAGroup.objects.all()
        server_tags = KeaServerTag.objects.all()
        shared_networks = KeaSharedNetwork.objects.all()
        publish_jobs = KeaPublishJob.objects.order_by("-created")[:10]

        context["server_count"] = servers.count()
        context["enabled_server_count"] = servers.filter(enabled=True).count()
        context["server_error_count"] = servers.exclude(last_error="").count()
        context["discovered_server_count"] = servers.exclude(last_seen__isnull=True).count()

        context["ha_group_count"] = ha_groups.count()
        context["server_tag_count"] = server_tags.count()
        context["shared_network_count"] = shared_networks.count()

        context["ha_groups"] = ha_groups.prefetch_related("servers")
        context["servers_with_errors"] = servers.exclude(last_error="")[:10]
        context["recent_publish_jobs"] = publish_jobs

        return context
