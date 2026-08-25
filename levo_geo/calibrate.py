"""Calibrate each adjustment against the deltas Specialized publishes.

The manual gives three numbers per adjustment - chainstay length, BB height and head
tube angle.  For the two flip chips those three are recovered by a single rigid
relocation of the rear axle within the frame, so fitting the two-parameter offset
`(dx, dy)` to the three published targets is over-determined by one: the residual is
therefore a real test of the model rather than a curve fit, and it comes out below
0.3 mm / 0.03 deg for both chips.

The headset cup is calibrated the same way, on its one free parameter: the physical
tilt of the steer axis is solved so that the *ground-referenced* head tube angle moves
by exactly the +/-1.0 deg the manual advertises.
"""

from __future__ import annotations

from dataclasses import dataclass

from .data import (
    HEADSET_CUP_DELTAS,
    HORST_LONG_DELTA,
    SHOCK_EXT_LONG_DELTA,
    ModelSpec,
    fork_a2c,
)
from .frame import Frame, solve

__all__ = ["ChipFit", "CupFit", "Calibration", "calibrate"]

#: Weight on the angle residual so that 0.1 deg counts about like 1 mm.
_ANGLE_WEIGHT = 10.0


@dataclass(frozen=True)
class ChipFit:
    """A flip chip modelled as a rear-axle offset in frame coordinates."""

    name: str
    dx: float
    dy: float
    residual: dict[str, float]  # modelled delta minus published delta

    @property
    def worst_residual(self) -> float:
        return max(abs(v) for v in self.residual.values())


@dataclass(frozen=True)
class CupFit:
    """A headset cup modelled as a tilt of the steer axis within the frame."""

    nominal: float  # the published label, -1 / 0 / +1
    tilt: float  # physical tilt needed to achieve it, degrees
    residual: dict[str, float]


@dataclass(frozen=True)
class Calibration:
    model: ModelSpec
    frame: Frame
    stock: object  # Geometry at the stock configuration
    horst: dict[str, ChipFit]
    shock_ext: dict[str, ChipFit]
    cups: dict[float, CupFit]


def _build_frame(model: ModelSpec) -> Frame:
    g = model.geometry
    return Frame.from_published(
        reach=g.reach,
        stack=g.stack,
        head_tube_length=g.head_tube_length,
        head_tube_angle=g.head_tube_angle,
        seat_tube_angle=g.seat_tube_angle,
        chainstay=g.chainstay,
        bb_height=g.bb_height,
        bb_drop=g.bb_drop,
        standover=g.standover,
        rake=g.rake,
    )


def _cost(modelled, stock, target: dict[str, float]) -> float:
    return (
        (modelled.chainstay - stock.chainstay - target["chainstay"]) ** 2
        + (modelled.bb_height - stock.bb_height - target["bb_height"]) ** 2
        + (
            _ANGLE_WEIGHT
            * (modelled.head_tube_angle - stock.head_tube_angle - target["head_tube_angle"])
        )
        ** 2
    )


def _residual(modelled, stock, target: dict[str, float]) -> dict[str, float]:
    return {
        "chainstay": modelled.chainstay - stock.chainstay - target["chainstay"],
        "bb_height": modelled.bb_height - stock.bb_height - target["bb_height"],
        "head_tube_angle": (
            modelled.head_tube_angle - stock.head_tube_angle - target["head_tube_angle"]
        ),
    }


def _fit_chip(name: str, frame: Frame, a2c: float, stock, target: dict[str, float]) -> ChipFit:
    """Coarse-to-fine grid search for the rear-axle offset reproducing `target`."""
    lo_x, hi_x, lo_y, hi_y = -40.0, 40.0, -40.0, 40.0
    steps = 40
    best = (float("inf"), 0.0, 0.0, None)
    for _ in range(45):
        best = (float("inf"), 0.0, 0.0, None)
        for i in range(steps + 1):
            dx = lo_x + (hi_x - lo_x) * i / steps
            for j in range(steps + 1):
                dy = lo_y + (hi_y - lo_y) * j / steps
                got = solve(frame, a2c, rear_dx=dx, rear_dy=dy)
                cost = _cost(got, stock, target)
                if cost < best[0]:
                    best = (cost, dx, dy, got)
        _, dx, dy, _ = best
        span_x, span_y = (hi_x - lo_x) / 8, (hi_y - lo_y) / 8
        lo_x, hi_x = dx - span_x, dx + span_x
        lo_y, hi_y = dy - span_y, dy + span_y

    _, dx, dy, got = best
    return ChipFit(name=name, dx=dx, dy=dy, residual=_residual(got, stock, target))


def _fit_cup(nominal: float, frame: Frame, a2c: float, stock) -> CupFit:
    """Solve the physical steer-axis tilt giving the published net head angle change."""
    target = HEADSET_CUP_DELTAS[nominal]
    if nominal == 0.0:
        return CupFit(nominal=0.0, tilt=0.0, residual=_residual(stock, stock, target))

    want = target["head_tube_angle"]

    def net(tilt: float) -> float:
        return solve(frame, a2c, cup=tilt).head_tube_angle - stock.head_tube_angle

    lo, hi = (-3.0, 0.0) if want < 0 else (0.0, 3.0)
    for _ in range(80):
        mid = (lo + hi) / 2
        if net(mid) > want:
            hi = mid
        else:
            lo = mid
    tilt = (lo + hi) / 2
    return CupFit(nominal=nominal, tilt=tilt, residual=_residual(solve(frame, a2c, cup=tilt), stock, target))


def calibrate(model: ModelSpec) -> Calibration:
    """Fit every adjustment for one model against the manual's published deltas."""
    frame = _build_frame(model)
    a2c = fork_a2c(model.stock_fork_travel)
    stock = solve(frame, a2c)

    horst = {
        "Short": ChipFit("Horst Short", 0.0, 0.0, {k: 0.0 for k in HORST_LONG_DELTA}),
        "Long": _fit_chip("Horst Long", frame, a2c, stock, HORST_LONG_DELTA),
    }

    shock_ext = {
        "Short": ChipFit("Shock Ext Short", 0.0, 0.0, {k: 0.0 for k in SHOCK_EXT_LONG_DELTA})
    }
    if model.has_shock_extension_chip:
        shock_ext["Long"] = _fit_chip(
            "Shock Ext Long", frame, a2c, stock, SHOCK_EXT_LONG_DELTA
        )

    cups = {n: _fit_cup(n, frame, a2c, stock) for n in sorted(HEADSET_CUP_DELTAS)}

    return Calibration(
        model=model, frame=frame, stock=stock, horst=horst, shock_ext=shock_ext, cups=cups
    )
