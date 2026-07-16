import socket

from dbay_sim import SimServer, VirtualDBay


def test_setdev_and_adc_read():
    dev = VirtualDBay(seed=1)
    assert dev.handle("SETDEV 2 ADC4D") == "+ok\n"
    response = dev.handle("ADC4D VRD 2 0")
    assert response.startswith(",")
    voltage = float(response[1:])
    assert -5.0 <= voltage <= 5.0


def test_adc_readings_vary():
    dev = VirtualDBay(seed=1)
    dev.handle("SETDEV 0 ADC4D")
    readings = {dev.handle("ADC4D VRD 0 1") for _ in range(5)}
    assert len(readings) > 1


def test_uninitialized_board_errors():
    dev = VirtualDBay()
    assert dev.handle("ADC4D VRD 0 0").startswith("-")


def test_wrong_device_type_errors():
    dev = VirtualDBay()
    dev.handle("SETDEV 0 DAC4D")
    assert dev.handle("ADC4D VRD 0 0") == "-use SETDEV with the proper board type\n"


def test_dac4d_set_voltage():
    dev = VirtualDBay()
    dev.handle("SETDEV 1 DAC4D")
    assert dev.handle("DAC4D VSD 1 3 -2.5") == "+ok\n"
    assert dev.modules[1].voltages[3] == -2.5
    assert dev.handle("DAC4D VSD 1 4 0.0").startswith("-")  # VSD channel range 0..3
    assert dev.handle("DAC4D VS 1 7 1.0") == "+ok\n"        # VS channel range 0..7


def test_dac16d_commands():
    dev = VirtualDBay(seed=3)
    dev.handle("SETDEV 4 DAC16D")
    assert dev.handle("DAC16D VS 4 31 0.25") == "+ok\n"
    assert dev.handle("DAC16D VSB 4 1.5") == "+ok\n"
    assert dev.handle("DAC16D VR 4").startswith(",")


def test_invalid_channel_and_voltage():
    dev = VirtualDBay()
    dev.handle("SETDEV 0 ADC4D")
    assert dev.handle("ADC4D VRD 0 5").startswith("-")
    assert dev.handle("ADC4D VRD 0 x").startswith("-")
    dev.handle("SETDEV 1 DAC4D")
    assert dev.handle("DAC4D VSD 1 0 abc").startswith("-")


def test_reset_clears_modules():
    dev = VirtualDBay()
    dev.handle("SETDEV 0 ADC4D")
    assert dev.handle("reset") == "+ok\n"
    assert dev.handle("ADC4D VRD 0 0").startswith("-")


def test_misc_commands():
    dev = VirtualDBay()
    assert dev.handle("debug on") == "+ok\n"
    assert dev.handle("help").startswith("-Available commands")
    assert dev.handle("bogus").startswith("-Unknown command")
    assert dev.handle("SETDEV 0 NOPE") == "-wrong devtype\n"
    assert dev.handle("SETDEV 9 ADC4D").startswith("-Invalid board number")


def test_udp_roundtrip():
    with SimServer(host="127.0.0.1", port=0, seed=7) as server:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(2.0)

            def send(message: str) -> str:
                sock.sendto((message + "\n").encode(), ("127.0.0.1", server.port))
                data, _ = sock.recvfrom(4096)
                return data.decode()

            assert send("SETDEV 3 ADC4D") == "+ok\n"
            reply = send("ADC4D VRD 3 2")
            assert reply.startswith(",")
            float(reply[1:])
