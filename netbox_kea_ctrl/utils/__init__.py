from extras.models import CustomField


def get_prefix_custom_field(name: str):
    """
    Return a Prefix custom field by name if it exists, otherwise None.
    """
    try:
        return CustomField.objects.get(name=name, object_types__model="prefix")
    except CustomField.DoesNotExist:
        return None
