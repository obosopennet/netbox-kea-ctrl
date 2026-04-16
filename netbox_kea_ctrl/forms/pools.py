from netbox.forms import NetBoxModelForm

from netbox_kea_ctrl.models import KeaPrefixPool
from netbox_kea_ctrl.utils.raw_config import parse_raw_config


class KeaPrefixPoolForm(NetBoxModelForm):
    class Meta:
        model = KeaPrefixPool
        fields = (
            "prefix",
            "start_address",
            "end_address",
            "description",
            "enabled",
            "raw_option_data",
        )
        labels = {
            "raw_option_data": "Advanced Raw Option Data",
        }
        help_texts = {
            "raw_option_data": "Optional advanced JSON/YAML for pool-specific Kea option structures.",
        }

    def clean_raw_option_data(self):
        raw = self.cleaned_data.get("raw_option_data", "")
        parse_raw_config(raw, "raw_option_data")
        return raw
