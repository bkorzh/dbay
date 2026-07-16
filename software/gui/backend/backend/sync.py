from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from lab_link import LabSync

from backend.initialize import global_state
from backend.location import PERSIST_DIR
from backend.module_registry import REGISTERED_MODULES
from backend.server_logging import get_logger
from backend.udp_control import parent_udp


logger = get_logger(__name__)

# DBAY_PERSIST=0 disables persistence (used by tests); DBAY_PERSIST_DB overrides
# the database location.
PERSIST_ENABLED = os.environ.get("DBAY_PERSIST", "1") != "0"
PERSIST_DB_PATH = os.environ.get(
    "DBAY_PERSIST_DB", str(Path(PERSIST_DIR) / "dbay_state.db")
)

sync = LabSync(persist=PERSIST_ENABLED, db_url=f"sqlite:///{PERSIST_DB_PATH}")

# The bound model is the single authoritative state: every attribute/list
# mutation anywhere in the tree is validated, batched, and broadcast by
# lab-link. There is no separate wire copy to keep in agreement.
sync.bind_state(global_state.system_state)

# Captured before the lifespan's load_state() swaps in persisted values:
# dev_mode is a launch-time setting from the config file, not session state.
_CONFIG_DEV_MODE = global_state.system_state.dev_mode


def _reset_transient_flags(module: Any) -> None:
    """Hardware output state is unknown at startup, so a restored session must
    not claim outputs are live. Keeps layout, names, and bias setpoints."""
    vsource = getattr(module, "vsource", None)
    if vsource is not None:
        for channel in vsource.channels:
            channel.activated = False
            channel.measuring = False
    vsense = getattr(module, "vsense", None)
    if vsense is not None:
        for channel in vsense.channels:
            channel.measuring = False
            channel.voltage = 0.0
    polling = getattr(module, "polling", None)
    if polling is not None:
        polling.running = False
    vsb = getattr(module, "vsb", None)
    if vsb is not None:
        vsb.activated = False
        vsb.measuring = False
    vr = getattr(module, "vr", None)
    if vr is not None:
        vr.measuring = False
        vr.voltage = 0.0


def restore_hardware_bindings() -> None:
    """Finish what lab-link's persistence restore cannot know about.

    During lifespan startup lab-link load_state()s the saved snapshot into the
    bound model in place, so global_state.system_state already holds the
    restored state. This rebuilds the hardware controllers for occupied slots
    and resets transient flags; must run after sync.lifespan is entered and
    before any commands are served.
    """
    if not PERSIST_ENABLED:
        return

    state = global_state.system_state
    state.dev_mode = _CONFIG_DEV_MODE

    for slot, module in enumerate(state.data):
        if module.module_type == "empty":
            continue
        registration = REGISTERED_MODULES.get(module.module_type)
        if registration is None:
            # load_state() validates against the SystemState union, so this is
            # unreachable unless the registry and union drift apart
            logger.warning("No controller registered for %r in slot %d", module.module_type, slot)
            continue
        _reset_transient_flags(module)
        global_state.controllers[slot] = registration.controller_class(parent_udp, slot)
        logger.info("Restored %s module in slot %d from persisted state", module.module_type, slot)
