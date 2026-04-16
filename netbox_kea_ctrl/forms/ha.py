from netbox.forms import NetBoxModelForm

from netbox_kea_ctrl.models import KeaHAGroup


class KeaHAGroupForm(NetBoxModelForm):
    class Meta:
        model = KeaHAGroup
        fields = (
            "name",
            "description",
            "mode",
            "enabled",
            "primary_server",
            "secondary_server",
            "valid_lifetime",
            "min_valid_lifetime",
            "max_valid_lifetime",
        )
        labels = {
            "valid_lifetime": "Valid Lifetime",
            "min_valid_lifetime": "Minimum Valid Lifetime",
            "max_valid_lifetime": "Maximum Valid Lifetime",
        }
        help_texts = {
            "valid_lifetime": (
                "Global valid-lifetime for this HA Group unless overridden "
                "at shared network, prefix, or pool level."
            ),
            "min_valid_lifetime": "Optional lower bound for valid-lifetime.",
            "max_valid_lifetime": "Optional upper bound for valid-lifetime.",
        }

    def clean(self):
        super().clean()
        cleaned_data = self.cleaned_data

        valid_lifetime = cleaned_data.get("valid_lifetime")
        min_valid_lifetime = cleaned_data.get("min_valid_lifetime")
        max_valid_lifetime = cleaned_data.get("max_valid_lifetime")
        primary_server = cleaned_data.get("primary_server")
        secondary_server = cleaned_data.get("secondary_server")

        if primary_server and secondary_server and primary_server == secondary_server:
            self.add_error("secondary_server", "Primary and secondary server must be different.")

        if min_valid_lifetime is not None and max_valid_lifetime is not None:
            if min_valid_lifetime > max_valid_lifetime:
                self.add_error("min_valid_lifetime", "Minimum cannot be greater than maximum.")
                self.add_error("max_valid_lifetime", "Maximum cannot be less than minimum.")

        if valid_lifetime is not None and min_valid_lifetime is not None:
            if valid_lifetime < min_valid_lifetime:
                self.add_error(
                    "valid_lifetime",
                    "Valid lifetime cannot be less than minimum valid lifetime.",
                )

        if valid_lifetime is not None and max_valid_lifetime is not None:
            if valid_lifetime > max_valid_lifetime:
                self.add_error(
                    "valid_lifetime",
                    "Valid lifetime cannot be greater than maximum valid lifetime.",
                )

        return cleaned_data
