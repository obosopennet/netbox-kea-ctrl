from netbox.api.viewsets import NetBoxModelViewSet
from netbox_kea_ctrl.models import KeaServer
from .serializers import KeaServerSerializer


class KeaServerViewSet(NetBoxModelViewSet):
    queryset = KeaServer.objects.all()
    serializer_class = KeaServerSerializer
