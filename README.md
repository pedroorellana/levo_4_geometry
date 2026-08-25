# Levo 4 / Levo 4 EVO geometry calculator — size S4

Specialized publishes **three** numbers per adjustment: chainstay length, BB height and head tube
angle (manual §11.1). But every one of these adjustments re-levels the whole bike, so reach, stack,
seat angle, wheelbase, front centre, trail and effective top tube all move too — and none of those
are published. Fork length isn't in that table at all.

This project reconstructs the frame from the published geometry charts, calibrates each adjustment
against the manual, and produces the **complete geometry sheet for all 36 legal configurations** of
an S4 Levo 4 and S4 Levo 4 EVO — including the columns Specialized leaves out — plus rear
suspension travel and the resulting sagged (riding) geometry.

| | Levo 4 | Levo 4 EVO |
|---|---|---|
| Fork | 160 / 170 mm | 170 / 180 mm |
| Horst pivot flip chip | Short / Long | Short / Long |
| Headset cup | −1° / 0° / +1° | −1° / 0° / +1° |
| Shock extension flip chip | Short / Long | — (Levo 4 only) |
| **Combinations** | **24** | **12** |

The EVO has no shock-extension flip chip: manual §11.3 is headed "LEVO 4 MODELS ONLY", and §15.4.6
fits the EVO with a fixed mounting chip instead, because the EVO extension lacks seat-tube clearance.

## Quick start

The `levo_geo` package is **stdlib-only** — no virtualenv needed:

```sh
python3 -m levo_geo          # run the full self-test
python3 -m levo_geo.export   # (re)write output/*.csv
```

```python
from levo_geo import LEVO4, build_rows

for row in build_rows(LEVO4):
    print(row["fork_travel"], row["horst_pivot"], row["reach"], row["head_tube_angle"])
```

The notebook is the only thing that needs third-party packages:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/jupyter lab notebooks/levo4_s4_geometry.ipynb
```

> This machine has no system `pip`, `uv`, `conda` or `node`. Use `python3 -m venv` and call
> `.venv/bin/python` / `.venv/bin/jupyter` directly.

## Layout

```
levo_geo/           stdlib-only calculator
  frame.py          2-D rigid-body model + the re-levelling solve
  data.py           source data: geometry charts, manual specs, published deltas
  calibrate.py      fits each adjustment to the manual's published deltas
  configs.py        enumerates the 24 + 12 combinations; self_test()
  export.py         CSV writer
notebooks/
  levo4_s4_geometry.ipynb   the analysis, executed with all outputs
output/             36 configurations x 14 geometry columns, static and at sag
data/               source material (see below)
```

* [levo_geo/frame.py](levo_geo/frame.py) — [data.py](levo_geo/data.py) —
  [calibrate.py](levo_geo/calibrate.py) — [configs.py](levo_geo/configs.py) —
  [export.py](levo_geo/export.py)
* [notebooks/levo4_s4_geometry.ipynb](notebooks/levo4_s4_geometry.ipynb)

## Output

Four CSVs in [output/](output/) — a static and a sagged table per model:

| File | Rows |
|---|---|
| [levo4_s4_static.csv](output/levo4_s4_static.csv) | 24 |
| [levo4_s4_sag.csv](output/levo4_s4_sag.csv) | 24 |
| [levo4_evo_s4_static.csv](output/levo4_evo_s4_static.csv) | 12 |
| [levo4_evo_s4_sag.csv](output/levo4_evo_s4_sag.csv) | 12 |

Columns: the four configuration choices and `fork_a2c` / `is_stock`, then the 14 geometry columns
(`head_tube_angle`, `seat_tube_angle`, `bb_height`, `bb_drop`, `reach`, `stack`, `chainstay`,
`wheelbase`, `front_center`, `trail`, `mechanical_trail`, `wheel_flop`, `effective_top_tube`,
`standover`), then rear suspension (`rear_wheel_travel`, `shock`, `leverage_ratio`,
`rear_sag_mm_range`, `rear_sag_pct_range`) and the sag actually applied.

Values are reported as `published baseline + modelled delta`, so **the stock row is identical to the
catalogue chart** and every other row differs from it by a physically derived amount. That keeps the
sub-millimetre rounding slop in the published (and over-determined) chart out of the other 35 rows.

## What the manual doesn't tell you

Each adjustment applied on its own to a stock Levo 4. The first three columns are what Specialized
publishes; **bold** is what also changes.

| | CS | BB | HTA | **Reach** | **Stack** | **STA** | **WB** | **Trail** |
|---|---|---|---|---|---|---|---|---|
| Fork 160→170 mm | 0 | +3.1 | −0.41 | **−4.6** | **+3.4** | **−0.41** | **+4.1** | **+3.2** |
| Horst pivot Long | +11 | −11.8 | −0.83 | **−9.3** | **+6.9** | **−0.83** | **+10.3** | **+6.4** |
| Headset cup −1° | 0 | −2.3 | −1.00 | **+3.4** | **−2.5** | **+0.30** | **+11.5** | **+7.8** |
| Shock extension Long | −2 | +5.9 | +0.41 | **+4.6** | **−3.5** | **+0.41** | **−1.8** | **−3.2** |

* **The Horst pivot chip is a reach adjustment** — 9.3 mm, more than a stem size. The manual
  describes it purely as a chainstay/BB change.
* **The headset cup is the biggest wheelbase and trail lever on the bike** (±11.5 mm / ±8 mm), which
  is where most of its change in steering feel actually comes from. It also moves reach the
  *opposite* way to intuition: the −1° cup slackens the head angle **and lengthens** reach.
* **Fork length appears nowhere in the manual's table**, yet it moves seven dimensions.
* **Every** adjustment moves the seat tube angle, which the manual never mentions.
* Sitting on the bike dwarfs all of it: at recommended sag the Levo 4 loses ~0.9° of head angle,
  **35 mm of BB height** and 10 mm of reach (1.1° / 40 mm / 12.5 mm on the EVO).

## Method

A 2-D rigid-body model. Frame-local coordinates: bottom bracket at the origin, +x forward, +y up.

1. **Frame skeleton** — head tube top at `(reach, stack)`, head tube bottom one head-tube-length down
   the steer axis, seat tube through the BB, rear axle placed by the chainstay length.
2. **Fork** — `axle = ht_bottom + a2c·(cos α, −sin α) + rake·(sin α, cos α)`. Axle-to-crown tracks
   travel 1:1: the charts give 160 → 577 and 180 → 597, so `a2c = 417 + travel`.
3. **Re-level** — rotate the whole assembly until both axles sit at their wheel radii again, then read
   every dimension in ground reference. A nose-up rotation tips the head tube toward horizontal, so
   ground-referenced angles are the frame-local angle *minus* the pitch.

Each adjustment touches exactly one input — fork length sets `a2c`, the headset cup tilts the steer
axis within the frame, the two flip chips move the rear axle within the frame — so front and rear
adjustments never interfere, and **all** of the interaction between them falls out of the re-levelling
step rather than from adding the manual's deltas together.

The flip chips are calibrated as a rigid rear-axle offset `(dx, dy)`: two free parameters against
**three** published targets, so the residual is a real test rather than a curve fit.

## Verification

`python3 -m levo_geo` checks every claim:

* Flip-chip fits reproduce all three published deltas — worst residual **0.19 mm**, angles inside 0.03°.
* The Horst offset, fitted **independently** from each model's own chart, agrees to 0.012 mm —
  confirming that the two bikes share a rear triangle.
* Both stock rows reproduce all 12 published columns of their charts exactly.
* Every single-adjustment row reproduces the manual's delta table.
* Cross-check: the EVO chart is the Levo 4 frame rotated 0.9° nose-up — rotating (480, 638) gives
  reach 469.9 / stack 645.5 against a published 470 / 646. Nothing in that check is fitted.
* Configuration counts are 24 and 12, and every trend runs the right way.

The reconstruction also predicts dimensions that were never inputs: trail comes out at 131.9 / 138.8
against a published 132 / 139, front centre 819.1 / 827.3 against 820 / 828, effective top tube
627.2 / 630.8 against 627 / 630. Getting trail right pins the front wheel radius at ≈380 mm and shows
that **BB drop on these mullet bikes is measured to the front axle**, not the mid-point of the two.

To re-run the notebook end to end:

```sh
.venv/bin/jupyter nbconvert --execute --to notebook --inplace notebooks/levo4_s4_geometry.ipynb
```

## Assumptions and limitations

* **Rear wheel travel is held constant** at the published 150 / 170 mm for every configuration.
  Specialized publishes no travel change for either flip chip, and the source data has no linkage
  pivot coordinates, so a per-configuration travel or leverage-progression figure cannot be derived
  from it. The chips certainly change static ride height — that *is* modelled — and moving the Horst
  pivot must perturb the leverage curve somewhat, but by how much is not knowable here and is not
  guessed at.
* **Headset cup convention.** The cup has one free parameter and the manual gives two targets, so it
  can't hit both. This calculator anchors to the manual's headline ±1.0° head angle (implying a
  physically ≈1.3° cup and ±2.2–2.4 mm of BB against the manual's rounded ±2 mm). A literal 1° cup
  would instead give a net ±0.77° and ±1.8 mm.
* **Combining the two Levo 4 chips** assumes their rear-axle offsets add. Each is verified against the
  manual on its own; the manual gives no combined figure to check the pair against.
* **Standover is indicative only** — top tube shape isn't in the source data, so it's modelled as a
  fixed point on the seat tube; cross-checking that between the two charts disagrees by ~5 mm. Every
  other column is reconstructed from published frame dimensions.
* **Fork sag of 15%** is an assumption; Specialized publishes a rear sag range but no fork figure.
  Change `FORK_SAG` in the notebook, or pass `fork_sag_fraction=` to `build_rows()`.
* The EVO geometry chart says BB height **356 mm**; the manual's §11.1 table says 355 mm. The chart
  is used here.
* Every configuration listed is inside Specialized's stated 160–180 mm fork range for both frames.
  Manual §11.1 warns that changing fork length or flip chip position alters BB height and head angle
  "which can have negative effects on the bicycle's handling characteristics and ride quality", and
  to consult a dealer before modifying. These numbers are an analysis, not a recommendation.

## Source data

Everything traces back to [data/](data/):

| File | Used for |
|---|---|
| [levo4_geometry.csv](data/levo4_geometry.csv) | Levo 4 published geometry chart (S4 column) |
| [levo4_geometry_evo.csv](data/levo4_geometry_evo.csv) | Levo 4 EVO published geometry chart (S4 column) |
| [adjustable_geo_info.png](data/adjustable_geo_info.png) | manual §11.1 "Adjustable Geometry Changes" |
| [LEVO_G4_USER_MANUAL_ENGLISH.pdf](data/LEVO_G4_USER_MANUAL_ENGLISH.pdf) | specifications table, §§11.1–11.3, §§15.4.5–15.4.6 |

The two CSVs are semicolon-delimited and latin-1 encoded — the degree sign in the angle rows is not
valid UTF-8, which is why [data.py](levo_geo/data.py) reads them explicitly as latin-1.
