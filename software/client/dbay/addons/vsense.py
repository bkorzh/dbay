"""Voltage-sense addon: shared state models + command payloads.

See :mod:`dbay.addons.vsource` — the state models live in :mod:`dbay.state`
and are re-exported here for import compatibility.
"""

from pydantic import BaseModel

from dbay.state import ChSenseState, IVsenseAddon

__all__ = ["ChSenseState", "IVsenseAddon", "VsenseChange"]


class VsenseChange(BaseModel):
    module_index: int
    index: int
    voltage: float
    measuring: bool
    name: str
