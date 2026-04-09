from django.urls import path

from .views.dashboard import DashboardView
from .views.validation import PrefixValidationView, PreviewServerTagView, PublishServerTagView
from .views.shared_networks import (
    KeaSharedNetworkListView,
    KeaSharedNetworkView,
    KeaSharedNetworkCreateView,
    KeaSharedNetworkEditView,
    KeaSharedNetworkPushView,
    KeaSharedNetworkVerifyView,
    KeaSharedNetworkAssignPrefixView,
    KeaSharedNetworkRemovePrefixView,
    KeaSharedNetworkPushPrefixView,
)
from .views.server_tags import (
    KeaServerTagListView,
    KeaServerTagView,
    KeaServerTagCreateView,
    KeaServerTagEditView,
    KeaServerTagPushView,
)
from .views.ha import (
    KeaHAGroupListView,
    KeaHAGroupView,
    KeaHAGroupCreateView,
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
    KeaServerCreateView,
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
    path("shared-networks/add/", KeaSharedNetworkCreateView.as_view(), name="keasharednetwork_add"),
    path("shared-networks/<int:pk>/", KeaSharedNetworkView.as_view(), name="keasharednetwork"),
    path("shared-networks/<int:pk>/edit/", KeaSharedNetworkEditView.as_view(), name="keasharednetwork_edit"),
    path("shared-networks/<int:pk>/push/", KeaSharedNetworkPushView.as_view(), name="keasharednetwork_push"),
    path("shared-networks/<int:pk>/verify/", KeaSharedNetworkVerifyView.as_view(), name="keasharednetwork_verify"),
    path("shared-networks/<int:pk>/assign-prefix/", KeaSharedNetworkAssignPrefixView.as_view(), name="keasharednetwork_assign_prefix"),
    path("shared-networks/<int:pk>/remove-prefix/<int:prefix_id>/", KeaSharedNetworkRemovePrefixView.as_view(), name="keasharednetwork_remove_prefix"),
    path("shared-networks/<int:pk>/push-prefix/<int:prefix_id>/", KeaSharedNetworkPushPrefixView.as_view(), name="keasharednetwork_push_prefix",),
    
    path("server-tags/", KeaServerTagListView.as_view(), name="keaservertag_list"),
    path("server-tags/add/", KeaServerTagCreateView.as_view(), name="keaservertag_add"),
    path("server-tags/<int:pk>/", KeaServerTagView.as_view(), name="keaservertag"),
    path("server-tags/<int:pk>/edit/", KeaServerTagEditView.as_view(), name="keaservertag_edit"),
    path("server-tags/<int:pk>/push/", KeaServerTagPushView.as_view(), name="keaservertag_push"),

    path("ha-groups/", KeaHAGroupListView.as_view(), name="keahagroup_list"),
    path("ha-groups/add/", KeaHAGroupCreateView.as_view(), name="keahagroup_add"),
    path("ha-groups/<int:pk>/", KeaHAGroupView.as_view(), name="keahagroup"),
    path("ha-groups/<int:pk>/edit/", KeaHAGroupEditView.as_view(), name="keahagroup_edit"),
    path("ha-groups/<int:pk>/refresh/", HARefreshStatusView.as_view(), name="keahagroup_refresh"),
    path("ha-groups/<int:pk>/maintenance/set/", HASetMaintenanceView.as_view(), name="keahagroup_set_maintenance"),
    path("ha-groups/<int:pk>/maintenance/clear/", HAClearMaintenanceView.as_view(), name="keahagroup_clear_maintenance"),

    path("publish-jobs/", KeaPublishJobListView.as_view(), name="keapublishjob_list"),
    path("publish-jobs/<int:pk>/", KeaPublishJobView.as_view(), name="keapublishjob"),
    
    path("servers/", KeaServerListView.as_view(), name="keaserver_list"),
    path("servers/add/", KeaServerCreateView.as_view(), name="keaserver_add"),
    path("servers/<int:pk>/", KeaServerView.as_view(), name="keaserver"),
    path("servers/<int:pk>/edit/", KeaServerEditView.as_view(), name="keaserver_edit"),
    path("servers/<int:pk>/discover/", KeaServerDiscoverView.as_view(), name="keaserver_discover"),
    path("servers/<int:pk>/test/", KeaServerTestConnectionView.as_view(), name="keaserver_test"),

]
