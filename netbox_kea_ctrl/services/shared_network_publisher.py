from netbox_kea_ctrl.services.kea_client import KeaClient
from netbox_kea_ctrl.utils.raw_config import parse_raw_config


class SharedNetworkPublishError(Exception):
    pass


class SharedNetworkPublisher:
    def build_payload(self, shared_network):
        if shared_network.family != "ipv4":
            raise SharedNetworkPublishError("Only IPv4 shared networks are supported in the first version.")

        if not shared_network.server_tag:
            raise SharedNetworkPublishError("Shared network is missing server_tag.")

        network = {
            "name": shared_network.name,
        }

        # Simple option_data field: key/value map -> Kea option-data list
        simple_option_data = self._parse_simple_option_data(shared_network.option_data)
        if simple_option_data:
            network["option-data"] = simple_option_data

        # Advanced raw_option_data field: merge directly
        raw = parse_raw_config(shared_network.raw_option_data, "raw_option_data") or {}
        if raw:
            if not isinstance(raw, dict):
                raise SharedNetworkPublishError("raw_option_data must parse to an object/dictionary.")

            raw_option_data = raw.get("option-data")
            if raw_option_data:
                if not isinstance(raw_option_data, list):
                    raise SharedNetworkPublishError("'option-data' in raw_option_data must be a list.")

                existing = network.get("option-data", [])
                network["option-data"] = existing + raw_option_data

            # Merge any other supported shared-network attributes directly
            for key, value in raw.items():
                if key == "option-data":
                    continue
                network[key] = value

        payload = {
            "command": "remote-network4-set",
            "service": ["dhcp4"],
            "arguments": {
                "shared-networks": [network],
                "server-tags": [shared_network.server_tag.name],
            },
        }

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

    def _parse_simple_option_data(self, raw):
        if not raw:
            return []

        import yaml

        parsed = yaml.safe_load(raw) or {}
        if not isinstance(parsed, dict):
            raise SharedNetworkPublishError("option_data must be a key/value mapping.")

        option_data = []
        for key, value in parsed.items():
            if isinstance(value, (dict, list)):
                raise SharedNetworkPublishError(
                    f"option_data value for '{key}' must be a simple scalar. "
                    f"Use raw_option_data for advanced option-data structures."
                )
            option_data.append({"name": key, "data": str(value)})

        return option_data
