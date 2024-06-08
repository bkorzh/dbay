from backend.state import IModule, Core
from backend.addons.vsource import IVsourceAddon, ChSourceState
from typing import Literal
from backend.udp_control import Controller, ParentUDP

from backend.logging import get_logger
logger = get_logger(__name__)



class dac4D(IModule):
    module_type: Literal["dac4D"] = "dac4D"
    core: Core
    vsource: IVsourceAddon


def create_prototype(slot: int):
    channels = [ChSourceState(index=i, bias_voltage=0, activated=False, heading_text=f"{i}th ch dac4D", measuring=False) for i in range(4)]
    return dac4D(core=Core(slot=slot, type="dac4D", name="my dac4D module"), vsource=IVsourceAddon(channels=channels))



class dac4DController(Controller):
    def __init__(self, parent_udp: ParentUDP, module_slot: int):
        super().__init__(parent_udp, "dac4D")
        self.module_slot = module_slot

        # Resource acquisition is initialization (RAII)

        print("this is module slot in dac4D controller", self.module_slot)
        self.setDevice(self.module_slot)
        

    def sendVS(self, board: int, dacchan: int, voltage: float) -> str:
        pass

    def sendVSD(self, board: int, dacchan: int, voltage: float) -> str:
        message = ""
        if board <0 or board > 7:
            return "error, board out of range"
        if dacchan <0 or dacchan > 15:
            return "error, channel out of range"
        if  voltage < -10  or voltage > 10:
            return "error, voltage out of range"
        else:
            message = "DAC4D VSD"+ str(board) + " " + str(dacchan) + " " + str(voltage) + "\n"
        
        return self.parent_udp.udp.send_message(message)

    def setChVol(self, board: int, diffchan: int, voltage: float):
        if board <0 or board > 7:
            logger.error("error, board out of range")
            return -1
        if diffchan <0 or diffchan > 7:
            logger.error("error, channel out of range")
            return -1
        if  voltage < -20  or voltage > 20:
            return "error, voltage out of range"
        else:
            # r1 = self.setDACVol(board, diffchan*2, voltage/2)
            # r2 = self.setDACVol(board, diffchan*2+1, -voltage/2)
            r1 = self.sendVSD(board, diffchan, voltage)

            logger.debug(f"UDPdac4D: {r1}")
            # logger.debug(f"UDPdac4D: {r2}")
            if r1 == '+ok\n':
                return 0
            else: 
                return -1
            

# udp_dac4d = UDPdac4D(global_controller.udp_control)