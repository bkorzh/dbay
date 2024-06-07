from backend.addons.vsource import VsourceChange, ChSourceState
from backend.udp_control import UdpControl, Controler
from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException

from backend.location import BASE_DIR


import os
import csv
from datetime import datetime
from backend.initialize import global_controller

from backend.state import IModule, Core
from backend.addons.vsource import IVsourceAddon, ChSourceState

from typing import cast
from backend.logging import get_logger

from backend.modules.dac4D_spec import dac4D


from backend.initialize import global_state


logger = get_logger(__name__)

router = APIRouter(
    prefix="/dac16D",
    responses={404: {"description": "Not found"}},
)

