from dbay import DBayClient, dac4D
from dbay.direct import DeviceConnection
from typing import List


class FakeConnection(DeviceConnection):
    def __init__(self):
        super().__init__(mode="udp", host="127.0.0.1", port=0, timeout=0.1)
        self.sent: List[str] = []

    def send(self, cmd: str) -> str:  # type: ignore[override]
        # Do not open real sockets; just record
        self.sent.append(cmd)
        return "+ok"

    def close(self):  # type: ignore[override]
        self.sent.append("<closed>")


def test_injected_connection_used():
    fake = FakeConnection()
    client = DBayClient(mode="direct", connection=fake)
    mod = client.attach_module(0, dac4D)
    mod.set_voltage(0, 1.0)
    assert fake.sent, "Expected command to be sent via injected connection"
    assert any(cmd.startswith("DAC4D VS 0 0 1.0") for cmd in fake.sent)
