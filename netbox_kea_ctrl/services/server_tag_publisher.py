from netbox_kea_ctrl.services.kea_client import KeaClient


class ServerTagPublishError(Exception):
    pass


class ServerTagPublisher:
    def build_payload(self, server_tag):
        if server_tag.family != "ipv4":
            raise ServerTagPublishError("Only IPv4 server-tags are supported in the first version.")

        return {
            "command": "remote-server4-set",
            "service": ["dhcp4"],
            "arguments": {
                "servers": [
                    {
                        "server-tag": server_tag.name,
                        "description": server_tag.description or "",
                    }
                ]
            },
        }

    def push(self, server_tag, target_server):
        payload = self.build_payload(server_tag)

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
