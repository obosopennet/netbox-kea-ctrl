from django.core.exceptions import ValidationError
from django.db import models
from netbox.models import NetBoxModel


class KeaHAGroup(NetBoxModel):
    MODE_HOT_STANDBY = "hot-standby"
    MODE_LOAD_BALANCING = "load-balancing"

    MODE_CHOICES = (
        (MODE_HOT_STANDBY, "Hot standby"),
        (MODE_LOAD_BALANCING, "Load balancing"),
    )

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    mode = models.CharField(
        max_length=32,
        choices=MODE_CHOICES,
        default=MODE_HOT_STANDBY,
    )
    enabled = models.BooleanField(default=True)

    primary_server = models.ForeignKey(
        to="netbox_kea_ctrl.KeaServer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ha_groups_as_primary",
    )
    secondary_server = models.ForeignKey(
        to="netbox_kea_ctrl.KeaServer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ha_groups_as_secondary",
    )

    valid_lifetime = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Global valid-lifetime for this HA Group.",
    )
    min_valid_lifetime = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Global min-valid-lifetime for this HA Group.",
    )
    max_valid_lifetime = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Global max-valid-lifetime for this HA Group.",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        errors = {}

        if self.primary_server and self.secondary_server:
            if self.primary_server_id == self.secondary_server_id:
                errors["secondary_server"] = "Primary and secondary server must be different."

        if self.min_valid_lifetime is not None and self.max_valid_lifetime is not None:
            if self.min_valid_lifetime > self.max_valid_lifetime:
                errors["min_valid_lifetime"] = (
                    "min_valid_lifetime cannot be greater than max_valid_lifetime."
                )
                errors["max_valid_lifetime"] = (
                    "max_valid_lifetime cannot be less than min_valid_lifetime."
                )

        if self.valid_lifetime is not None and self.min_valid_lifetime is not None:
            if self.valid_lifetime < self.min_valid_lifetime:
                errors["valid_lifetime"] = (
                    "valid_lifetime cannot be less than min_valid_lifetime."
                )

        if self.valid_lifetime is not None and self.max_valid_lifetime is not None:
            if self.valid_lifetime > self.max_valid_lifetime:
                errors["valid_lifetime"] = (
                    "valid_lifetime cannot be greater than max_valid_lifetime."
                )

        if errors:
            raise ValidationError(errors)

    @property
    def global_lease_settings(self):
        data = {}

        if self.valid_lifetime is not None:
            data["valid-lifetime"] = self.valid_lifetime
        if self.min_valid_lifetime is not None:
            data["min-valid-lifetime"] = self.min_valid_lifetime
        if self.max_valid_lifetime is not None:
            data["max-valid-lifetime"] = self.max_valid_lifetime

        return data
