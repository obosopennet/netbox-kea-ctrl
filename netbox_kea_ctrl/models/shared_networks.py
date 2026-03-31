from django.db import models
from netbox.models import NetBoxModel

from netbox_kea_ctrl.choices import FAMILY_CHOICES, FAMILY_IPV4


class KeaSharedNetwork(NetBoxModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    family = models.CharField(max_length=10, choices=FAMILY_CHOICES, default=FAMILY_IPV4)
    enabled = models.BooleanField(default=True)

    server_tag = models.ForeignKey(
        to="netbox_kea_ctrl.KeaServerTag",
        on_delete=models.PROTECT,
        related_name="shared_networks",
    )

    option_data = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
