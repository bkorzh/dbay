"""Voltage-source addon: shared state models + GUI command payloads.

State models are re-exported from :mod:`dbay.state` (shared with the Python
client). They are re-exported *here* rather than imported directly by callers
because `pydantic_to_typescript.py` generates the frontend's
`lib/addons/vsource/interface.ts` from this module — the frontend imports
`ChSourceState` and `IVsourceAddon` from it by name.
"""

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
    link_enabled: list[bool]  # the channels to apply the change to
