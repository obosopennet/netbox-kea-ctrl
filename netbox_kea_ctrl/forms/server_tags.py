from netbox.forms import NetBoxModelForm

from netbox_kea_ctrl.models import KeaServerTag


class KeaServerTagForm(NetBoxModelForm):
    class Meta:
        model = KeaServerTag
        fields = (
            "name",
            "description",
            "enabled",
            "family",
            "ha_group",
            "configuration_backend_target",
        )
