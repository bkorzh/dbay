from starlette.testclient import TestClient

from backend.initialize import global_state
from backend.main import app


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


def test_sync_websocket_sends_current_state_snapshot():
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            message = websocket.receive_json()

    assert message["type"] == "snapshot"
    assert message["data"] == global_state.system_state.model_dump(mode="json")
    assert isinstance(message["version"], int)


def test_rest_state_routes_are_removed():
    with TestClient(app) as client:
        assert client.get("/full-state").status_code == 404
        assert client.put("/full-state", json={}).status_code == 404
        assert client.get("/sync/state").status_code == 404
        assert client.post("/initialize-module", json={}).status_code == 404
        assert client.post("/initialize-vsource", json={}).status_code == 404
        assert client.get("/server-info").status_code == 404


def test_initialize_vsource_command_broadcasts_sync_patch():
    with TestClient(app) as client:
        initial_state = global_state.system_state.model_dump(mode="json")
        next_dev_mode = not initial_state["dev_mode"]

        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()
            websocket.send_json(
                {
                    "type": "command",
                    "command": "initialize_vsource",
                    "requestId": "initialize-vsource-test",
                    "params": {
                        "ipaddr": "127.0.0.1",
                        "timeout": 1.0,
                        "port": 9,
                        "dev_mode": next_dev_mode,
                    },
                }
            )
            messages = [websocket.receive_json(), websocket.receive_json()]

    patch_message = next(message for message in messages if message["type"] == "patch")
    ack_message = next(message for message in messages if message["type"] == "command_ack")

    assert patch_message["type"] == "patch"
    assert patch_message["patch"] == [
        {"op": "replace", "path": "/dev_mode", "value": next_dev_mode}
    ]
    assert ack_message["requestId"] == "initialize-vsource-test"


def test_sync_command_error_for_invalid_module():
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()
            websocket.send_json(
                {
                    "type": "command",
                    "command": "set_dac4d_vsource",
                    "requestId": "invalid-module-test",
                    "params": {
                        "module_index": 999,
                        "index": 0,
                        "bias_voltage": 1.0,
                        "activated": True,
                        "heading_text": "test",
                        "measuring": False,
                    },
                }
            )
            message = websocket.receive_json()

    assert message["type"] == "command_error"
    assert message["requestId"] == "invalid-module-test"
    assert message["code"] == "invalid_module"
    assert message["display"] == "toast"
