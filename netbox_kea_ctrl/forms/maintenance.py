from django import forms


class MaintenanceActionForm(forms.Form):
    reason = forms.CharField(required=False)
