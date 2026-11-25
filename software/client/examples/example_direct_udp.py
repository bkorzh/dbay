"""Example: Using DBayClient in direct UDP (stateless) mode.

Requires network reachability to the mainframe. Adjust HOST and PORT.
"""
from dbay import DBayClient
from dbay import dac4D, dac16D

HOST = "192.168.0.108"  # Replace with your device's IP
PORT = 8880


def main():
    client = DBayClient(mode="direct", direct_host=HOST, direct_port=PORT)

    # Attach DAC4D in slot 0 and set voltages
    dac4 = client.attach_module(0, dac4D)
    dac4.set_voltage(0, 5.0)
    dac4.set_voltage_diff(1, -2.0)

    # Attach DAC16D in slot 1 and perform operations
    dac16 = client.attach_module(1, dac16D)
    dac16.set_voltage(10, -1.25)
    dac16.set_bias(3.0)
    print("Raw read:", dac16.read())

    # Raw command (expert mode)
    resp = client.direct_send("DAC16D VS 1 5 2.5")
    print("Raw command response:", resp)


if __name__ == "__main__":
    main()
