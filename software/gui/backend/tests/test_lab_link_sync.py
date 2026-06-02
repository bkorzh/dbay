from fastapi.testclient import TestClient

from backend.main import app


def test_sync_state_matches_full_state():
    with TestClient(app) as client:
        full_state = client.get("/full-state").json()
        sync_state = client.get("/sync/state").json()

    assert sync_state == full_state


def test_sync_websocket_sends_initial_snapshot():
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            message = websocket.receive_json()
        sync_state = client.get("/sync/state").json()

    assert message["type"] == "snapshot"
    assert message["data"] == sync_state
    assert isinstance(message["version"], int)


def test_rest_update_broadcasts_sync_patch():
    with TestClient(app) as client:
        initial_state = client.get("/sync/state").json()
        next_dev_mode = not initial_state["dev_mode"]

        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()

            response = client.post(
                "/initialize-vsource",
                json={
                    "ipaddr": "127.0.0.1",
                    "timeout": 1.0,
                    "port": 9,
                    "dev_mode": next_dev_mode,
                },
            )
            patch_message = websocket.receive_json()

    assert response.status_code == 200
    assert patch_message["type"] == "patch"
    assert patch_message["patch"] == [
        {"op": "replace", "path": "/dev_mode", "value": next_dev_mode}
    ]


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
