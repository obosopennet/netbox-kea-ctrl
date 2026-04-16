import json
from django.core.exceptions import ValidationError
import yaml


def parse_raw_config(raw_value: str, field_name: str = "raw_option_data"):
    """
    Parse user-supplied JSON or YAML.

    Accepts:
    - empty string / None -> returns None
    - valid JSON
    - valid YAML

    Raises:
    - ValidationError on syntax errors
    """
    if raw_value is None:
        return None

    raw_value = raw_value.strip()
    if not raw_value:
        return None

    # Try JSON first if it looks like JSON
    if raw_value.startswith("{") or raw_value.startswith("["):
        try:
            return json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise ValidationError({
                field_name: f"Invalid JSON syntax: {exc.msg} (line {exc.lineno}, column {exc.colno})"
            })

    # Fall back to YAML
    try:
        return yaml.safe_load(raw_value)
    except yaml.YAMLError as exc:
        raise ValidationError({
            field_name: f"Invalid YAML syntax: {exc}"
        })
