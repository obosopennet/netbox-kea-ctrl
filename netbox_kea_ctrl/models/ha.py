from django.db import models
from netbox.models import NetBoxModel

from netbox_kea_ctrl.choices import HA_MODE_CHOICES, HA_MODE_HOT_STANDBY


class KeaHAGroup(NetBoxModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    mode = models.CharField(max_length=32, choices=HA_MODE_CHOICES, default=HA_MODE_HOT_STANDBY)
    enabled = models.BooleanField(default=True)

    primary_name = models.CharField(max_length=100, blank=True)
    secondary_name = models.CharField(max_length=100, blank=True)

    primary_control_agent_url = models.URLField(blank=True)
    secondary_control_agent_url = models.URLField(blank=True)

    last_status = models.JSONField(default=dict, blank=True)
    last_status_check = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
