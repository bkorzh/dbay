from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit, urlunsplit

from lab_link import LabLinkClient


class GuiSync:
    """Thin dbay-facing wrapper around the generic lab-link client."""

    def __init__(
        self,
        server_address: str,
        port: int = 8345,
        *,
        path: str = "/sync/ws",
        command_timeout: float = 10.0,
        connect_timeout: float = 10.0,
    ) -> None:
        self.url = _sync_ws_url(server_address, port, path)
        self._client = LabLinkClient(
            self.url,
            command_timeout=command_timeout,
            connect_timeout=connect_timeout,
        )

    @property
    def connected(self) -> bool:
        return self._client.connected

    def connect(self) -> GuiSync:
        self._client.connect()
        return self

    def close(self) -> None:
        self._client.close()

    def snapshot(self) -> dict[str, Any]:
        snapshot = self._client.snapshot()
        return snapshot or {}

    def module_data(self, slot: int) -> dict[str, Any]:
        modules = self.snapshot().get("data", [])
        if not isinstance(modules, list) or not (0 <= slot < len(modules)):
            raise IndexError(f"No module state for slot {slot}")
        module = modules[slot]
        if not isinstance(module, dict):
            raise TypeError(f"Module state for slot {slot} is not an object")
        return module

    def send_command(self, command: str, params: dict[str, Any]) -> Any:
        ack = self._client.send_command(command, params)
        return ack.result


def _sync_ws_url(server_address: str, port: int, path: str) -> str:
    path = path if path.startswith("/") else f"/{path}"
    address = server_address.rstrip("/")

    if address.startswith(("ws://", "wss://", "http://", "https://")):
        parsed = urlsplit(address)
        scheme = {"http": "ws", "https": "wss"}.get(parsed.scheme, parsed.scheme)
        netloc = parsed.netloc if ":" in parsed.netloc else f"{parsed.netloc}:{port}"
        ws_path = parsed.path if parsed.path and parsed.path != "/" else path
        return urlunsplit((scheme, netloc, ws_path, "", ""))

    host = address if ":" in address else f"{address}:{port}"
    return f"ws://{host}{path}"
