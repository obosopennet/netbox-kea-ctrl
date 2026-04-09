from netbox.forms import NetBoxModelForm

from netbox_kea_ctrl.models import KeaHAGroup


class KeaHAGroupForm(NetBoxModelForm):
    class Meta:
        model = KeaHAGroup
        fields = (
            "name",
            "description",
            "mode",
            "service",
            "enabled",
        )
