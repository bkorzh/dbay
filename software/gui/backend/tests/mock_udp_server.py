"""Mock UDP server for testing dynamic UDP switching.

Listens on a specified port and records all received messages.
Responds with '+ok\n' to simulate the real device.
"""

import socket
import threading
from typing import List
from dataclasses import dataclass, field


@dataclass
class MockUDPServer:
    """A simple UDP server that records received messages for test assertions."""

    host: str = "127.0.0.1"
    port: int = 0  # 0 = let OS assign an available port
    response: str = "+ok\n"

    # Recorded messages
    messages: List[str] = field(default_factory=list)

    _socket: socket.socket = field(default=None, repr=False)
    _thread: threading.Thread = field(default=None, repr=False)
    _running: bool = field(default=False, repr=False)

    def __post_init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.host, self.port))
        # Update port if it was auto-assigned
        self.port = self._socket.getsockname()[1]
        self._socket.settimeout(0.5)  # Allow periodic checking of _running flag

    def start(self):
        """Start listening in a background thread."""
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        return self

    def stop(self):
        """Stop the server and clean up."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._socket:
            self._socket.close()

    def _listen_loop(self):
        """Background thread that receives messages."""
        while self._running:
            try:
                data, addr = self._socket.recvfrom(4096)
                message = data.decode().strip()
                self.messages.append(message)
                # Send response back to sender
                self._socket.sendto(self.response.encode(), addr)
            except socket.timeout:
                continue
            except OSError:
                # Socket was closed
                break

    def clear(self):
        """Clear recorded messages."""
        self.messages.clear()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc, tb):
        self.stop()
