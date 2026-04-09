from netbox.api.routers import NetBoxRouter

from .views import (
    KeaHAGroupViewSet,
    KeaPublishJobViewSet,
    KeaServerTagViewSet,
    KeaServerViewSet,
    KeaSharedNetworkViewSet,
)

router = NetBoxRouter()
router.register("ha-groups", KeaHAGroupViewSet)
router.register("servers", KeaServerViewSet)
router.register("server-tags", KeaServerTagViewSet)
router.register("shared-networks", KeaSharedNetworkViewSet)
router.register("publish-jobs", KeaPublishJobViewSet)

urlpatterns = router.urls
