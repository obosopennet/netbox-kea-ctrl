import yaml


class OptionParser:
    def parse(self, raw: str) -> dict:
        if not raw:
            return {}

        parsed = yaml.safe_load(raw) or {}
        if not isinstance(parsed, dict):
            raise ValueError("Option data must be a mapping")
        return parsed

    def to_kea_option_data(self, raw: str) -> list[dict]:
        parsed = self.parse(raw)
        return [{"name": key, "data": value} for key, value in parsed.items()]
