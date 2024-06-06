
from backend.location import BASE_DIR
import json
import os

from backend.udp_control import UdpControl
from backend.state import IModule, Core, SystemState
from backend.modules import dac4D_spec


class GlobalControl:
    def __init__(self, udp_control: UdpControl):
        self.udp_control = udp_control

# load defuault ip address and port
with open(os.path.join(BASE_DIR, "vsource_params.json"), "r") as f:
    vsource_params = json.load(f)
    udp_control = UdpControl(vsource_params["ipaddr"], vsource_params["port"], dev_mode = vsource_params["dev_mode"])
    global_controller = GlobalControl(udp_control)



data = [IModule(core=Core(slot=i, type="empty", name="empty")) for i in range(8)]
data[3] = dac4D_spec.create_prototype(3)
# load dev mode setting. If true, python does not acctually send UDP messages to the rack. 
with open(os.path.join(BASE_DIR, "vsource_params.json"), "r") as f:
    vsource_params= json.load(f)
system_state = SystemState(data=data, valid=True, dev_mode=vsource_params["dev_mode"])