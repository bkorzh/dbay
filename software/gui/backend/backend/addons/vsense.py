"""Voltage-sense addon: shared state models + GUI command payloads.

See :mod:`backend.addons.vsource` for why the state models are re-exported
here rather than imported from :mod:`dbay.state` at each call site.
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
