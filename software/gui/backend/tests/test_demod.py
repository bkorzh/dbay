"""Tests for the demoD tutorial module.

demoD is the worked example in `docs/content/Development/Adding a Module.md`.
These tests exist so that the guide cannot quietly stop being true: they cover
each step the guide claims works — registering the type, the vsource command,
the trim command, validation, and the patch that reaches connected clients.
"""

import pytest
from starlette.testclient import TestClient

from backend.initialize import global_state
from backend.main import app
from backend.modules.demoD_controller import TRIM_MAX, TRIM_MIN, DemoDState


SLOT = 4


def send_command(websocket, command: str, params: dict, request_id: str = "test"):
    websocket.send_json(
        {
            "type": "command",
            "command": command,
            "requestId": request_id,
            "params": params,
        }
    )

    while True:
        message = websocket.receive_json()
        if message["type"] == "command_ack" and message["requestId"] == request_id:
            return message
        if message["type"] == "command_error" and message["requestId"] == request_id:
            raise AssertionError(message)


def send_command_expecting_error(websocket, command: str, params: dict, request_id="err"):
    websocket.send_json(
        {
            "type": "command",
            "command": command,
            "requestId": request_id,
            "params": params,
        }
    )

    while True:
        message = websocket.receive_json()
        if message["type"] == "command_error" and message["requestId"] == request_id:
            return message
        if message["type"] == "command_ack" and message["requestId"] == request_id:
            raise AssertionError(f"expected a command error, got: {message}")


@pytest.fixture
def demod_slot():
    """A demoD in slot 4, as the module adder would create it."""
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()  # snapshot
            send_command(websocket, "initialize_module", {"slot": SLOT, "type": "demoD"})
    return SLOT


def test_registry_creates_a_demod_prototype(demod_slot):
    module = global_state.system_state.data[demod_slot]

    assert isinstance(module, DemoDState)
    assert module.core.type == "demoD"
    assert module.module_type == "demoD"
    assert len(module.vsource.channels) == 1
    assert module.trim_voltage == 0.0


def test_set_demod_vsource_updates_shared_state(demod_slot):
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()  # snapshot
            ack = send_command(
                websocket,
                "set_demod_vsource",
                {
                    "module_index": demod_slot,
                    "index": 0,
                    "bias_voltage": 1.25,
                    "activated": True,
                    "heading_text": "detector A",
                    "measuring": False,
                },
            )

    assert ack["result"]["bias_voltage"] == 1.25

    channel = global_state.system_state.data[demod_slot].vsource.channels[0]
    assert channel.bias_voltage == 1.25
    assert channel.activated is True
    assert channel.heading_text == "detector A"


def test_set_demod_trim_updates_shared_state(demod_slot):
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()  # snapshot
            ack = send_command(
                websocket,
                "set_demod_trim",
                {"module_index": demod_slot, "voltage": 0.42},
            )

    assert ack["result"]["voltage"] == 0.42
    assert global_state.system_state.data[demod_slot].trim_voltage == 0.42


def test_trim_change_is_broadcast_as_a_patch(demod_slot):
    """The mutation in the handler is what updates other clients."""
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()  # snapshot
            websocket.send_json(
                {
                    "type": "command",
                    "command": "set_demod_trim",
                    "requestId": "patch",
                    "params": {"module_index": demod_slot, "voltage": -0.5},
                }
            )

            patches = []
            for _ in range(6):
                message = websocket.receive_json()
                if message["type"] == "patch":
                    patches.append(message)
                if message["type"] == "command_ack" and patches:
                    break

    operations = [op for patch in patches for op in patch["patch"]]
    assert any(
        op["path"] == f"/data/{demod_slot}/trim_voltage" and op["value"] == -0.5
        for op in operations
    ), operations


@pytest.mark.parametrize("voltage", [TRIM_MIN - 0.1, TRIM_MAX + 0.1])
def test_trim_outside_range_is_rejected(demod_slot, voltage):
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()  # snapshot
            error = send_command_expecting_error(
                websocket,
                "set_demod_trim",
                {"module_index": demod_slot, "voltage": voltage},
            )

    assert error["code"] == "trim_out_of_range"
    # The error names the field it came from, so the UI can show it inline.
    assert error["path"] == f"/data/{demod_slot}/trim_voltage"
    assert error["display"] == "inline"
    # A rejected command must not have changed the state.
    assert global_state.system_state.data[demod_slot].trim_voltage == 0.0


def test_trim_command_on_a_non_demod_slot_is_rejected():
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()  # snapshot
            send_command(websocket, "initialize_module", {"slot": 5, "type": "dac4D"})
            error = send_command_expecting_error(
                websocket,
                "set_demod_trim",
                {"module_index": 5, "voltage": 0.1},
            )

    assert error["code"] == "invalid_module"
