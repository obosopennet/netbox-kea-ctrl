from django.urls import path

from .views.dashboard import DashboardView
from .views.validation import PrefixValidationView, PreviewServerTagView, PublishServerTagView
from .views.shared_networks import (
    KeaSharedNetworkListView,
    KeaSharedNetworkView,
    KeaSharedNetworkEditView,
)
from .views.server_tags import (
    KeaServerTagListView,
    KeaServerTagView,
    KeaServerTagEditView,
)
from .views.ha import (
    KeaHAGroupListView,
    KeaHAGroupView,
    KeaHAGroupEditView,
    HARefreshStatusView,
    HASetMaintenanceView,
    HAClearMaintenanceView,
)
from .views.publish_jobs import (
    KeaPublishJobListView,
    KeaPublishJobView,
)

from .views.servers import (
    KeaServerListView,
    KeaServerView,
    KeaServerEditView,
    KeaServerDiscoverView,
    KeaServerTestConnectionView,
)

app_name = "netbox_kea_ctrl"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),

    path("validation/", PrefixValidationView.as_view(), name="prefix_validation"),
    path("validation/preview/<str:server_tag>/", PreviewServerTagView.as_view(), name="preview_server_tag"),
    path("validation/publish/<str:server_tag>/", PublishServerTagView.as_view(), name="publish_server_tag"),

    path("shared-networks/", KeaSharedNetworkListView.as_view(), name="keasharednetwork_list"),
    path("shared-networks/add/", KeaSharedNetworkEditView.as_view(), name="keasharednetwork_add"),
    path("shared-networks/<int:pk>/", KeaSharedNetworkView.as_view(), name="keasharednetwork"),
    path("shared-networks/<int:pk>/edit/", KeaSharedNetworkEditView.as_view(), name="keasharednetwork_edit"),

    path("server-tags/", KeaServerTagListView.as_view(), name="keaservertag_list"),
    path("server-tags/add/", KeaServerTagEditView.as_view(), name="keaservertag_add"),
    path("server-tags/<int:pk>/", KeaServerTagView.as_view(), name="keaservertag"),
    path("server-tags/<int:pk>/edit/", KeaServerTagEditView.as_view(), name="keaservertag_edit"),

    path("ha-groups/", KeaHAGroupListView.as_view(), name="keahagroup_list"),
    path("ha-groups/add/", KeaHAGroupEditView.as_view(), name="keahagroup_add"),
    path("ha-groups/<int:pk>/", KeaHAGroupView.as_view(), name="keahagroup"),
    path("ha-groups/<int:pk>/edit/", KeaHAGroupEditView.as_view(), name="keahagroup_edit"),
    path("ha-groups/<int:pk>/refresh/", HARefreshStatusView.as_view(), name="keahagroup_refresh"),
    path("ha-groups/<int:pk>/maintenance/set/", HASetMaintenanceView.as_view(), name="keahagroup_set_maintenance"),
    path("ha-groups/<int:pk>/maintenance/clear/", HAClearMaintenanceView.as_view(), name="keahagroup_clear_maintenance"),

    path("publish-jobs/", KeaPublishJobListView.as_view(), name="keapublishjob_list"),
    path("publish-jobs/<int:pk>/", KeaPublishJobView.as_view(), name="keapublishjob"),
]
