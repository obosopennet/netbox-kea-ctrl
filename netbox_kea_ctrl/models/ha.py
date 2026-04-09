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
        servers = list(self.servers.all())

        # Prefer discovered role from Kea
        for server in servers:
            if (server.discovered_local_role or "").lower() == "primary":
                return server

        # Fallback to manually assigned role
        for server in servers:
            if (server.role or "").lower() == "primary":
                return server

        return None

    @property
    def detected_secondary_server(self):
        servers = list(self.servers.all())

        secondary_candidates = {"secondary", "standby"}

        # Prefer discovered role from Kea
        for server in servers:
            if (server.discovered_local_role or "").lower() in secondary_candidates:
                return server

        # Fallback to manually assigned role
        for server in servers:
            if (server.role or "").lower() == "secondary":
                return server

        return None
