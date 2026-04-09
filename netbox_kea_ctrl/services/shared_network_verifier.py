from netbox_kea_ctrl.services.kea_client import KeaClient


class SharedNetworkVerifier:
    def verify(self, shared_network, target_server):
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

        names = []
        if isinstance(result, list) and result:
            args = result[0].get("arguments", {})
            dhcp4 = args.get("Dhcp4", {})
            shared_networks = dhcp4.get("shared-networks", []) or []
            names = [item.get("name") for item in shared_networks if item.get("name")]

        return {
            "exists": shared_network.name in names,
            "target_server": target_server.name,
            "shared_networks": names,
            "raw_result": result,
        }
