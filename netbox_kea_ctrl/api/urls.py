from netbox.api.routers import NetBoxRouter
from .views import KeaServerViewSet

router = NetBoxRouter()
router.register("servers", KeaServerViewSet)

urlpatterns = router.urls
