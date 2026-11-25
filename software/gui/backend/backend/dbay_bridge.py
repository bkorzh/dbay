"""Bridge module that creates the DBayClient instance.

This module is separate from initialize.py to avoid circular imports.
The module spec files can import dbay_client from here without triggering
the initialize.py -> state.py -> modules/ import chain.
"""

from backend.udp_control import parent_udp
from backend.udp_adapter import UDPAdapter
from dbay.client import DBayClient


# Create a DBayClient in direct mode using the backend's UDP infrastructure.
# This allows controllers to delegate to device-bay-client modules for UDP commands.
# We pass parent_udp (not parent_udp.udp) so dynamic UDP replacement works correctly.
_udp_adapter = UDPAdapter(parent_udp)
dbay_client = DBayClient(mode="direct", connection=_udp_adapter)
