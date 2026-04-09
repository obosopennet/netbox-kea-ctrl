from netbox_kea_ctrl.services.kea_client import KeaClient, KeaAPIError


class SharedNetworkPublishError(Exception):
    pass


class SharedNetworkPublisher:
    def build_payload(self, shared_network):
        if shared_network.family != "ipv4":
            raise SharedNetworkPublishError("Only IPv4 shared networks are supported in the first version.")

        if not shared_network.server_tag:
            raise SharedNetworkPublishError("Shared network is missing server_tag.")

        payload = {
            "command": "remote-network4-set",
            "service": ["dhcp4"],
            "arguments": {
                "shared-networks": [
                    {
                        "name": shared_network.name,
                        "server-tags": [shared_network.server_tag.name],
                    }
                ]
            },
        }

        option_data = self._parse_option_data(shared_network.option_data)
        if option_data:
            payload["arguments"]["shared-networks"][0]["option-data"] = option_data

        return payload

    def push(self, shared_network, target_server):
        payload = self.build_payload(shared_network)

        client = KeaClient(
            base_url=target_server.api_url,
            timeout=target_server.request_timeout,
            verify_tls=target_server.verify_tls,
        )

        result = client.call_raw(payload)
        return {
            "target_server": target_server.name,
            "target_url": target_server.api_url,
            "payload": payload,
            "result": result,
        }

    def _parse_option_data(self, raw):
        if not raw:
            return []

        import yaml

        parsed = yaml.safe_load(raw) or {}
        if not isinstance(parsed, dict):
            raise SharedNetworkPublishError("Option data must be a key/value mapping.")

        return [{"name": key, "data": value} for key, value in parsed.items()]
