from netbox.api.viewsets import NetBoxModelViewSet

from netbox_kea_ctrl.models import (
    KeaHAGroup,
    KeaPrefixPool,
    KeaPublishJob,
    KeaServer,
    KeaServerTag,
    KeaSharedNetwork,
)
from .serializers import (
    KeaHAGroupSerializer,
    KeaPrefixPoolSerializer,
    KeaPublishJobSerializer,
    KeaServerSerializer,
    KeaServerTagSerializer,
    KeaSharedNetworkSerializer,
)


class KeaHAGroupViewSet(NetBoxModelViewSet):
    queryset = KeaHAGroup.objects.all()
    serializer_class = KeaHAGroupSerializer


class KeaServerViewSet(NetBoxModelViewSet):
    queryset = KeaServer.objects.all()
    serializer_class = KeaServerSerializer


class KeaServerTagViewSet(NetBoxModelViewSet):
    queryset = KeaServerTag.objects.all()
    serializer_class = KeaServerTagSerializer


class KeaSharedNetworkViewSet(NetBoxModelViewSet):
    queryset = KeaSharedNetwork.objects.all()
    serializer_class = KeaSharedNetworkSerializer


class KeaPrefixPoolViewSet(NetBoxModelViewSet):
    queryset = KeaPrefixPool.objects.all()
    serializer_class = KeaPrefixPoolSerializer


class KeaPublishJobViewSet(NetBoxModelViewSet):
    queryset = KeaPublishJob.objects.all()
    serializer_class = KeaPublishJobSerializer
