from netbox.plugins import PluginMenu, PluginMenuItem

menu_items = (
    PluginMenuItem(
        link="plugins:netbox_kea_ctrl:dashboard",
        link_text="Dashboard",
    ),
    PluginMenuItem(
        link="plugins:netbox_kea_ctrl:keasharednetwork_list",
        link_text="Shared Networks",
    ),
    PluginMenuItem(
        link="plugins:netbox_kea_ctrl:keaservertag_list",
        link_text="Server Tags",
    ),
    PluginMenuItem(
        link="plugins:netbox_kea_ctrl:keahagroup_list",
        link_text="HA Groups",
    ),
    PluginMenuItem(
        link="plugins:netbox_kea_ctrl:prefix_validation",
        link_text="Prefix Validation",
    ),
    PluginMenuItem(
        link="plugins:netbox_kea_ctrl:keapublishjob_list",
        link_text="Publish Jobs",
    ),
    PluginMenuItem(
         link="plugins:netbox_kea_ctrl:keaserver_list",
         link_text="Kea Servers",
),
)

menu = PluginMenu(
    label="Kea",
    groups=(("Kea", menu_items),),
    icon_class="mdi mdi-lan",
)
