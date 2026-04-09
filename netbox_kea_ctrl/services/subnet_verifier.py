from netbox_kea_ctrl.services.kea_client import KeaClient


class SubnetVerifier:
    def verify_shared_network_prefixes(self, shared_network, target_server):
        client = KeaClient(
            base_url=target_server.api_url,
            timeout=target_server.request_timeout,
            verify_tls=target_server.verify_tls,
        )

        if shared_network.family != "ipv4":
            raise ValueError("Only IPv4 shared networks are supported in the first version.")

        result = client.call_raw({
            "command": "config-get",
            "service": ["dhcp4"],
        })

        runtime_prefixes = []
        if isinstance(result, list) and result:
            args = result[0].get("arguments", {})
            dhcp4 = args.get("Dhcp4", {})
            shared_networks = dhcp4.get("shared-networks", []) or []

            for item in shared_networks:
                if item.get("name") != shared_network.name:
                    continue
                for subnet in item.get("subnet4", []) or []:
                    if subnet.get("subnet"):
                        runtime_prefixes.append(subnet.get("subnet"))

        return {
            "target_server": target_server.name,
            "shared_network": shared_network.name,
            "prefixes": sorted(runtime_prefixes),
            "raw_result": result,
        }
