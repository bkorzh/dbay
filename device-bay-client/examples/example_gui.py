"""Example: Using DBayClient in GUI (HTTP/stateful) mode.

Run this while the DBay GUI backend is running and accessible.
Adjust SERVER_IP if necessary.
"""
from dbay import DBayClient
from dbay import dac16D, dac4D
from typing import cast

SERVER_IP = "0.0.0.0"  # Change to the host running the GUI backend
PORT = 8345


def main():
    # retain_changes now defaults to True (persist settings). Pass retain_changes=False to auto-revert DAC channels.
    client = DBayClient(mode="gui", server_address=SERVER_IP, port=PORT)
    client.list_modules()

    # Attempt to work with a dac16D expected in slot 1 (adjust as needed)
    mod = cast(dac4D, client.module(2, expected="dac4D"))
    if mod:
        mod.set_voltage(1, 2.0, activated=True)
        # mod.set_voltage_shared(0.5)
        # mod.set_bias(2.0)
        
        print("Updated dac4D slot 2")
    else:
        print("No dac4D in slot 2.")



    mod = cast(dac4D, client.module(6, expected="dac4D"))
    if mod:
        mod.set_voltage(0, 3.3, activated=True)
        print("Updated dac4D slot 6")
    else:
        print("No dac4D in slot 6.")

if __name__ == "__main__":
    main()
