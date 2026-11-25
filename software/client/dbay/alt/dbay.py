import socket
import serial


class DeviceError(Exception):
    """Raised when the device returns an error or invalid response."""


class DeviceConnection:
    def __init__(self, mode="udp", host="192.168.0.108", port=8880,
                 serial_port=None, baudrate=115200, timeout=1):
        """
        mode: "udp" or "serial"
        host/port: used in UDP mode
        serial_port/baudrate: used in Serial mode
        """
        self.mode = mode
        self.host = host
        self.port = port
        self.timeout = timeout
        self.serial_port = serial_port
        self.baudrate = baudrate

        if self.mode == "serial":
            if not self.serial_port:
                raise ValueError("serial_port must be specified in serial mode")
            self.ser = serial.Serial(self.serial_port, baudrate=self.baudrate, timeout=self.timeout)

    def send(self, message: str) -> str:
        message = message.strip() + "\n"

        if self.mode == "udp":
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(self.timeout)
                sock.sendto(message.encode(), (self.host, self.port))
                try:
                    data, _ = sock.recvfrom(4096)
                    response = data.decode().strip()
                except socket.timeout:
                    raise DeviceError("Timeout waiting for device response")
        else:  # serial
            self.ser.write(message.encode())
            response = self.ser.readline().decode().strip()
            print(response)
        #if response != "+ok":
        #    raise DeviceError(f"Unexpected response from device: {response}")

        return response


# -------------------------
# Base Device
# -------------------------

class Device:
    def __init__(self, conn: DeviceConnection, address: int, dev_type: str):
        if not (0 <= address <= 7):
            raise ValueError("address must be in range 0–7")
        self.conn = conn
        self.address = address
        self.dev_type = dev_type
        self.conn.send(f"SETDEV {address} {dev_type}")

    def reset(self):
        return self.conn.send("reset")

    def help(self):
        return self.conn.send("help")

    def debug(self, enable: bool):
        return self.conn.send(f"debug {'on' if enable else 'off'}")


# -------------------------
# Device Implementations
# -------------------------

class DAC4D(Device):
    def __init__(self, conn, address):
        super().__init__(conn, address, "DAC4D")

    def set_voltage(self, channel: int, value: float):
        if not (0 <= channel <= 7):
            raise ValueError("channel must be 0–7")
        if not (-10 <= value <= 10):
            raise ValueError("voltage must be -10..10")
        return self.conn.send(f"DAC4D VS {self.address} {channel} {value}")

    def set_voltage_diff(self, channel: int, value: float):
        if not (0 <= channel <= 3):
            raise ValueError("channel must be 0–3")
        if not (-10 <= value <= 10):
            raise ValueError("voltage must be -10..10")
        return self.conn.send(f"DAC4D VSD {self.address} {channel} {value}")


class DAC16D(Device):
    def __init__(self, conn, address):
        super().__init__(conn, address, "DAC16D")

    def set_voltage(self, channel: int, value: float):
        if not (0 <= channel <= 31):
            raise ValueError("channel must be 0–31")
        if not (-10 <= value <= 10):
            raise ValueError("voltage must be -10..10")
        return self.conn.send(f"DAC16D VS {self.address} {channel} {value}")

    def set_voltage_diff(self, channel: int, value: float):
        if not (-3 <= channel <= 15):
            raise ValueError("channel must be -3..15")
        if not (-10 <= value <= 10):
            raise ValueError("voltage must be -10..10")
        return self.conn.send(f"DAC16D VSD {self.address} {channel} {value}")

    def read(self):
        return self.conn.send(f"DAC16D VR {self.address}")

    def set_bias(self, value: float):
        if not (0 <= value <= 8):
            raise ValueError("bias voltage must be 0..8")
        return self.conn.send(f"DAC16D VSB {self.address} {value}")


class FAFD(Device):
    def __init__(self, conn, address):
        super().__init__(conn, address, "FAFD")

    def read(self, channel: int):
        if not (0 <= channel <= 3):
            raise ValueError("channel must be 0–3")
        return self.conn.send(f"FAFD VR {self.address} {channel}")

    def set_voltage(self, channel: int, value: float):
        if not (0 <= channel <= 3):
            raise ValueError("channel must be 0–3")
        if not (0 <= value <= 2.5):
            raise ValueError("voltage must be 0..2.5")
        return self.conn.send(f"FAFD VS {self.address} {channel} {value}")


class HIC4(Device):
    def __init__(self, conn, address):
        super().__init__(conn, address, "HIC4")

    def set_voltage(self, channel: int, value: float):
        if not (0 <= channel <= 3):
            raise ValueError("channel must be 0–3")
        # voltage range TBD, skip validation for now
        return self.conn.send(f"HIC4 VS {self.address} {channel} {value}")


class ADC4D(Device):
    def __init__(self, conn, address):
        super().__init__(conn, address, "ADC4D")

    def read_diff(self, channel: int):
        if not (0 <= channel <= 4):
            raise ValueError("channel must be 0–4")
        return self.conn.send(f"ADC4D VRD {self.address} {channel}")


class DAC4ETH(Device):
    def __init__(self, conn, address):
        super().__init__(conn, address, "DAC4ETH")

    def set_voltage(self, channel: int, value: float):
        if not (0 <= channel <= 31):
            raise ValueError("channel must be 0–31")
        if not (-10 <= value <= 10):
            raise ValueError("voltage must be -10..10")
        return self.conn.send(f"DAC4ETH VS {self.address} {channel} {value}")

    def set_voltage_diff(self, channel: int, value: float):
        if not (0 <= channel <= 15):
            raise ValueError("channel must be 0–15")
        if not (-10 <= value <= 10):
            raise ValueError("voltage must be -10..10")
        return self.conn.send(f"DAC4ETH VSD {self.address} {channel} {value}")