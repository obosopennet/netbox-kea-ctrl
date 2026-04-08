from django.db import models
from netbox.models import NetBoxModel


class KeaServer(NetBoxModel):
    ROLE_CHOICES = (
        ("primary", "Primary"),
        ("secondary", "Secondary"),
        ("standalone", "Standalone"),
        ("unknown", "Unknown"),
    )

    SERVICE_CHOICES = (
        ("dhcp4", "DHCPv4"),
        ("dhcp6", "DHCPv6"),
    )

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    enabled = models.BooleanField(default=True)

    api_url = models.URLField(
        help_text="Kea API endpoint or Control Agent URL, e.g. http://10.0.0.10:8000/"
    )
    service = models.CharField(max_length=10, choices=SERVICE_CHOICES, default="dhcp4")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="unknown")

    ha_group = models.ForeignKey(
        to="netbox_kea_ctrl.KeaHAGroup",
        on_delete=models.PROTECT,
        related_name="servers",
        null=True,
        blank=True,
    )

    verify_tls = models.BooleanField(default=True)
    request_timeout = models.PositiveIntegerField(default=5)

    discovered_server_tag = models.CharField(max_length=100, blank=True)
    discovered_ha_info = models.JSONField(default=dict, blank=True)
    discovered_config = models.JSONField(default=dict, blank=True)

    last_seen = models.DateTimeField(null=True, blank=True)
    last_status = models.JSONField(default=dict, blank=True)
    last_error = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
