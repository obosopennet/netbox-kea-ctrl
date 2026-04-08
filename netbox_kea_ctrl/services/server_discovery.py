from django.utils import timezone

from netbox_kea_ctrl.services.kea_client import KeaClient, KeaAPIError


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

        # Best-effort HA extraction
        ha_info = {}
        if isinstance(result["status"], list) and result["status"]:
            entry = result["status"][0]
            args = entry.get("arguments", {})
            # Keep entire status snapshot; HA presence varies by version/config
            ha_info = {k: v for k, v in args.items() if "ha" in k.lower() or "high" in k.lower()}
        result["ha_info"] = ha_info

        # Persist
        server.last_seen = timezone.now()
        server.last_status = result["status"] or {}
        server.discovered_ha_info = result["ha_info"] or {}
        server.discovered_config = result["config"] or {}
        server.last_error = "\n".join(result["errors"])

        if isinstance(result["server_tag"], list) and result["server_tag"]:
            args = result["server_tag"][0].get("arguments", {})
            tag = args.get("server-tag") or args.get("server_tag") or ""
            server.discovered_server_tag = tag

        server.save()

        return result
