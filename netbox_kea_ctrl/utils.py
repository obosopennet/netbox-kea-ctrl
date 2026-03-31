def get_prefix_custom_field(prefix, name, default=None):
    value = (getattr(prefix, "custom_field_data", None) or {}).get(name, default)
    if isinstance(value, str):
        value = value.strip()
    return value
