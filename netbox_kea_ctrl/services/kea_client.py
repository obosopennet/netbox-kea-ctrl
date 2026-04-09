import json
import ssl
from urllib import request, error


class KeaAPIError(Exception):
    pass


class KeaClient:
    def __init__(self, base_url: str, timeout: int = 5, verify_tls: bool = True):
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.verify_tls = verify_tls

    def _build_ssl_context(self):
        if self.verify_tls:
            return None
        return ssl._create_unverified_context()

    def call(self, command: str, service: str | None = None, arguments: dict | None = None):
        payload: dict = {"command": command}
        if arguments:
            payload["arguments"] = arguments
        if service:
            payload["service"] = [service]

        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.base_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(
                req,
                timeout=self.timeout,
                context=self._build_ssl_context(),
            ) as resp:
                raw = resp.read().decode("utf-8")
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise KeaAPIError(f"HTTP {exc.code}: {body}") from exc
        except Exception as exc:
            raise KeaAPIError(str(exc)) from exc

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise KeaAPIError(f"Invalid JSON response: {raw}") from exc

        return parsed

    def status_get(self, service: str):
        return self.call("status-get", service=service)

    def server_tag_get(self, service: str):
        return self.call("server-tag-get", service=service)

    def config_get(self, service: str):
        return self.call("config-get", service=service)

    def list_commands(self, service: str):
        return self.call("list-commands", service=service)
    def call_raw(self, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.base_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(
                req,
                timeout=self.timeout,
                context=self._build_ssl_context(),
            ) as resp:
                raw = resp.read().decode("utf-8")
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise KeaAPIError(f"HTTP {exc.code}: {body}") from exc
        except Exception as exc:
            raise KeaAPIError(str(exc)) from exc

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise KeaAPIError(f"Invalid JSON response: {raw}") from exc

        return parsed
