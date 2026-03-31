from netbox.forms import NetBoxModelForm

from netbox_kea_ctrl.models import KeaHAGroup


class KeaHAGroupForm(NetBoxModelForm):
    class Meta:
        model = KeaHAGroup
        fields = (
            "name",
            "description",
            "mode",
            "enabled",
            "primary_name",
            "secondary_name",
            "primary_control_agent_url",
            "secondary_control_agent_url",
        )
