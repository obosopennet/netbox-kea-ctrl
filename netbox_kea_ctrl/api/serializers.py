from netbox.api.serializers import NetBoxModelSerializer
from netbox_kea_ctrl.models import KeaServer


class KeaServerSerializer(NetBoxModelSerializer):
    class Meta:
        model = KeaServer
        fields = "__all__"
