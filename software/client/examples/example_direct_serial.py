"""Example: Using DBayClient in direct Serial (stateless) mode.

Ensure the serial device path and permissions are correct.
Install pyserial (already a dependency) if running standalone.
"""
from dbay import DBayClient
from dbay import HIC4, ADC4D

SERIAL_PORT = "/dev/ttyUSB0"  # Adjust for your platform (e.g., /dev/ttyACM0, COM5)
BAUDRATE = 115200


def main():
    client = DBayClient(
        mode="direct",
        direct_transport="serial",
        serial_port=SERIAL_PORT,
        baudrate=BAUDRATE,
        timeout=1.0,
    )

    hic4 = client.attach_module(2, HIC4)
    hic4.set_voltage(0, 0.75)

    adc = client.attach_module(3, ADC4D)
    try:
        print("ADC4D diff ch1:", adc.read_diff(1))
    except Exception as e:
        print("ADC read failed:", e)

    client.close()


if __name__ == "__main__":
    main()
