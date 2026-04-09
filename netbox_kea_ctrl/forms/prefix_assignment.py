from django import forms


class PrefixAssignForm(forms.Form):
    prefix_id = forms.ChoiceField(label="Prefix")

    def __init__(self, *args, prefix_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["prefix_id"].choices = prefix_choices or []
