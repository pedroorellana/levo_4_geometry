"""Source data for the Levo 4 geometry calculator.

Everything here traces back to the `data/` folder:

  * `levo4_geometry.csv` / `levo4_geometry_evo.csv` - the published geometry charts.
  * `adjustable_geo_info.png` - manual s11.1, the "Adjustable Geometry Changes" table.
  * `LEVO_G4_USER_MANUAL_ENGLISH.pdf` - specifications table and ss11.1-11.3, 15.4.5-15.4.6.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "DATA_DIR",
    "ModelSpec",
    "PublishedGeometry",
    "LEVO4",
    "LEVO4_EVO",
    "MODELS",
    "HORST_LONG_DELTA",
    "SHOCK_EXT_LONG_DELTA",
    "HEADSET_CUP_DELTAS",
    "FORK_A2C_INTERCEPT",
    "fork_a2c",
    "read_geometry_csv",
]

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

#: Fork axle-to-crown scales 1:1 with travel.  The two published tables give
#: 160 mm -> 577 mm and 180 mm -> 597 mm, so a2c = 417 + travel.
FORK_A2C_INTERCEPT = 417.0


def fork_a2c(travel_mm: float) -> float:
    """Axle-to-crown length for a given fork travel."""
    return FORK_A2C_INTERCEPT + travel_mm


@dataclass(frozen=True)
class PublishedGeometry:
    """One size's column from a published geometry chart, in mm and degrees."""

    reach: float
    stack: float
    head_tube_length: float
    head_tube_angle: float
    seat_tube_angle: float
    chainstay: float
    bb_height: float
    bb_drop: float
    wheelbase: float
    front_center: float
    trail: float
    fork_length: float
    rake: float
    effective_top_tube: float
    standover: float
    seat_tube_length: float
    saddle_height_for_eff_sta: float


@dataclass(frozen=True)
class ModelSpec:
    """A model (Levo 4 or Levo 4 EVO) at size S4."""

    name: str
    short: str
    csv_name: str
    geometry: PublishedGeometry
    stock_fork_travel: float
    fork_travel_options: tuple[float, ...]
    rear_wheel_travel: float
    shock_length: float
    shock_stroke: float
    shock_sag_range: tuple[float, float]  # shock shaft sag, mm
    shock_extension_length: float
    has_shock_extension_chip: bool

    @property
    def leverage_ratio(self) -> float:
        """Average leverage ratio: rear wheel travel per mm of shock stroke."""
        return self.rear_wheel_travel / self.shock_stroke

    @property
    def rear_wheel_sag_range(self) -> tuple[float, float]:
        """Recommended shock sag converted to rear wheel travel, mm."""
        lo, hi = self.shock_sag_range
        return (lo * self.leverage_ratio, hi * self.leverage_ratio)

    @property
    def rear_sag_percent_range(self) -> tuple[float, float]:
        lo, hi = self.rear_wheel_sag_range
        return (100 * lo / self.rear_wheel_travel, 100 * hi / self.rear_wheel_travel)


def _parse(value: str) -> float:
    """Strip the unit or degree suffix off a geometry chart cell."""
    return float(value.strip().rstrip("mm").rstrip("\N{DEGREE SIGN}\xb0?").strip())


def read_geometry_csv(path: Path | str, size: str = "S4") -> dict[str, float]:
    """Read one size column out of a published geometry chart.

    The files are semicolon-delimited and latin-1 encoded (the degree sign in the
    angle rows is not valid UTF-8).
    """
    rows: dict[str, list[str]] = {}
    with open(path, encoding="latin-1") as handle:
        for line in handle:
            cells = [c.strip() for c in line.rstrip("\n").split(";")]
            if len(cells) > 1 and cells[0]:
                rows[cells[0]] = cells[1:]

    sizes = rows["Size"]
    if size not in sizes:
        raise KeyError(f"size {size!r} not in {sizes}")
    column = sizes.index(size)
    return {label: _parse(cells[column]) for label, cells in rows.items() if label != "Size"}


def _published(path: Path) -> PublishedGeometry:
    v = read_geometry_csv(path)
    return PublishedGeometry(
        reach=v["Reach"],
        stack=v["Stack"],
        head_tube_length=v["Headtube Length"],
        head_tube_angle=v["Headtube Angle"],
        seat_tube_angle=v["Seat Tube Angle"],
        chainstay=v["Chainstay Length"],
        bb_height=v["BB Height"],
        bb_drop=v["BB Drop"],
        wheelbase=v["Wheelbase"],
        front_center=v["Front Center"],
        trail=v["Trail"],
        fork_length=v["Fork Length (full)"],
        rake=v["Fork Rake/Offset"],
        effective_top_tube=v["Top-tube Length (horizontal)"],
        standover=v["Bike Standover Height"],
        seat_tube_length=v["Seat Tube Length"],
        saddle_height_for_eff_sta=v["Saddle Height for Effective ST Angle"],
    )


LEVO4 = ModelSpec(
    name="Levo 4",
    short="levo4",
    csv_name="levo4_geometry.csv",
    geometry=_published(DATA_DIR / "levo4_geometry.csv"),
    stock_fork_travel=160.0,
    fork_travel_options=(160.0, 170.0),
    rear_wheel_travel=150.0,
    shock_length=210.0,
    shock_stroke=55.0,
    shock_sag_range=(14.0, 16.5),
    shock_extension_length=91.0,
    has_shock_extension_chip=True,
)

LEVO4_EVO = ModelSpec(
    name="Levo 4 EVO",
    short="levo4_evo",
    csv_name="levo4_geometry_evo.csv",
    geometry=_published(DATA_DIR / "levo4_geometry_evo.csv"),
    stock_fork_travel=180.0,
    fork_travel_options=(170.0, 180.0),
    rear_wheel_travel=170.0,
    shock_length=230.0,
    shock_stroke=62.5,
    shock_sag_range=(17.0, 18.5),
    shock_extension_length=69.0,
    # Manual s11.3: "LEVO 4 MODELS ONLY".  s15.4.6 fits the EVO with a fixed
    # mounting chip instead, because the EVO extension lacks seat tube clearance.
    has_shock_extension_chip=False,
)

MODELS = (LEVO4, LEVO4_EVO)


# --- Manual s11.1, "Adjustable Geometry Changes" ---------------------------
# Deltas from the default setting (Horst short, headset 0 deg, shock ext short).
# Identical for Levo 4 and Levo 4 EVO.  Order: chainstay, BB height, head tube angle.

HORST_LONG_DELTA = {"chainstay": 11.0, "bb_height": -12.0, "head_tube_angle": -0.8}
SHOCK_EXT_LONG_DELTA = {"chainstay": -2.0, "bb_height": 6.0, "head_tube_angle": 0.4}
HEADSET_CUP_DELTAS = {
    -1.0: {"chainstay": 0.0, "bb_height": -2.0, "head_tube_angle": -1.0},
    0.0: {"chainstay": 0.0, "bb_height": 0.0, "head_tube_angle": 0.0},
    +1.0: {"chainstay": 0.0, "bb_height": 2.0, "head_tube_angle": 1.0},
}
