from django import forms


class MaintenanceActionForm(forms.Form):
    target = forms.ChoiceField(
        choices=(
            ("primary", "Primary"),
            ("secondary", "Secondary"),
        )
    )
