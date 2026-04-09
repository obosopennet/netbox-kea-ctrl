from django.db import models
from netbox.models import NetBoxModel

from netbox_kea_ctrl.choices import FAMILY_CHOICES, FAMILY_IPV4


class KeaServerTag(NetBoxModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    enabled = models.BooleanField(default=True)
    family = models.CharField(max_length=10, choices=FAMILY_CHOICES, default=FAMILY_IPV4)

    ha_group = models.ForeignKey(
        to="netbox_kea_ctrl.KeaHAGroup",
        on_delete=models.PROTECT,
        related_name="server_tags",
        null=True,
        blank=True,
    )

    configuration_backend_target = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional target identifier used by the publish adapter.",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
