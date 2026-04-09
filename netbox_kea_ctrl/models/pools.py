from django.core.exceptions import ValidationError
from django.db import models
from netbox.models import NetBoxModel

from ipam.models import Prefix


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

        if self.start_address and self.end_address:
            if self.start_address > self.end_address:
                raise ValidationError({"end_address": "End address must be greater than or equal to start address."})

        if self.prefix:
            network = self.prefix.prefix.network
            broadcast = self.prefix.prefix.broadcast_address

            if self.start_address and self.start_address not in self.prefix.prefix:
                raise ValidationError({"start_address": "Start address must be داخل prefix range."})

            if self.end_address and self.end_address not in self.prefix.prefix:
                raise ValidationError({"end_address": "End address must be inside prefix range."})

            if str(self.start_address) == str(network):
                raise ValidationError({"start_address": "Start address cannot be the network address."})

            if str(self.end_address) == str(broadcast):
                raise ValidationError({"end_address": "End address cannot be the broadcast address."})

    @property
    def pool_string(self):
        return f"{self.start_address} - {self.end_address}"
