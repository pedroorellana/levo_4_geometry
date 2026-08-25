"""Enumerate every legal configuration and produce its full geometry sheet.

Levo 4      fork 160/170  x  Horst Short/Long  x  cup -1/0/+1  x  shock ext Short/Long  = 24
Levo 4 EVO  fork 170/180  x  Horst Short/Long  x  cup -1/0/+1                           = 12

Results are reported as `published_baseline + modelled_delta`, so the stock row is
identical to the catalogue table and every other row differs from it by a physically
derived amount.  That keeps the sub-millimetre rounding slop in the published (and
over-determined) chart from leaking into all 36 rows.
"""

from __future__ import annotations

import itertools
import math
from math import cos, radians, sin

from .calibrate import Calibration, calibrate
from .data import LEVO4, LEVO4_EVO, MODELS, ModelSpec, fork_a2c
from .frame import Geometry, solve

__all__ = [
    "ANCHORED_FIELDS",
    "GEOMETRY_FIELDS",
    "DEFAULT_FORK_SAG_FRACTION",
    "build_rows",
    "all_rows",
    "stock_row",
    "self_test",
]

#: Modelled field -> the column of the published chart it is anchored to.
ANCHORED_FIELDS = {
    "head_tube_angle": "head_tube_angle",
    "seat_tube_angle": "seat_tube_angle",
    "bb_height": "bb_height",
    "bb_drop": "bb_drop",
    "reach": "reach",
    "stack": "stack",
    "chainstay": "chainstay",
    "wheelbase": "wheelbase",
    "front_center": "front_center",
    "trail": "trail",
    "effective_top_tube": "effective_top_tube",
    "standover": "standover",
}

#: Geometry columns in report order.
GEOMETRY_FIELDS = (
    "head_tube_angle",
    "seat_tube_angle",
    "bb_height",
    "bb_drop",
    "reach",
    "stack",
    "chainstay",
    "wheelbase",
    "front_center",
    "trail",
    "mechanical_trail",
    "wheel_flop",
    "effective_top_tube",
    "standover",
)

#: Fork sag as a fraction of travel.  Specialized publishes a rear shock sag range but
#: no fork figure; 15% is the usual starting point for a long-travel enduro fork.
DEFAULT_FORK_SAG_FRACTION = 0.15

_CUP_LABELS = {-1.0: "-1 deg", 0.0: "0 deg", 1.0: "+1 deg"}


def _anchor(modelled: Geometry, stock: Geometry, model: ModelSpec) -> dict[str, float]:
    """Shift a modelled geometry so the stock configuration matches the chart exactly."""
    published = model.geometry
    out = {
        field: getattr(published, column)
        + (getattr(modelled, field) - getattr(stock, field))
        for field, column in ANCHORED_FIELDS.items()
    }
    # Derive the trail companions from the anchored values rather than anchoring them
    # separately, so the three stay mutually consistent.
    hta = radians(out["head_tube_angle"])
    out["mechanical_trail"] = out["trail"] * sin(hta)
    out["wheel_flop"] = out["trail"] * sin(hta) * cos(hta)
    out["pitch"] = modelled.pitch - stock.pitch
    return out


def build_rows(
    model: ModelSpec,
    calibration: Calibration | None = None,
    *,
    sagged: bool = False,
    fork_sag_fraction: float = DEFAULT_FORK_SAG_FRACTION,
    rear_sag_mm: float | None = None,
) -> list[dict]:
    """Every configuration of one model, as a list of flat dicts.

    With `sagged=True` the fork is compressed by `fork_sag_fraction` of its travel and
    the rear axle is raised by `rear_sag_mm` (default: the midpoint of the manual's
    recommended shock sag, converted through the average leverage ratio) before the
    bike is re-levelled.
    """
    cal = calibration or calibrate(model)
    stock = cal.stock

    if rear_sag_mm is None:
        lo, hi = model.rear_wheel_sag_range
        rear_sag_mm = (lo + hi) / 2

    sag_lo, sag_hi = model.rear_wheel_sag_range
    pct_lo, pct_hi = model.rear_sag_percent_range

    rows = []
    for travel, horst, cup, ext in itertools.product(
        model.fork_travel_options,
        ("Short", "Long"),
        sorted(cal.cups),
        sorted(cal.shock_ext, reverse=True),  # Short before Long
    ):
        horst_fit = cal.horst[horst]
        ext_fit = cal.shock_ext[ext]
        cup_fit = cal.cups[cup]

        fork_sag = fork_sag_fraction * travel if sagged else 0.0
        rear_sag = rear_sag_mm if sagged else 0.0

        geo = solve(
            cal.frame,
            fork_a2c(travel),
            cup=cup_fit.tilt,
            rear_dx=horst_fit.dx + ext_fit.dx,
            rear_dy=horst_fit.dy + ext_fit.dy,
            fork_sag=fork_sag,
            rear_sag=rear_sag,
        )

        row = {
            "model": model.name,
            "fork_travel": travel,
            "fork_a2c": fork_a2c(travel),
            "horst_pivot": horst,
            "headset_cup": _CUP_LABELS[cup],
            "shock_extension": ext if model.has_shock_extension_chip else "n/a",
            "is_stock": (
                travel == model.stock_fork_travel
                and horst == "Short"
                and cup == 0.0
                and ext == "Short"
            ),
        }
        row.update(_anchor(geo, stock, model))
        row.update(
            {
                "rear_wheel_travel": model.rear_wheel_travel,
                "shock": f"{model.shock_length:g} x {model.shock_stroke:g}",
                "leverage_ratio": model.leverage_ratio,
                "rear_sag_mm_range": f"{sag_lo:.0f}-{sag_hi:.0f}",
                "rear_sag_pct_range": f"{pct_lo:.0f}-{pct_hi:.0f}%",
                "fork_sag_applied": fork_sag,
                "rear_sag_applied": rear_sag,
            }
        )
        rows.append(row)
    return rows


def all_rows(**kwargs) -> list[dict]:
    """Every configuration of both models."""
    return [row for model in MODELS for row in build_rows(model, **kwargs)]


def stock_row(model: ModelSpec, **kwargs) -> dict:
    """The as-delivered configuration for one model."""
    return next(r for r in build_rows(model, **kwargs) if r["is_stock"])


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------

def _check(label: str, got: float, want: float, tol: float, failures: list[str]) -> None:
    if abs(got - want) > tol:
        failures.append(f"{label}: got {got:.4f}, want {want:.4f} (tol {tol})")


def self_test(verbose: bool = True) -> bool:
    """Validate the model against every published number.  Returns True on success."""
    from .data import HEADSET_CUP_DELTAS, HORST_LONG_DELTA, SHOCK_EXT_LONG_DELTA

    failures: list[str] = []
    log = print if verbose else (lambda *a, **k: None)

    cals = {m.short: calibrate(m) for m in MODELS}

    # 1. Flip-chip fits must reproduce all three published deltas.
    log("Flip-chip calibration (3 published targets, 2 free parameters):")
    for model in MODELS:
        cal = cals[model.short]
        for group, published in (
            (cal.horst, HORST_LONG_DELTA),
            (cal.shock_ext, SHOCK_EXT_LONG_DELTA),
        ):
            fit = group.get("Long")
            if fit is None:
                continue
            log(
                f"  {model.name:11s} {fit.name:16s} dx={fit.dx:+7.3f} dy={fit.dy:+7.3f}"
                f"  worst residual {fit.worst_residual:.4f}"
            )
            for key, value in fit.residual.items():
                _check(f"{model.name} {fit.name} {key}", value, 0.0, 0.3, failures)

    # 2. Both models must fit the shared rear triangle to the same offset.
    l4, evo = cals["levo4"].horst["Long"], cals["levo4_evo"].horst["Long"]
    log(f"\nHorst Long offset agreement between models: "
        f"dx {l4.dx:+.3f} vs {evo.dx:+.3f}, dy {l4.dy:+.3f} vs {evo.dy:+.3f}")
    _check("Horst dx agreement", l4.dx, evo.dx, 0.5, failures)
    _check("Horst dy agreement", l4.dy, evo.dy, 0.5, failures)

    # 3. Headset cups must land on the published net head angle change.
    log("\nHeadset cup calibration:")
    for model in MODELS:
        for nominal, fit in sorted(cals[model.short].cups.items()):
            log(f"  {model.name:11s} {_CUP_LABELS[nominal]:7s} physical tilt {fit.tilt:+.3f} deg"
                f"  BB residual {fit.residual['bb_height']:+.2f} mm")
            _check(
                f"{model.name} cup {nominal} head angle",
                fit.residual["head_tube_angle"], 0.0, 0.03, failures,
            )

    # 4. The stock row must reproduce the published chart exactly.
    log("\nStock row vs published chart:")
    for model in MODELS:
        row = stock_row(model, calibration=cals[model.short])
        for field, column in ANCHORED_FIELDS.items():
            _check(
                f"{model.name} stock {field}",
                row[field], getattr(model.geometry, column), 1e-9, failures,
            )
        log(f"  {model.name:11s} all {len(ANCHORED_FIELDS)} published columns match exactly")

    # 5. Single-adjustment rows must reproduce the manual's delta table.
    log("\nSingle-adjustment rows vs manual delta table:")
    for model in MODELS:
        cal = cals[model.short]
        rows = build_rows(model, cal)
        base = next(r for r in rows if r["is_stock"])
        # Tolerances differ by adjustment.  The flip chips are fitted to all three
        # published deltas at once, so all three should land inside 0.3 mm / 0.03 deg.
        # The headset cup has a single free parameter, spent on hitting the published
        # +/-1.0 deg exactly; its BB height is then a prediction, not a fit, and lands
        # about 0.4 mm off the manual's rounded +/-2 mm.
        chip_tol = {"chainstay": 0.3, "bb_height": 0.3, "head_tube_angle": 0.03}
        cup_tol = {"chainstay": 1e-9, "bb_height": 0.5, "head_tube_angle": 0.01}
        cases = [("Horst Long", {"horst_pivot": "Long"}, HORST_LONG_DELTA, chip_tol)]
        if model.has_shock_extension_chip:
            cases.append(
                ("Shock Ext Long", {"shock_extension": "Long"}, SHOCK_EXT_LONG_DELTA, chip_tol)
            )
        for nominal in (-1.0, 1.0):
            cases.append(
                (f"Cup {_CUP_LABELS[nominal]}",
                 {"headset_cup": _CUP_LABELS[nominal]},
                 HEADSET_CUP_DELTAS[nominal],
                 cup_tol)
            )
        for label, selector, published, tolerance in cases:
            row = next(
                r for r in rows
                if all(r[k] == v for k, v in selector.items())
                and all(
                    r[k] == base[k]
                    for k in ("fork_travel", "horst_pivot", "headset_cup", "shock_extension")
                    if k not in selector
                )
            )
            parts = []
            for field, want in published.items():
                got = row[field] - base[field]
                parts.append(f"{field} {got:+.2f}/{want:+.1f}")
                _check(f"{model.name} {label} {field}", got, want, tolerance[field], failures)
            log(f"  {model.name:11s} {label:15s} " + "  ".join(parts))

    # 6. The EVO chart must be the Levo 4 frame rotated nose-up by ~0.9 deg.
    log("\nCross-check: EVO chart as the Levo 4 frame rotated nose-up")
    from .frame import rotate
    g4, ge = LEVO4.geometry, LEVO4_EVO.geometry
    pitch = g4.head_tube_angle - ge.head_tube_angle
    reach, stack = rotate((g4.reach, g4.stack), pitch)
    log(f"  rotate Levo 4 by {pitch:+.2f} deg -> reach {reach:.1f} (EVO chart {ge.reach:.0f})"
        f", stack {stack:.1f} (EVO chart {ge.stack:.0f})")
    _check("EVO cross-check reach", reach, ge.reach, 1.0, failures)
    _check("EVO cross-check stack", stack, ge.stack, 1.0, failures)
    _check("EVO cross-check STA", g4.seat_tube_angle - pitch, ge.seat_tube_angle, 0.2, failures)

    # 7. Row counts.
    counts = {m.name: len(build_rows(m, cals[m.short])) for m in MODELS}
    log(f"\nConfiguration counts: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    _check("Levo 4 row count", counts["Levo 4"], 24, 0, failures)
    _check("Levo 4 EVO row count", counts["Levo 4 EVO"], 12, 0, failures)

    # 8. Monotonic trends.
    log("\nTrend checks:")
    for model in MODELS:
        rows = build_rows(model, cals[model.short])
        base = next(r for r in rows if r["is_stock"])
        longer = next(
            r for r in rows
            if r["fork_travel"] == max(model.fork_travel_options)
            and all(r[k] == base[k] for k in ("horst_pivot", "headset_cup", "shock_extension"))
        )
        if longer is not base:
            for field, sense in (
                ("head_tube_angle", -1), ("bb_height", 1), ("reach", -1),
                ("stack", 1), ("wheelbase", 1), ("trail", 1),
            ):
                change = (longer[field] - base[field]) * sense
                if change <= 0:
                    failures.append(f"{model.name} longer fork: {field} moved the wrong way")
            log(f"  {model.name:11s} longer fork -> slacker, higher BB, shorter reach  OK")
        horst_long = next(
            r for r in rows
            if r["horst_pivot"] == "Long"
            and all(r[k] == base[k] for k in ("fork_travel", "headset_cup", "shock_extension"))
        )
        assert horst_long["chainstay"] > base["chainstay"]
        assert horst_long["bb_height"] < base["bb_height"]
        assert horst_long["reach"] < base["reach"]
        log(f"  {model.name:11s} Horst Long -> longer CS, lower BB, shorter reach     OK")

    if failures:
        log("\nFAILED:")
        for failure in failures:
            log("  " + failure)
        return False
    log("\nAll checks passed.")
    return True
