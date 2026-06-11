from backend.module import IModule, Core
from backend.addons.vsense import IVsenseAddon, ChSenseState
from typing import Literal
from pydantic import BaseModel
from backend.udp_control import Controller, ParentUDP
from backend.dbay_bridge import dbay_client
from dbay.modules.adc4d import ADC4D as ClientADC4D

from backend.server_logging import get_logger
logger = get_logger(__name__)


NUM_CHANNELS = 4

MIN_POLLING_HZ = 0.1
MAX_POLLING_HZ = 20.0


class PollingState(BaseModel):
    """Polling configuration for the adc4D module."""
    running: bool = False
    frequency: float = 2.0  # Hz


class adc4D(IModule):
    """Backend state model for adc4D module (tracks GUI state)."""
    module_type: Literal["adc4D"] = "adc4D"
    core: Core
    vsense: IVsenseAddon
    polling: PollingState = PollingState()


def create_prototype(slot: int):
    channels = [ChSenseState(index=i, voltage=0, measuring=False, name="") for i in range(NUM_CHANNELS)]
    return adc4D(
        core=Core(slot=slot, type="adc4D", name="my adc4D module"),
        vsense=IVsenseAddon(channels=channels),
        polling=PollingState(),
    )



class adc4DController(Controller):
    """Controller that delegates UDP commands to device-bay-client module."""

    def __init__(self, parent_udp: ParentUDP, module_slot: int):
        super().__init__(parent_udp, "ADC4D")
        self.module_slot = module_slot

        # Attach a client module for this slot
        self._module = dbay_client.attach_module(module_slot, ClientADC4D)

        logger.info(f"adc4DController initialized for slot {self.module_slot}")
        self.setDevice(self.module_slot)

    def readChannelVoltage(self, board: int, channel: int) -> float:
        """Read voltage from a specific ADC channel using device-bay-client module."""
        if board < 0 or board > 7:
            logger.error("error, board out of range")
            return -1
        if channel < 0 or channel > 4:
            logger.error(f"error, channel out of range. channel: {channel}")
            return -1

        try:
            response = self._module.read_diff(channel)
            logger.debug(f"ADC4D readChannelVoltage response: {response}")
            return self._parse_voltage(response)
        except Exception as e:
            logger.error(f"ADC4D readChannelVoltage failed: {e}")
            return 0.0

    @staticmethod
    def _parse_voltage(response: str) -> float:
        """Parse a firmware VRD response into a float.

        The firmware formats replies as:
          ",<float>"  successful float read (e.g. ",0.093000")
          "+ok"       generic success (dev_mode stub responses)
          "-<error>"  error message
        """
        resp = response.strip()
        if resp.startswith("Error"):
            # UDP.send_message returns transport failures as "Error: ..." strings
            logger.error(f"ADC4D read failed at the UDP transport: {resp}")
            return 0.0
        if resp.startswith(","):
            return float(resp[1:])
        if resp.startswith("+ok"):
            # Stub/dev-mode response carries no reading.
            parts = resp.split()
            return float(parts[1]) if len(parts) > 1 else 0.0
        if resp.startswith("-"):
            try:
                return float(resp)  # bare negative float
            except ValueError:
                logger.error(f"ADC4D read returned error: {resp}")
                return 0.0
        return float(resp)

    def readAllChannels(self, board: int) -> list[float]:
        """Read voltages from all ADC channels."""
        voltages = []
        for channel in range(NUM_CHANNELS):
            voltage = self.readChannelVoltage(board, channel)
            voltages.append(voltage)
        return voltages
