class KeaServerFormatter:
    def build_status_summary(self, server):
        summary = {}

        status = server.last_status
        if isinstance(status, list) and status:
            item = status[0]
            args = item.get("arguments", {})

            summary = {
                "result": item.get("result"),
                "pid": args.get("pid"),
                "uptime": args.get("uptime"),
                "reload": args.get("reload"),
                "socket_status": (args.get("sockets") or {}).get("status"),
                "dhcp_state": args.get("dhcp-state", {}),
            }

        return summary

    def build_ha_summary(self, server):
        return {
            "ha_mode": server.discovered_ha_mode,
            "this_server_name": server.discovered_this_server_name,
            "local_role": server.discovered_local_role,
            "local_state": server.discovered_local_state,
            "peer_name": server.discovered_peer_name,
            "peer_role": server.discovered_peer_role,
            "peer_state": server.discovered_peer_state,
            "communication_state": server.discovered_communication_state,
            "scopes": server.discovered_scopes or [],
        }

    def build_config_summary(self, server):
        summary = {
            "hash": None,
            "subnet4_count": 0,
            "shared_network4_count": 0,
            "hooks": [],
        }

        config = server.discovered_config
        if isinstance(config, list) and config:
            item = config[0]
            args = item.get("arguments", {})

            summary["hash"] = args.get("hash")

            dhcp4 = args.get("Dhcp4", {})
            if dhcp4:
                summary["subnet4_count"] = len(dhcp4.get("subnet4", []) or [])
                summary["shared_network4_count"] = len(dhcp4.get("shared-networks", []) or [])

                hooks = dhcp4.get("hooks-libraries", []) or []
                summary["hooks"] = [h.get("library") for h in hooks if h.get("library")]

        return summary
