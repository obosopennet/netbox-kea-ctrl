from netbox.forms import NetBoxModelForm

from netbox_kea_ctrl.models import KeaPrefixPool


class KeaPrefixPoolForm(NetBoxModelForm):
    class Meta:
        model = KeaPrefixPool
        fields = (
            "prefix",
            "start_address",
            "end_address",
            "description",
            "enabled",
        )
