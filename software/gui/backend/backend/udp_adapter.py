"""Adapter to make backend's UDP class compatible with device-bay-client's IConnection interface."""

from __future__ import annotations
from typing import TYPE_CHECKING

from dbay.direct import IConnection

if TYPE_CHECKING:
    from backend.udp_control import ParentUDP


class UDPAdapter(IConnection):
    """Wraps the backend's ParentUDP to match the IConnection protocol.

    This allows the backend to use device-bay-client modules in direct mode
    while still using the existing UDP infrastructure with its retry logic.

    By holding a reference to ParentUDP (not the inner UDP), this adapter
    correctly uses the current UDP instance even after dynamic replacement
    via /initialize-vsource.
    """

    def __init__(self, parent_udp: "ParentUDP"):
        self._parent = parent_udp

    def send(self, message: str) -> str:
        """Send a command and return the response.

        The backend's UDP.send_message() expects messages to end with newline,
        while IConnection.send() adds the newline internally. We handle both cases.
        """
        msg = message.strip() + "\n"
        return self._parent.udp.send_message(msg)

    def close(self) -> None:
        """No-op: UDP lifecycle is managed by ParentUDP."""
        pass

    def __enter__(self) -> "UDPAdapter":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass
