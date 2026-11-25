from __future__ import annotations

from typing import Any, Callable
from urllib.parse import urlsplit, urlunsplit

from lab_link import LabLinkClient, PatchEvent, SnapshotEvent

Unsubscribe = Callable[[], None]


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

    @property
    def version(self) -> int:
        """Version of the state the client currently holds.

        Bumped by the server on every applied patch, so a consumer can cache
        derived views and recompute only when this changes, and can detect a
        dropped update by comparing against the version it last saw.
        """
        return self._client.version

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

    def on_patch(self, callback: Callable[[PatchEvent], Any]) -> Unsubscribe:
        """Register ``callback`` for every state patch the server broadcasts.

        The client applies each patch to its own snapshot before the callback
        runs, so ``snapshot()`` is already current when the callback fires and
        consumers never apply patch operations themselves.

        ``PatchEvent.origin_client_id`` identifies the client whose command
        produced the change, so a consumer can ignore echoes of its own writes.
        Returns a callable that unregisters the callback.
        """
        return self._client.on_patch(callback)

    def on_snapshot(self, callback: Callable[[SnapshotEvent], Any]) -> Unsubscribe:
        """Register ``callback`` for full-state snapshots.

        Fired on the initial sync and on any resync, so a consumer can rebuild
        derived state that a patch stream alone would leave stale.
        Returns a callable that unregisters the callback.
        """
        return self._client.on_snapshot(callback)

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
