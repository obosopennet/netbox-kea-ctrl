from netbox.forms import NetBoxModelForm

from netbox_kea_ctrl.models import KeaSharedNetwork


class KeaSharedNetworkForm(NetBoxModelForm):
    class Meta:
        model = KeaSharedNetwork
        fields = (
            "name",
            "description",
            "family",
            "server_tag",
            "enabled",
            "option_data",
        )
