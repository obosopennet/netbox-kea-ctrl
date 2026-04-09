from django.core.exceptions import ValidationError
from django.db import models
from netbox.models import NetBoxModel

from ipam.models import Prefix
from netaddr import IPAddress


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

    class Meta:
        ordering = ("prefix", "start_address")
        verbose_name = "Kea Prefix Pool"
        verbose_name_plural = "Kea Prefix Pools"

    def __str__(self):
        return f"{self.prefix} :: {self.start_address} - {self.end_address}"

    def clean(self):
        super().clean()

        errors = {}

        if self.start_address and self.end_address:
            if IPAddress(self.start_address) > IPAddress(self.end_address):
                errors["end_address"] = "End address must be greater than or equal to start address."

        if self.prefix:
            network = self.prefix.prefix.network
            broadcast = self.prefix.prefix.broadcast

            if self.start_address:
                start_ip = IPAddress(self.start_address)
                if start_ip not in self.prefix.prefix:
                    errors["start_address"] = "Start address must be inside prefix range."
                elif start_ip == network:
                    errors["start_address"] = "Start address cannot be the network address."
                elif start_ip == broadcast:
                    errors["start_address"] = "Start address cannot be the broadcast address."

            if self.end_address:
                end_ip = IPAddress(self.end_address)
                if end_ip not in self.prefix.prefix:
                    errors["end_address"] = "End address must be inside prefix range."
                elif end_ip == network:
                    errors["end_address"] = "End address cannot be the network address."
                elif end_ip == broadcast:
                    errors["end_address"] = "End address cannot be the broadcast address."

        if errors:
            raise ValidationError(errors)

    @property
    def pool_string(self):
        return f"{self.start_address} - {self.end_address}"
