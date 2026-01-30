"""Integration test for dynamic UDP switching.

Tests that:
1. Modules send UDP commands to the initially configured address
2. After /initialize-vsource switches the UDP target, commands go to the new address
3. The UDPAdapter correctly follows ParentUDP's inner UDP replacement
"""

import pytest
import socket
import time
from fastapi.testclient import TestClient

from tests.mock_udp_server import MockUDPServer


# We need to patch vsource_params.json before importing main,
# so the initial UDP target points to our first mock server.
@pytest.fixture
def mock_servers():
    """Create two mock UDP servers to test switching between them."""
    server1 = MockUDPServer(host="127.0.0.1")
    server2 = MockUDPServer(host="127.0.0.1")

    with server1, server2:
        yield server1, server2


@pytest.fixture
def configured_app(mock_servers, tmp_path, monkeypatch):
    """Configure the app to use our first mock server initially."""
    server1, server2 = mock_servers

    # Create a temporary vsource_params.json pointing to server1
    import json

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    params_file = config_dir / "vsource_params.json"
    params_file.write_text(
        json.dumps(
            {
                "ipaddr": "127.0.0.1",
                "port": server1.port,
                "dev_mode": False,  # Real UDP mode so we actually send packets
            }
        )
    )

    # Also create a minimal state.json
    state_file = config_dir / "state.json"
    state_file.write_text(json.dumps({"data": [None] * 8, "dev_mode": False}))

    # Patch DATA_DIR before importing backend modules
    monkeypatch.setenv("DBAY_DATA_DIR", str(config_dir))

    # Now we need to reload the modules that read from DATA_DIR at import time
    # This is tricky - we may need to structure the test differently
    # For now, let's use a simpler approach: directly manipulate parent_udp after import

    from backend.main import app
    from backend.udp_control import parent_udp, UDP

    # Override the UDP instance to point to server1
    parent_udp.udp = UDP("127.0.0.1", server1.port, dev_mode=False)

    client = TestClient(app)
    yield client, server1, server2, parent_udp


class TestDynamicUDPSwitch:
    """Test suite for dynamic UDP target switching."""

    def test_initial_module_commands_go_to_server1(self, configured_app):
        """After adding a module, UDP commands should go to the initial server."""
        client, server1, server2, parent_udp = configured_app

        # Add a dac4D module to slot 0
        response = client.post("/initialize-module", json={"slot": 0, "type": "dac4D"})
        assert response.status_code == 200

        # Give the server a moment to receive
        time.sleep(0.1)

        # Server1 should have received the SETDEV command
        assert len(server1.messages) > 0, "Server1 should have received commands"
        assert any(
            "SETDEV" in msg for msg in server1.messages
        ), f"Expected SETDEV command, got: {server1.messages}"

        # Server2 should have received nothing
        assert (
            len(server2.messages) == 0
        ), "Server2 should not have received anything yet"

    def test_switch_udp_target(self, configured_app):
        """After /initialize-vsource, commands should go to the new server."""
        client, server1, server2, parent_udp = configured_app

        # First, initialize a module (goes to server1)
        client.post("/initialize-module", json={"slot": 0, "type": "dac4D"})
        time.sleep(0.1)

        initial_server1_count = len(server1.messages)

        # Now switch to server2
        response = client.post(
            "/initialize-vsource",
            json={
                "ipaddr": "127.0.0.1",
                "port": server2.port,
                "timeout": 1.0,
                "dev_mode": False,
            },
        )
        assert response.status_code == 200

        # Clear server messages to start fresh
        server1.clear()
        server2.clear()

        # Add another module - should go to server2 now
        response = client.post("/initialize-module", json={"slot": 1, "type": "dac4D"})
        assert response.status_code == 200

        time.sleep(0.1)

        # Server2 should now have the new commands
        assert (
            len(server2.messages) > 0
        ), f"Server2 should have received commands after switch. Server1 has: {server1.messages}"
        assert any(
            "SETDEV" in msg for msg in server2.messages
        ), f"Expected SETDEV command on server2, got: {server2.messages}"

        # Server1 should NOT have received the new commands
        assert (
            len(server1.messages) == 0
        ), f"Server1 should not receive commands after switch, got: {server1.messages}"

    def test_voltage_command_after_switch(self, configured_app):
        """Voltage commands should also follow the UDP switch."""
        client, server1, server2, parent_udp = configured_app

        # Initialize module on server1
        client.post("/initialize-module", json={"slot": 0, "type": "dac4D"})
        time.sleep(0.1)

        # Switch to server2
        client.post(
            "/initialize-vsource",
            json={
                "ipaddr": "127.0.0.1",
                "port": server2.port,
                "timeout": 1.0,
                "dev_mode": False,
            },
        )

        server2.clear()

        # Send a voltage command - should go to server2
        response = client.put(
            "/dac4D/vsource/",
            json={
                "module_index": 0,
                "index": 0,
                "bias_voltage": 1.5,
                "activated": True,
                "heading_text": "Test",
                "measuring": False,
            },
        )
        assert response.status_code == 200

        time.sleep(0.1)

        # Check server2 received the voltage command
        assert len(server2.messages) > 0, "Server2 should have received voltage command"
        # The command format is "DAC4D VSD <slot> <channel> <voltage>"
        assert any(
            "VSD" in msg or "DAC4D" in msg for msg in server2.messages
        ), f"Expected voltage command, got: {server2.messages}"


class TestMockUDPServer:
    """Basic tests for the mock server itself."""

    def test_mock_server_receives_and_responds(self):
        """Verify the mock server works correctly."""
        with MockUDPServer() as server:
            # Send a test message
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1.0)

            sock.sendto(b"TEST MESSAGE\n", ("127.0.0.1", server.port))
            response, _ = sock.recvfrom(4096)

            sock.close()

            assert response.decode() == "+ok\n"
            assert "TEST MESSAGE" in server.messages


# Allow running with: python -m pytest tests/test_dynamic_udp_switch.py -v
if __name__ == "__main__":
    import socket  # needed for TestMockUDPServer

    pytest.main([__file__, "-v"])
