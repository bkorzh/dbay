"""Module state primitives.

Re-exported from :mod:`dbay.state` — the schema is shared with the Python
client so both sides validate against one definition instead of maintaining
parallel copies that drift.
"""

from dbay.state import Core, ModuleState, ModuleState as IModule

__all__ = ["Core", "ModuleState", "IModule"]
