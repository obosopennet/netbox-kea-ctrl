from dataclasses import dataclass, field
from typing import Optional

from ipam.models import Prefix

from netbox_kea_ctrl.constants import (
    CF_KEA_OPTION_DATA,
    CF_KEA_POOL_RANGE,
    CF_KEA_SERVER_TAG,
    CF_KEA_SHARED_NETWORK,
    KEA_MANAGED_TAG,
)
from netbox_kea_ctrl.utils import get_prefix_custom_field


@dataclass
class ManagedPrefix:
    prefix_id: int
    prefix: str
    family: int
    status: str
    is_container: bool

    kea_shared_network: Optional[str] = None
    kea_server_tag: Optional[str] = None
    kea_pool_range: Optional[str] = None
    kea_option_data: Optional[str] = None

    validation_state: str = "unknown"
    messages: list[str] = field(default_factory=list)


class PrefixLoader:
    def load(self) -> list[ManagedPrefix]:
        prefixes = Prefix.objects.filter(
            status="active",
            tags__name=KEA_MANAGED_TAG,
        )

        objects: list[ManagedPrefix] = []

        for prefix in prefixes:
            objects.append(
                ManagedPrefix(
                    prefix_id=prefix.pk,
                    prefix=str(prefix.prefix),
                    family=prefix.family,
                    status=str(prefix.status),
                    is_container=False,
                    kea_shared_network=get_prefix_custom_field(prefix, CF_KEA_SHARED_NETWORK),
                    kea_server_tag=get_prefix_custom_field(prefix, CF_KEA_SERVER_TAG),
                    kea_pool_range=get_prefix_custom_field(prefix, CF_KEA_POOL_RANGE),
                    kea_option_data=get_prefix_custom_field(prefix, CF_KEA_OPTION_DATA),
                )
            )

        return objects
