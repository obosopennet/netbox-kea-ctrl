from netbox.forms import NetBoxModelForm

from netbox_kea_ctrl.models import KeaServer


class KeaServerForm(NetBoxModelForm):
    class Meta:
        model = KeaServer
        fields = (
            "name",
            "description",
            "enabled",
            "api_url",
            "service",
            "role",
            "ha_group",
            "verify_tls",
            "request_timeout",
        )
