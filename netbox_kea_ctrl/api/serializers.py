from netbox.api.serializers import NetBoxModelSerializer

from netbox_kea_ctrl.models import (
    KeaHAGroup,
    KeaPublishJob,
    KeaServer,
    KeaServerTag,
    KeaSharedNetwork,
)


class KeaHAGroupSerializer(NetBoxModelSerializer):
    class Meta:
        model = KeaHAGroup
        fields = "__all__"


class KeaServerSerializer(NetBoxModelSerializer):
    class Meta:
        model = KeaServer
        fields = "__all__"


class KeaServerTagSerializer(NetBoxModelSerializer):
    class Meta:
        model = KeaServerTag
        fields = "__all__"


class KeaSharedNetworkSerializer(NetBoxModelSerializer):
    class Meta:
        model = KeaSharedNetwork
        fields = "__all__"


class KeaPublishJobSerializer(NetBoxModelSerializer):
    class Meta:
        model = KeaPublishJob
        fields = "__all__"
