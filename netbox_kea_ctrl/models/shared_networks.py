from django.core.exceptions import ValidationError
from django.db import models
from netbox.models import NetBoxModel

from netbox_kea_ctrl.choices import FAMILY_CHOICES, FAMILY_IPV4


class KeaSharedNetwork(NetBoxModel):
    PUBLISH_STRATEGY_HA_GROUP = "ha_group"
    PUBLISH_STRATEGY_MANUAL = "manual"

    PUBLISH_STRATEGY_CHOICES = (
        (PUBLISH_STRATEGY_HA_GROUP, "HA Group"),
        (PUBLISH_STRATEGY_MANUAL, "Manual Server Selection"),
    )

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    family = models.CharField(max_length=10, choices=FAMILY_CHOICES, default=FAMILY_IPV4)
    enabled = models.BooleanField(default=True)

    server_tag = models.ForeignKey(
        to="netbox_kea_ctrl.KeaServerTag",
        on_delete=models.PROTECT,
        related_name="shared_networks",
    )

    publish_strategy = models.CharField(
        max_length=20,
        choices=PUBLISH_STRATEGY_CHOICES,
        default=PUBLISH_STRATEGY_HA_GROUP,
    )

    ha_group = models.ForeignKey(
        to="netbox_kea_ctrl.KeaHAGroup",
        on_delete=models.PROTECT,
        related_name="shared_networks",
        null=True,
        blank=True,
    )

    manual_servers = models.ManyToManyField(
        to="netbox_kea_ctrl.KeaServer",
        related_name="manual_shared_networks",
        blank=True,
    )

    option_data = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        errors = {}

        if self.publish_strategy == self.PUBLISH_STRATEGY_HA_GROUP:
            if not self.ha_group:
                errors["ha_group"] = "HA Group must be set when publish strategy is 'HA Group'."

        if self.publish_strategy == self.PUBLISH_STRATEGY_MANUAL:
            # ManyToMany can't reliably be validated on unsaved instance here,
            # so form validation should also handle this.
            pass

        if self.ha_group and self.server_tag and self.server_tag.ha_group:
            if self.server_tag.ha_group_id != self.ha_group_id:
                errors["server_tag"] = "Selected server tag belongs to a different HA Group."
                errors["ha_group"] = "Selected HA Group does not match the selected server tag."

        if errors:
            raise ValidationError(errors)

    def get_publish_targets(self):
        if self.publish_strategy == self.PUBLISH_STRATEGY_HA_GROUP and self.ha_group:
            return self.ha_group.servers.filter(enabled=True).order_by("name")

        if self.publish_strategy == self.PUBLISH_STRATEGY_MANUAL:
            return self.manual_servers.filter(enabled=True).order_by("name")

        return self.manual_servers.none()

    @property
    def publish_targets_display(self):
        targets = self.get_publish_targets()
        if not targets.exists():
            return "-"
        return ", ".join(server.name for server in targets)

    @property
    def publish_target_count(self):
        return self.get_publish_targets().count()
