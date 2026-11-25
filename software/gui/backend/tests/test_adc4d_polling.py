import pytest
from starlette.testclient import TestClient

from backend.initialize import global_state
from backend.main import app
from backend.modules.adc4D_spec import NUM_CHANNELS, adc4DController


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


@pytest.fixture
def adc4d_slot():
    """Initialize an adc4D module in slot 3 and return the slot index."""
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()  # snapshot
            send_command(websocket, "initialize_module", {"slot": 3, "type": "adc4D"})
    return 3


def test_adc4d_prototype_has_four_channels_and_polling(adc4d_slot):
    module = global_state.system_state.data[adc4d_slot]
    assert module.core.type == "adc4D"
    assert len(module.vsense.channels) == NUM_CHANNELS == 4
    assert module.polling.running is False
    assert module.polling.frequency > 0


def test_set_adc4d_polling_starts_and_stops(adc4d_slot):
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()  # snapshot

            ack = send_command(
                websocket,
                "set_adc4d_polling",
                {"module_index": adc4d_slot, "running": True, "frequency": 5.0},
                request_id="start-polling",
            )
            assert ack["result"]["running"] is True
            assert ack["result"]["frequency"] == 5.0

            module = global_state.system_state.data[adc4d_slot]
            assert module.polling.running is True
            assert module.polling.frequency == 5.0

            ack = send_command(
                websocket,
                "set_adc4d_polling",
                {"module_index": adc4d_slot, "running": False, "frequency": 5.0},
                request_id="stop-polling",
            )
            assert ack["result"]["running"] is False
            assert global_state.system_state.data[adc4d_slot].polling.running is False


def test_set_adc4d_polling_clamps_frequency(adc4d_slot):
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()

            ack = send_command(
                websocket,
                "set_adc4d_polling",
                {"module_index": adc4d_slot, "running": False, "frequency": 1000.0},
                request_id="clamp-test",
            )
            assert ack["result"]["frequency"] == 20.0


def test_set_adc4d_polling_rejects_non_adc_slot():
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()
            websocket.send_json(
                {
                    "type": "command",
                    "command": "set_adc4d_polling",
                    "requestId": "bad-slot",
                    "params": {"module_index": 7, "running": True, "frequency": 2.0},
                }
            )
            message = websocket.receive_json()

    assert message["type"] == "command_error"
    assert message["code"] == "invalid_module"


def test_set_adc4d_vsense_rejects_out_of_range_channel(adc4d_slot):
    with TestClient(app) as client:
        with client.websocket_connect("/sync/ws") as websocket:
            websocket.receive_json()
            websocket.send_json(
                {
                    "type": "command",
                    "command": "set_adc4d_vsense",
                    "requestId": "bad-channel",
                    "params": {
                        "module_index": adc4d_slot,
                        "index": 4,
                        "voltage": 0.0,
                        "measuring": True,
                        "name": "ch4",
                    },
                }
            )
            message = websocket.receive_json()

    assert message["type"] == "command_error"
    assert message["code"] == "invalid_channel_index"


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        (",0.093000\n", 0.093),
        (",-1.250000", -1.25),
        ("+ok\n", 0.0),
        ("+ok 0.5", 0.5),
        ("-board is not initialized, use SETDEV", 0.0),
        ("-0.25", -0.25),
        ("0.125", 0.125),
    ],
)
def test_parse_voltage_formats(response, expected):
    assert adc4DController._parse_voltage(response) == pytest.approx(expected)
