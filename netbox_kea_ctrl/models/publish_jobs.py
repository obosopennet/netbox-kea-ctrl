from django.db import models
from netbox.models import NetBoxModel

from netbox_kea_ctrl.choices import JOB_STATUS_CHOICES, JOB_PENDING


class KeaPublishJob(NetBoxModel):
    status = models.CharField(max_length=20, choices=JOB_STATUS_CHOICES, default=JOB_PENDING)
    server_tag_name = models.CharField(max_length=100, blank=True)

    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    summary = models.TextField(blank=True)
    validation_output = models.JSONField(default=dict, blank=True)
    generated_payload = models.JSONField(default=dict, blank=True)
    publish_output = models.JSONField(default=dict, blank=True)
    error_log = models.TextField(blank=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        label = self.server_tag_name or "all"
        return f"{label} - {self.created}"
