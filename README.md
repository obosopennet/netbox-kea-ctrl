# netbox-kea-ctrl

NetBox plugin for managing Kea DHCP configuration, validation, publishing, and HA operations.

## Features planned

- Shared Network management
- Server Tag management
- HA Group visibility and maintenance actions
- Prefix validation from NetBox IPAM
- Kea configuration preview
- Publish to Kea Configuration Backend
- Publish job history and audit

## Prefix requirements

The plugin expects a tag and a few custom fields on `ipam.Prefix`.

### Tag
- `kea-managed`

### Custom fields
- `kea_shared_network`
- `kea_server_tag`
- `kea_pool_range`
- `kea_option_data`

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/<org>/netbox-kea-ctrl.git
```

# NetBox configuration

Add the plugin to your NetBox configuration:


NetBox configuration

Add the plugin to your NetBox configuration:

```
PLUGINS = ["netbox_kea_ctrl"]

PLUGINS_CONFIG = {
    "netbox_kea_ctrl": {
        "enable_ha_actions": True,
        "default_publisher": "dry-run",
    }
}
```

## Migrations

```bash
python manage.py migrate
python manage.py collectstatic --no-input
```
