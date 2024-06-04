
from backend.location import BASE_DIR
import json
import os

from backend.DACVME_ctrl import VMECTRL

# load defuault ip address and port
with open(os.path.join(BASE_DIR, "vsource_params.json"), "r") as f:
    vsource_params = json.load(f)
    vsource = VMECTRL(vsource_params["ipaddr"], vsource_params["port"])