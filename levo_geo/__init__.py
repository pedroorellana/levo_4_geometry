"""Geometry calculator for the Specialized Levo 4 and Levo 4 EVO, size S4.

Works out the complete geometry sheet for every combination of fork length, Horst
pivot flip chip, headset cup and shock extension flip chip - including the changes
Specialized does not publish (reach, stack, seat angle, wheelbase, front centre,
trail, effective top tube), which all move because each adjustment re-levels the bike.

    from levo_geo import LEVO4, build_rows
    rows = build_rows(LEVO4)

Stdlib only; no virtualenv required.
"""

from .calibrate import Calibration, ChipFit, CupFit, calibrate
from .configs import GEOMETRY_FIELDS, all_rows, build_rows, self_test, stock_row
from .data import LEVO4, LEVO4_EVO, MODELS, ModelSpec, PublishedGeometry, fork_a2c
from .frame import Frame, Geometry, solve

__all__ = [
    "LEVO4",
    "LEVO4_EVO",
    "MODELS",
    "ModelSpec",
    "PublishedGeometry",
    "Frame",
    "Geometry",
    "solve",
    "fork_a2c",
    "calibrate",
    "Calibration",
    "ChipFit",
    "CupFit",
    "build_rows",
    "all_rows",
    "stock_row",
    "self_test",
    "GEOMETRY_FIELDS",
]
