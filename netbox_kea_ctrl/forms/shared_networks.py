from django import forms
from netbox.forms import NetBoxModelForm

from netbox_kea_ctrl.models import KeaSharedNetwork


class KeaSharedNetworkForm(NetBoxModelForm):
    class Meta:
        model = KeaSharedNetwork
        fields = (
            "name",
            "description",
            "family",
            "server_tag",
            "publish_strategy",
            "ha_group",
            "manual_servers",
            "enabled",
            "option_data",
        )
        labels = {
            "server_tag": "Kea Server Tag",
            "ha_group": "Mapped HA Group",
            "manual_servers": "Manual Publish Targets",
        }
        help_texts = {
            "server_tag": "Logical Kea server-tag used in configuration.",
            "publish_strategy": "Choose whether publish targets come from an HA Group or manual server selection.",
            "ha_group": "Used when publish strategy is 'HA Group'.",
            "manual_servers": "Used when publish strategy is 'Manual Server Selection'.",
        }

    def clean(self):
        cleaned_data = super().clean()

        publish_strategy = cleaned_data.get("publish_strategy")
        ha_group = cleaned_data.get("ha_group")
        manual_servers = cleaned_data.get("manual_servers")
        server_tag = cleaned_data.get("server_tag")

        if publish_strategy == KeaSharedNetwork.PUBLISH_STRATEGY_HA_GROUP:
            if not ha_group:
                self.add_error("ha_group", "HA Group must be selected when publish strategy is 'HA Group'.")

        if publish_strategy == KeaSharedNetwork.PUBLISH_STRATEGY_MANUAL:
            if not manual_servers or manual_servers.count() == 0:
                self.add_error("manual_servers", "At least one Kea Server must be selected when publish strategy is 'Manual Server Selection'.")

        if ha_group and server_tag and server_tag.ha_group:
            if server_tag.ha_group_id != ha_group.id:
                self.add_error("server_tag", "Selected server tag belongs to a different HA Group.")
                self.add_error("ha_group", "Selected HA Group does not match the selected server tag.")

        return cleaned_data
