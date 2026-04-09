from django.db import models
from netbox.models import NetBoxModel

from netbox_kea_ctrl.choices import HA_MODE_CHOICES, HA_MODE_HOT_STANDBY


class KeaHAGroup(NetBoxModel):
    SERVICE_CHOICES = (
        ("dhcp4", "DHCPv4"),
        ("dhcp6", "DHCPv6"),
    )

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    mode = models.CharField(max_length=32, choices=HA_MODE_CHOICES, default=HA_MODE_HOT_STANDBY)
    service = models.CharField(max_length=10, choices=SERVICE_CHOICES, default="dhcp4")
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def detected_primary_server(self):
        for server in self.servers.all():
            if getattr(server, "discovered_local_role", "") == "primary":
                return server
        return None

    @property
    def detected_secondary_server(self):
        for server in self.servers.all():
            if getattr(server, "discovered_local_role", "") == "secondary":
                return server
        return None
