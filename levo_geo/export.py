"""Write the full configuration tables out as CSV: `python3 -m levo_geo.export`."""

from __future__ import annotations

import csv
from pathlib import Path

from .calibrate import calibrate
from .configs import DEFAULT_FORK_SAG_FRACTION, GEOMETRY_FIELDS, build_rows
from .data import MODELS

__all__ = ["COLUMNS", "write_csvs"]

COLUMNS = (
    "model",
    "fork_travel",
    "fork_a2c",
    "horst_pivot",
    "headset_cup",
    "shock_extension",
    "is_stock",
    *GEOMETRY_FIELDS,
    "rear_wheel_travel",
    "shock",
    "leverage_ratio",
    "rear_sag_mm_range",
    "rear_sag_pct_range",
    "fork_sag_applied",
    "rear_sag_applied",
)

#: Decimal places per column; angles to 2, lengths to 1.
_PRECISION = {
    "head_tube_angle": 2,
    "seat_tube_angle": 2,
    "leverage_ratio": 3,
}


def _format(column: str, value) -> str:
    if isinstance(value, float):
        return f"{value:.{_PRECISION.get(column, 1)}f}"
    return str(value)


def write_csvs(
    outdir: Path | str = Path(__file__).resolve().parent.parent / "output",
    *,
    fork_sag_fraction: float = DEFAULT_FORK_SAG_FRACTION,
) -> list[Path]:
    """Write a static and a sagged table for each model.  Returns the paths written."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    written = []
    for model in MODELS:
        cal = calibrate(model)
        for kind, sagged in (("static", False), ("sag", True)):
            rows = build_rows(
                model, cal, sagged=sagged, fork_sag_fraction=fork_sag_fraction
            )
            path = outdir / f"{model.short}_s4_{kind}.csv"
            with open(path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(COLUMNS)
                for row in rows:
                    writer.writerow([_format(c, row[c]) for c in COLUMNS])
            written.append(path)
    return written


if __name__ == "__main__":
    for path in write_csvs():
        print(f"wrote {path}")
