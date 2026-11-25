"""Voltage-source addon — re-exported from the shared client package.

Both the state models and the command payloads live in :mod:`dbay.addons.vsource`
so the GUI backend and any client validate against one definition. They are
re-exported *here* rather than imported directly at each call site because
`pydantic_to_typescript.py` generates the frontend's
`lib/addons/vsource/interface.ts` from this module: the frontend imports
`ChSourceState`, `IVsourceAddon`, `VsourceChange` and `SharedVsourceChange`
from it by name.
"""

from dbay.addons.vsource import (
    ChSourceState,
    IVsourceAddon,
    SharedVsourceChange,
    VsourceChange,
)

__all__ = [
    "ChSourceState",
    "IVsourceAddon",
    "VsourceChange",
    "SharedVsourceChange",
]
