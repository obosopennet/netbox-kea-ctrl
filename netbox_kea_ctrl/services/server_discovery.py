from django.utils import timezone

from netbox_kea_ctrl.services.kea_client import KeaClient


class KeaDiscoveryService:
    def discover(self, server):
        client = KeaClient(
            base_url=server.api_url,
            timeout=server.request_timeout,
            verify_tls=server.verify_tls,
        )

        result = {
            "status": None,
            "server_tag": None,
            "config": None,
            "ha_info": {},
            "commands": None,
            "errors": [],
        }

        try:
            result["commands"] = client.list_commands(server.service)
        except Exception as exc:
            result["errors"].append(f"list-commands failed: {exc}")

        try:
            result["status"] = client.status_get(server.service)
        except Exception as exc:
            result["errors"].append(f"status-get failed: {exc}")

        try:
            result["server_tag"] = client.server_tag_get(server.service)
        except Exception as exc:
            result["errors"].append(f"server-tag-get failed: {exc}")

        try:
            result["config"] = client.config_get(server.service)
        except Exception as exc:
            result["errors"].append(f"config-get failed: {exc}")

        ha_info = {}
        if isinstance(result["status"], list) and result["status"]:
            entry = result["status"][0]
            args = entry.get("arguments", {})
            ha_info = args.get("high-availability", {})
            if isinstance(ha_info, list) and ha_info:
                ha_info = ha_info[0]
            elif not isinstance(ha_info, dict):
                ha_info = {}

        result["ha_info"] = ha_info

        server.last_seen = timezone.now()
        server.last_status = result["status"] or {}
        server.discovered_ha_info = result["ha_info"] or {}
        server.discovered_config = result["config"] or {}
        server.last_error = "\n".join(result["errors"])

        if isinstance(result["server_tag"], list) and result["server_tag"]:
            args = result["server_tag"][0].get("arguments", {})
            tag = args.get("server-tag") or args.get("server_tag") or ""
            server.discovered_server_tag = tag

        self._populate_normalized_ha_fields(server, result["ha_info"])
        server.save()

        return result

    def _populate_normalized_ha_fields(self, server, ha_info):
        server.discovered_ha_mode = ""
        server.discovered_this_server_name = ""
        server.discovered_local_role = ""
        server.discovered_local_state = ""
        server.discovered_peer_name = ""
        server.discovered_peer_role = ""
        server.discovered_peer_state = ""
        server.discovered_communication_state = ""
        server.discovered_scopes = []

        if not isinstance(ha_info, dict):
            return

        servers = ha_info.get("ha-servers", {})
        local = servers.get("local", {}) or {}
        remote = servers.get("remote", {}) or {}

        server.discovered_ha_mode = ha_info.get("ha-mode", "") or ""
        server.discovered_this_server_name = ha_info.get("this-server-name", "") or ""
        server.discovered_local_role = local.get("role", "") or ""
        server.discovered_local_state = local.get("state", "") or ""
        server.discovered_peer_name = remote.get("server-name", "") or ""
        server.discovered_peer_role = remote.get("role", "") or ""
        server.discovered_peer_state = remote.get("state", "") or ""
        server.discovered_communication_state = ha_info.get("communication-state", "") or ""
        server.discovered_scopes = local.get("scopes", []) or []
