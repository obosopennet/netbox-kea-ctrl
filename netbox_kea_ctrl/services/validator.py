import ipaddress

from netbox_kea_ctrl.constants import (
    VALIDATION_ERROR,
    VALIDATION_VALID,
    VALIDATION_VALID_STANDALONE,
    VALIDATION_WARNING,
)
from netbox_kea_ctrl.services.option_parser import OptionParser


class PrefixValidator:
    def __init__(self, server_tags, shared_networks):
        self.server_tags = {obj.name: obj for obj in server_tags}
        self.shared_networks = {obj.name: obj for obj in shared_networks}
        self.option_parser = OptionParser()

    def validate(self, mp):
        if not mp.kea_server_tag:
            mp.validation_state = VALIDATION_ERROR
            mp.messages.append("Missing kea_server_tag")
            return mp

        if mp.kea_server_tag not in self.server_tags:
            mp.validation_state = VALIDATION_ERROR
            mp.messages.append(f"Unknown server tag: {mp.kea_server_tag}")
            return mp

        if mp.kea_shared_network:
            sn = self.shared_networks.get(mp.kea_shared_network)
            if not sn:
                mp.validation_state = VALIDATION_ERROR
                mp.messages.append(f"Unknown shared network: {mp.kea_shared_network}")
                return mp

            if not sn.enabled:
                mp.validation_state = VALIDATION_ERROR
                mp.messages.append(f"Shared network {sn.name} is disabled")
                return mp

            expected_family = 4 if sn.family == "ipv4" else 6
            if mp.family != expected_family:
                mp.validation_state = VALIDATION_ERROR
                mp.messages.append("Family mismatch between prefix and shared network")
                return mp

            if sn.server_tag.name != mp.kea_server_tag:
                mp.validation_state = VALIDATION_ERROR
                mp.messages.append(
                    f"Server tag mismatch: prefix={mp.kea_server_tag}, shared-network={sn.server_tag.name}"
                )
                return mp

        if mp.kea_pool_range:
            pool_error = self._validate_pool(mp.prefix, mp.kea_pool_range)
            if pool_error:
                mp.validation_state = VALIDATION_ERROR
                mp.messages.append(pool_error)
                return mp

        if mp.kea_option_data:
            try:
                self.option_parser.parse(mp.kea_option_data)
            except Exception as exc:
                mp.validation_state = VALIDATION_ERROR
                mp.messages.append(f"Invalid option data: {exc}")
                return mp

        mp.validation_state = VALIDATION_VALID_STANDALONE if not mp.kea_shared_network else VALIDATION_VALID

        if not mp.kea_pool_range:
            mp.validation_state = VALIDATION_WARNING
            mp.messages.append("No pool range configured")

        return mp

    def _validate_pool(self, prefix: str, pool_range: str):
        try:
            network = ipaddress.ip_network(prefix, strict=False)
            start_s, end_s = [x.strip() for x in pool_range.split("-", 1)]
            start_ip = ipaddress.ip_address(start_s)
            end_ip = ipaddress.ip_address(end_s)
        except Exception as exc:
            return f"Invalid pool format: {exc}"

        if start_ip.version != network.version or end_ip.version != network.version:
            return "Pool IP version mismatch with prefix"

        if start_ip not in network or end_ip not in network:
            return "Pool range is outside prefix"

        if int(start_ip) > int(end_ip):
            return "Pool start is greater than pool end"

        return None
