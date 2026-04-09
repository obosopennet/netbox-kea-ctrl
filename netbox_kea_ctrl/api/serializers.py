from ipam.api.serializers import PrefixSerializer
from netbox.api.serializers import NetBoxModelSerializer

from netbox_kea_ctrl.models import (
    KeaHAGroup,
    KeaPrefixPool,
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
        fields = (
            "id",
            "url",
            "display_url",
            "display",
            "name",
            "description",
            "family",
            "enabled",
            "server_tag",
            "publish_strategy",
            "ha_group",
            "manual_servers",
            "option_data",
            "created",
            "last_updated",
            "custom_fields",
            "tags",
        )


class KeaPrefixPoolSerializer(NetBoxModelSerializer):
    prefix = PrefixSerializer(nested=True)

    class Meta:
        model = KeaPrefixPool
        fields = (
            "id",
            "url",
            "display_url",
            "display",
            "prefix",
            "start_address",
            "end_address",
            "description",
            "enabled",
            "created",
            "last_updated",
            "custom_fields",
            "tags",
        )


class KeaPublishJobSerializer(NetBoxModelSerializer):
    class Meta:
        model = KeaPublishJob
        fields = "__all__"
