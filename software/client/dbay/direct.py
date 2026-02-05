from __future__ import annotations

from dataclasses import dataclass
import socket
from typing import Optional, Protocol, runtime_checkable

__all__ = [
    "DirectDeviceError",
    "DeviceConnection",
    "IConnection",
]


class DirectDeviceError(Exception):
    """Raised when the direct transport fails or returns an unexpected response."""


@runtime_checkable
class IConnection(Protocol):
    """Protocol defining the interface for device connections.

    Any class implementing send(), close(), and context manager methods
    can be used as a connection. This allows dependency injection of
    custom transports (e.g., the backend's UDPAdapter).
    """

    def send(self, message: str) -> str:
        """Send a command and return the response."""
        ...

    def close(self) -> None:
        """Clean up resources."""
        ...

    def __enter__(self) -> "IConnection": ...

    def __exit__(self, exc_type, exc, tb) -> None: ...


@dataclass
class DeviceConnection:
    """A thin transport wrapper for UDP or Serial ASCII command exchange.

    Parameters
    ----------
    mode: "udp" | "serial"
        Transport selection. Serial import is lazy so users who only use UDP do
        not need the `pyserial` dependency.
    host, port: Used for UDP mode.
    serial_port, baudrate, timeout: Used for serial mode.
    """

    mode: str = "udp"
    host: str = "127.0.0.1"
    port: int = 8880
    serial_port: Optional[str] = None
    baudrate: int = 115200
    timeout: float = 1.0

    def __post_init__(self):
        if self.mode not in {"udp", "serial"}:
            raise ValueError("DeviceConnection.mode must be 'udp' or 'serial'")
        self._ser = None
        if self.mode == "serial":
            if not self.serial_port:
                raise ValueError("serial_port must be specified for serial mode")
            try:
                import serial  # type: ignore
            except ImportError as exc:  # pragma: no cover - import guard
                raise ImportError(
                    "pyserial is required for serial direct mode: pip install pyserial"
                ) from exc
            self._ser = serial.Serial(
                self.serial_port, baudrate=self.baudrate, timeout=self.timeout
            )

    # Public API -----------------------------------------------------
    def send(self, message: str) -> str:
        """Send a single-line command and return the raw response string.

        Always appends a newline, strips trailing whitespace from the response.
        Raises DirectDeviceError on timeout.
        """

        msg = message.strip() + "\n"
        if self.mode == "udp":
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(self.timeout)
                sock.sendto(msg.encode(), (self.host, self.port))
                try:
                    data, _ = sock.recvfrom(4096)
                except socket.timeout as exc:
                    raise DirectDeviceError(
                        "Timeout waiting for device response"
                    ) from exc
            return data.decode().strip()
        else:  # serial
            assert self._ser is not None
            self._ser.write(msg.encode())
            resp = self._ser.readline().decode().strip()
            return resp

    # Context manager convenience (optional) ------------------------
    def close(self):  # pragma: no cover - lightweight
        if self._ser is not None:
            try:
                self._ser.close()
            except Exception:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
