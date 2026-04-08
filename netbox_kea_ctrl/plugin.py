from netbox.plugins import PluginConfig


class NetBoxKeaCtrlConfig(PluginConfig):
    name = "netbox_kea_ctrl"
    verbose_name = "NetBox Kea Ctrl"
    description = "NetBox plugin for Kea DHCP validation, publishing, and HA operations"
    version = "0.1.0"
    author = "OBOS Nett"
    base_url = "kea-ctrl"

    menu = "netbox_kea_ctrl.navigation.menu"

    required_settings = []
    default_settings = {
        "enable_ha_actions": True,
        "default_publisher": "dry-run",
    }


config = NetBoxKeaCtrlConfig
