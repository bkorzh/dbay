"""Voltage-source addon: shared state models + command payloads.

The state models are re-exported from :mod:`dbay.state`, which is the single
definition shared with the GUI backend. They previously existed here as a
parallel `BaseModel` copy that could drift from the server's.
"""

from typing import List

from pydantic import BaseModel

from dbay.state import ChSourceState, IVsourceAddon

__all__ = [
    "ChSourceState",
    "IVsourceAddon",
    "VsourceChange",
    "SharedVsourceChange",
]


# MESSAGE ##################################
class VsourceChange(BaseModel):
    module_index: int
    index: int
    bias_voltage: float
    activated: bool
    heading_text: str
    measuring: bool


class SharedVsourceChange(BaseModel):
    change: VsourceChange  # the change to apply
    link_enabled: List[bool]  # the channels to apply the change to
