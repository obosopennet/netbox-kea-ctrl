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
        summary = {}

        ha = server.discovered_ha_info or {}
        entries = ha.get("high-availability") or []
        if entries:
            ha0 = entries[0]
            servers = ha0.get("ha-servers", {})
            local = servers.get("local", {})
            remote = servers.get("remote", {})

            summary = {
                "ha_mode": ha0.get("ha-mode"),
                "this_server_name": ha0.get("this-server-name"),
                "scopes": local.get("scopes", []),
                "local_role": local.get("role"),
                "local_state": local.get("state"),
                "peer_role": remote.get("role"),
                "peer_state": remote.get("state"),
                "peer_name": remote.get("server-name"),
                "communication_state": ha0.get("communication-state"),
            }

        return summary

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
