from netbox_kea_ctrl.services.kea_client import KeaClient


class SubnetRemoveError(Exception):
    pass


class SubnetRemover:
    def build_payload(self, shared_network, prefix):
        if shared_network.family != "ipv4":
            raise SubnetRemoveError("Only IPv4 prefixes are supported in the first version.")

        payload = {
            "command": "remote-subnet4-del-by-prefix",
            "service": ["dhcp4"],
            "arguments": {
                "subnets": [
                    {
                        "subnet": str(prefix.prefix),
                    }
                ]
            },
        }
        return payload

    def remove(self, shared_network, prefix, target_server):
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
