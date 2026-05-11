from django.core.exceptions import ValidationError
from django.db import models
from netbox.models import NetBoxModel

from ipam.models import Prefix
from netaddr import IPAddress

from netbox_kea_ctrl.utils.raw_config import parse_raw_config


class KeaPrefixPool(NetBoxModel):
    prefix = models.ForeignKey(
        Prefix,
        on_delete=models.CASCADE,
        related_name="kea_pools",
    )
    start_address = models.GenericIPAddressField(protocol="IPv4")
    end_address = models.GenericIPAddressField(protocol="IPv4")
    description = models.TextField(blank=True)
    enabled = models.BooleanField(default=True)
    raw_option_data = models.TextField(blank=True)

    class Meta:
        ordering = ("prefix", "start_address")
        verbose_name = "Kea Prefix Pool"
        verbose_name_plural = "Kea Prefix Pools"

    def __str__(self):
        return f"{self.prefix} :: {self.start_address} - {self.end_address}"

    def clean(self):
        super().clean()

        errors = {}

        start_ip = IPAddress(self.start_address) if self.start_address else None
        end_ip = IPAddress(self.end_address) if self.end_address else None

        if start_ip and end_ip and start_ip > end_ip:
            errors["end_address"] = "End address must be greater than or equal to start address."

        if self.prefix:
            network = self.prefix.prefix.network
            broadcast = self.prefix.prefix.broadcast

            if start_ip:
                if start_ip not in self.prefix.prefix:
                    errors["start_address"] = "Start address must be inside prefix range."
                elif start_ip == network:
                    errors["start_address"] = "Start address cannot be the network address."
                elif start_ip == broadcast:
                    errors["start_address"] = "Start address cannot be the broadcast address."

            if end_ip:
                if end_ip not in self.prefix.prefix:
                    errors["end_address"] = "End address must be inside prefix range."
                elif end_ip == network:
                    errors["end_address"] = "End address cannot be the network address."
                elif end_ip == broadcast:
                    errors["end_address"] = "End address cannot be the broadcast address."

        try:
            parse_raw_config(self.raw_option_data, "raw_option_data")
        except ValidationError as exc:
            if hasattr(exc, "message_dict"):
                errors.update(exc.message_dict)
            else:
                errors["raw_option_data"] = exc.messages

        if errors:
            raise ValidationError(errors)

    @property
    def pool_string(self):
        return f"{self.start_address} - {self.end_address}"
