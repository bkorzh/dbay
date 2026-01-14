from backend.module import IModule, Core
from backend.addons.vsense import IVsenseAddon, ChSenseState
from typing import Literal
from backend.udp_control import Controller, ParentUDP

from backend.server_logging import get_logger
logger = get_logger(__name__)



class adc4D(IModule):
    module_type: Literal["adc4D"] = "adc4D"
    core: Core
    vsense: IVsenseAddon


def create_prototype(slot: int):
    channels = [ChSenseState(index=i, voltage=0, measuring=False, name=f"ADC4D Ch{i}") for i in range(5)]
    return adc4D(core=Core(slot=slot, type="adc4D", name="my adc4D module"), vsense=IVsenseAddon(channels=channels))



class adc4DController(Controller):
    def __init__(self, parent_udp: ParentUDP, module_slot: int):
        super().__init__(parent_udp, "ADC4D")
        self.module_slot = module_slot

        # Resource acquisition is initialization (RAII)
        print("this is module slot in adc4D controller", self.module_slot)
        self.setDevice(self.module_slot)
        

    def sendVRD(self, board: int, channel: int) -> str:
        """Send VRD command to read differential voltage from ADC channel"""
        message = ""
        if board < 0 or board > 7:
            return "error, board out of range"
        if channel < 0 or channel > 4:
            return f"error, channel out of range. channel: {channel}"
        else:
            message = "ADC4D VRD " + str(board) + " " + str(channel) + "\n"
            logger.info(message)
        
        return self.parent_udp.udp.send_message(message)

    def readChannelVoltage(self, board: int, channel: int) -> float:
        """Read voltage from a specific ADC channel"""
        if board < 0 or board > 7:
            logger.error("error, board out of range")
            return -1
        if channel < 0 or channel > 4:
            logger.error(f"error, channel out of range. channel: {channel}")
            return -1
        
        response = self.sendVRD(board, channel)
        logger.debug(f"UDP ADC4D response: {response}")
        
        try:
            # Parse the response to get the voltage value
            # Expected format: "+ok voltage_value\n" or just the voltage value
            if response.startswith('+ok'):
                voltage_str = response.split()[1] if len(response.split()) > 1 else "0"
                return float(voltage_str)
            else:
                # Try to parse directly as float
                return float(response.strip())
        except (ValueError, IndexError):
            logger.error(f"Failed to parse voltage response: {response}")
            return 0.0

    def readAllChannels(self, board: int) -> list[float]:
        """Read voltages from all 5 ADC channels"""
        voltages = []
        for channel in range(5):
            voltage = self.readChannelVoltage(board, channel)
            voltages.append(voltage)
        return voltages
