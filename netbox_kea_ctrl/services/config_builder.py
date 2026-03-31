import ipaddress

from netbox_kea_ctrl.services.option_parser import OptionParser


class KeaConfigBuilder:
    def __init__(self):
        self.option_parser = OptionParser()

    def build_for_server_tag(self, validated_prefixes, server_tag):
        grouped = self.build_grouped(validated_prefixes)
        return grouped.get(server_tag, {"shared-networks": {}, "standalone-subnets": []})

    def build_grouped(self, validated_prefixes):
        result = {}

        for mp in validated_prefixes:
            if not mp.validation_state.startswith("valid") and mp.validation_state != "warning":
                continue

            tag_bucket = result.setdefault(
                mp.kea_server_tag,
                {
                    "shared-networks": {},
                    "standalone-subnets": [],
                },
            )

            subnet_dict = self._build_subnet_dict(mp)

            if mp.kea_shared_network:
                tag_bucket["shared-networks"].setdefault(mp.kea_shared_network, []).append(subnet_dict)
            else:
                tag_bucket["standalone-subnets"].append(subnet_dict)

        return result

    def _build_subnet_dict(self, mp):
        network = ipaddress.ip_network(mp.prefix, strict=False)

        subnet = {
            "subnet": str(network),
        }

        if mp.kea_pool_range:
            subnet["pools"] = [{"pool": mp.kea_pool_range}]

        if mp.kea_option_data:
            subnet["option-data"] = self.option_parser.to_kea_option_data(mp.kea_option_data)

        return subnet
