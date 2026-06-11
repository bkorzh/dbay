from dbay import DBayClient, dac4D


def minimal_dac4d_state(slot: int = 0):
    return {
        "core": {"slot": slot, "type": "dac4D", "name": "dac4D"},
        "vsource": {"channels": [
            {"index": i, "bias_voltage": 0.0, "activated": False, "heading_text": f"CH{i}", "measuring": False}
            for i in range(4)
        ]},
    }


class FakeSync:
    def __init__(self):
        self.calls = []
        self.state = {"data": [minimal_dac4d_state(0)]}

    def snapshot(self):
        return self.state

    def module_data(self, slot: int):
        return self.state["data"][slot]

    def send_command(self, command: str, params: dict):
        self.calls.append((command, params))
        if command == "set_dac4d_vsource":
            channel = self.state["data"][params["module_index"]]["vsource"]["channels"][params["index"]]
            channel.update(
                {
                    "bias_voltage": params["bias_voltage"],
                    "activated": params["activated"],
                    "heading_text": params["heading_text"],
                    "measuring": params["measuring"],
                }
            )
        return params


def test_gui_module_set_voltage_uses_sync_command():
    sync = FakeSync()
    mod = dac4D(sync.module_data(0), sync=sync, mode="gui")
    mod.set_voltage(0, 1.25, activated=True)
    assert sync.calls, "Expected at least one sync command"
    command, payload = sync.calls[-1]
    assert command == "set_dac4d_vsource"
    assert payload["bias_voltage"] == 1.25
    assert mod.data.vsource.channels[0].bias_voltage == 1.25


def test_gui_client_loads_state_from_sync(monkeypatch):
    fake_sync = FakeSync()

    class FakeGuiSync:
        def __init__(self, *args, **kwargs):
            pass

        def connect(self):
            return self

        def close(self):
            pass

        def snapshot(self):
            return fake_sync.snapshot()

        def module_data(self, slot: int):
            return fake_sync.module_data(slot)

        def send_command(self, command: str, params: dict):
            return fake_sync.send_command(command, params)

    monkeypatch.setattr("dbay.client.GuiSync", FakeGuiSync)
    client = DBayClient(mode="gui", server_address="127.0.0.1")
    mod = client.module(0, expected="dac4D")
    assert mod is not None
    mod.set_voltage(0, 2.0, activated=True)
    assert fake_sync.calls[-1][0] == "set_dac4d_vsource"
