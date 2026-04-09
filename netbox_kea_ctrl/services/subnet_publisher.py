from netbox_kea_ctrl.services.kea_client import KeaClient


class SubnetPublishError(Exception):
    pass


class SubnetPublisher:
    def build_payload(self, shared_network, prefix):
        if shared_network.family != "ipv4":
            raise SubnetPublishError("Only IPv4 prefixes are supported in the first version.")

        if not shared_network.server_tag:
            raise SubnetPublishError("Shared Network is missing server_tag.")

        subnet = {
            "subnet": str(prefix.prefix),
            "id": self._build_subnet_id(prefix),
            "shared-network-name": shared_network.name,
        }

        pool_range = (prefix.custom_field_data or {}).get("kea_pool_range")
        if pool_range:
            subnet["pools"] = [{"pool": pool_range}]

        option_data = self._parse_option_data((prefix.custom_field_data or {}).get("kea_option_data"))
        if option_data:
            subnet["option-data"] = option_data

        payload = {
            "command": "remote-subnet4-set",
            "service": ["dhcp4"],
            "arguments": {
                "subnets": [subnet],
                "server-tags": [shared_network.server_tag.name],
            },
        }
        return payload

    def push(self, shared_network, prefix, target_server):
        payload = self.build_payload(shared_network, prefix)

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

    def _build_subnet_id(self, prefix):
        return prefix.id

    def _parse_option_data(self, raw):
        if not raw:
            return []

        import yaml

        parsed = yaml.safe_load(raw) or {}
        if not isinstance(parsed, dict):
            raise SubnetPublishError("Prefix option data must be a key/value mapping.")

        return [{"name": key, "data": value} for key, value in parsed.items()]
