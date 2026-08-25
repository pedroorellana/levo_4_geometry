"""2-D rigid-body geometry model for the Specialized Levo 4 / Levo 4 EVO.

Frame-local coordinates: bottom bracket at the origin, +x forward, +y up, with the
frame held at its stock (published) attitude.  Every adjustment is expressed as a
change to one of four things:

    fork axle-to-crown   -> `a2c`
    headset cup          -> tilt of the steer axis relative to the frame
    Horst flip chip      -> rear axle offset in frame coordinates
    shock extension chip -> rear axle offset in frame coordinates

The front adjustments never touch the rear axle and the rear adjustments never touch
the steer axis, so they compose without interfering.  All of the interaction between
them falls out of `solve()`, which re-levels the bike (both wheels back on the ground)
and reads every dimension in ground reference.

Stdlib only, so this module runs under a bare `python3` with no virtualenv.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from math import atan2, cos, degrees, hypot, radians, sin, sqrt

__all__ = ["Frame", "Geometry", "rotate", "solve"]


def rotate(point: tuple[float, float], phi_deg: float) -> tuple[float, float]:
    """Rotate a point counter-clockwise (nose-up) by `phi_deg`."""
    c, s = cos(radians(phi_deg)), sin(radians(phi_deg))
    x, y = point
    return (x * c - y * s, x * s + y * c)


@dataclass(frozen=True)
class Frame:
    """A frame skeleton reconstructed from a published geometry table.

    The seat tube is modelled as passing through the bottom bracket, which the
    published effective top-tube lengths confirm to within ~1 mm for both models.
    """

    ht_top: tuple[float, float]  # top of head tube, relative to the BB
    ht_bottom: tuple[float, float]  # bottom of head tube (crown race datum)
    rear_axle: tuple[float, float]  # rear axle, relative to the BB
    standover: tuple[float, float]  # seat tube / top tube junction, relative to the BB
    hta0: float  # steer axis angle at stock attitude, degrees from horizontal
    sta0: float  # seat tube angle at stock attitude
    rake: float  # fork offset, mm
    r_front: float  # front wheel + tyre radius, mm
    r_rear: float  # rear wheel + tyre radius, mm

    @classmethod
    def from_published(
        cls,
        *,
        reach: float,
        stack: float,
        head_tube_length: float,
        head_tube_angle: float,
        seat_tube_angle: float,
        chainstay: float,
        bb_height: float,
        bb_drop: float,
        standover: float,
        rake: float,
    ) -> "Frame":
        """Build the skeleton from the numbers a geometry chart actually publishes.

        `bb_drop` is referenced to the *front* axle: both published tables imply a
        front radius of ~379.5-380 mm that way, and the resulting radius reproduces
        the published trail figures exactly.  The rear radius then follows from the
        chainstay length and BB height.
        """
        a = radians(head_tube_angle)
        ht_top = (reach, stack)
        ht_bottom = (reach + head_tube_length * cos(a), stack - head_tube_length * sin(a))

        r_front = bb_height + bb_drop
        # The rear axle sits at (r_rear - bb_height) above the BB.  For both models the
        # published chainstay and wheelbase put that within a millimetre of zero, i.e.
        # the rear axle is level with the BB.
        r_rear = bb_height
        ry = r_rear - bb_height
        rear_axle = (-sqrt(max(chainstay**2 - ry**2, 0.0)), ry)

        # Standover point: on the seat tube axis at the published standover height.
        # Top tube shape is not in the source data, so this is an approximation.
        so_y = standover - bb_height
        so_x = -so_y / math.tan(radians(seat_tube_angle))

        return cls(
            ht_top=ht_top,
            ht_bottom=ht_bottom,
            rear_axle=rear_axle,
            standover=(so_x, so_y),
            hta0=head_tube_angle,
            sta0=seat_tube_angle,
            rake=rake,
            r_front=r_front,
            r_rear=r_rear,
        )


@dataclass(frozen=True)
class Geometry:
    """Ground-referenced geometry for one configuration."""

    pitch: float  # frame rotation vs stock attitude, + = nose up = slacker
    head_tube_angle: float
    seat_tube_angle: float
    bb_height: float
    bb_drop: float
    reach: float
    stack: float
    chainstay: float
    wheelbase: float
    front_center: float
    trail: float
    mechanical_trail: float
    wheel_flop: float
    effective_top_tube: float
    standover: float

    def delta(self, other: "Geometry") -> dict[str, float]:
        """This geometry minus `other`, field by field."""
        return {
            f: getattr(self, f) - getattr(other, f)
            for f in self.__dataclass_fields__
        }


def solve(
    frame: Frame,
    a2c: float,
    *,
    cup: float = 0.0,
    rear_dx: float = 0.0,
    rear_dy: float = 0.0,
    fork_sag: float = 0.0,
    rear_sag: float = 0.0,
) -> Geometry:
    """Re-level the bike for one configuration and read off its geometry.

    `cup` tilts the steer axis relative to the frame (positive = steeper).
    `rear_dx` / `rear_dy` move the rear axle within the frame.
    `fork_sag` shortens the fork; `rear_sag` raises the rear axle into its travel.
    """
    # --- front: steer axis and front axle, in frame coordinates -------------
    alpha = frame.hta0 + cup
    a = radians(alpha)
    length = a2c - fork_sag
    front = (
        frame.ht_bottom[0] + length * cos(a) + frame.rake * sin(a),
        frame.ht_bottom[1] - length * sin(a) + frame.rake * cos(a),
    )

    # --- rear: axle position, in frame coordinates --------------------------
    rear = (frame.rear_axle[0] + rear_dx, frame.rear_axle[1] + rear_dy + rear_sag)

    # --- re-level: rotate until both axles sit at their wheel radii ---------
    vx, vy = front[0] - rear[0], front[1] - rear[1]
    span = hypot(vx, vy)
    rise = frame.r_front - frame.r_rear
    if abs(rise) > span:
        raise ValueError("axle separation too small to place both wheels on the ground")
    pitch = degrees(math.asin(rise / span)) - degrees(atan2(vy, vx))

    bb_height = frame.r_rear - rotate(rear, pitch)[1]

    ht_top = rotate(frame.ht_top, pitch)
    front_w = rotate(front, pitch)
    rear_w = rotate(rear, pitch)
    so_w = rotate(frame.standover, pitch)

    # A nose-up rotation tips the head tube toward horizontal, so the ground-
    # referenced angle is the frame-local angle *minus* the pitch.
    hta = alpha - pitch
    sta = frame.sta0 - pitch

    trail = (frame.r_front * cos(radians(hta)) - frame.rake) / sin(radians(hta))

    return Geometry(
        pitch=pitch,
        head_tube_angle=hta,
        seat_tube_angle=sta,
        bb_height=bb_height,
        bb_drop=frame.r_front - bb_height,
        reach=ht_top[0],
        stack=ht_top[1],
        chainstay=hypot(*rear_w),
        wheelbase=front_w[0] - rear_w[0],
        front_center=hypot(*front_w),
        trail=trail,
        mechanical_trail=trail * sin(radians(hta)),
        wheel_flop=trail * sin(radians(hta)) * cos(radians(hta)),
        effective_top_tube=ht_top[0] + ht_top[1] / math.tan(radians(sta)),
        standover=so_w[1] + bb_height,
    )
