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
python3 -m levo_geo.export   # (re)write output/*.csv and the tables in this README
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
  export.py         CSV + README table writer
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

## Full results

Static, unweighted numbers — the same convention as the catalogue chart, and not the geometry
anyone actually rides. The sagged tables are in [output/](output/) and the notebook. Regenerate this
block with `python3 -m levo_geo.export`.

<!-- BEGIN GENERATED: static-tables -->

### Levo 4 — all 24 configurations (mm and degrees)

| Stock | Fork | Horst | Cup | Shock ext | HTA | STA † | BB height | BB drop † | Reach † | Stack † | CS | WB † | FC † | Trail † | Mech trail † | Flop † | ETT † | Standover †* |
|---|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|  | 160 | Short | -1 deg | Short | 63.50 | 77.30 | 347.7 | 31.8 | 483.4 | 635.5 | 435.0 | 1265.5 | 831.6 | 139.8 | 125.1 | 55.8 | 626.2 | 751.2 |
|  | 160 | Short | -1 deg | Long | 63.91 | 77.71 | 353.6 | 25.9 | 487.9 | 632.0 | 433.0 | 1263.7 | 831.6 | 136.6 | 122.7 | 53.9 | 625.3 | 757.8 |
| **stock** | 160 | Short | 0 deg | Short | 64.50 | 77.00 | 350.0 | 29.5 | 480.0 | 638.0 | 435.0 | 1254.0 | 820.0 | 132.0 | 119.1 | 51.3 | 627.0 | 753.0 |
|  | 160 | Short | 0 deg | Long | 64.91 | 77.41 | 355.9 | 23.6 | 484.6 | 634.5 | 433.0 | 1252.2 | 820.0 | 128.8 | 116.7 | 49.5 | 626.0 | 759.6 |
|  | 160 | Short | +1 deg | Short | 65.50 | 76.71 | 352.2 | 27.3 | 476.7 | 640.5 | 435.0 | 1242.5 | 808.4 | 124.3 | 113.1 | 46.9 | 627.7 | 754.7 |
|  | 160 | Short | +1 deg | Long | 65.92 | 77.12 | 358.1 | 21.4 | 481.4 | 637.0 | 433.0 | 1240.6 | 808.4 | 121.2 | 110.6 | 45.1 | 626.7 | 761.3 |
|  | 160 | Long | -1 deg | Short | 62.68 | 76.48 | 335.8 | 43.7 | 474.2 | 642.3 | 446.0 | 1275.7 | 831.6 | 146.3 | 129.9 | 59.6 | 628.3 | 737.9 |
|  | 160 | Long | -1 deg | Long | 63.08 | 76.89 | 341.7 | 37.8 | 478.7 | 639.0 | 443.6 | 1273.8 | 831.6 | 143.1 | 127.6 | 57.7 | 627.3 | 744.5 |
|  | 160 | Long | 0 deg | Short | 63.67 | 76.17 | 338.2 | 41.3 | 470.7 | 644.9 | 446.0 | 1264.3 | 820.0 | 138.4 | 124.1 | 55.0 | 629.2 | 739.8 |
|  | 160 | Long | 0 deg | Long | 64.08 | 76.58 | 344.0 | 35.5 | 475.3 | 641.5 | 443.6 | 1262.3 | 820.0 | 135.2 | 121.6 | 53.2 | 628.1 | 746.3 |
|  | 160 | Long | +1 deg | Short | 64.67 | 75.87 | 340.5 | 39.0 | 467.4 | 647.3 | 446.0 | 1252.9 | 808.4 | 130.7 | 118.1 | 50.5 | 630.0 | 741.6 |
|  | 160 | Long | +1 deg | Long | 65.08 | 76.29 | 346.3 | 33.2 | 472.0 | 643.9 | 443.6 | 1250.8 | 808.4 | 127.5 | 115.7 | 48.7 | 628.9 | 748.1 |
|  | 170 | Short | -1 deg | Short | 63.10 | 76.90 | 350.8 | 28.7 | 478.9 | 638.9 | 435.0 | 1269.8 | 835.7 | 143.0 | 127.5 | 57.7 | 627.3 | 753.6 |
|  | 170 | Short | -1 deg | Long | 63.50 | 77.31 | 356.7 | 22.8 | 483.4 | 635.4 | 433.0 | 1267.9 | 835.7 | 139.7 | 125.1 | 55.8 | 626.2 | 760.2 |
|  | 170 | Short | 0 deg | Short | 64.09 | 76.59 | 353.1 | 26.4 | 475.4 | 641.4 | 435.0 | 1258.1 | 824.0 | 135.2 | 121.6 | 53.1 | 628.1 | 755.4 |
|  | 170 | Short | 0 deg | Long | 64.50 | 77.00 | 359.0 | 20.5 | 480.0 | 638.0 | 433.0 | 1256.2 | 824.0 | 132.0 | 119.1 | 51.3 | 627.0 | 762.0 |
|  | 170 | Short | +1 deg | Short | 65.08 | 76.29 | 355.4 | 24.1 | 472.0 | 643.9 | 435.0 | 1246.4 | 812.3 | 127.5 | 115.7 | 48.7 | 628.8 | 757.2 |
|  | 170 | Short | +1 deg | Long | 65.50 | 76.70 | 361.3 | 18.2 | 476.7 | 640.5 | 433.0 | 1244.5 | 812.3 | 124.4 | 113.2 | 46.9 | 627.8 | 763.8 |
|  | 170 | Long | -1 deg | Short | 62.28 | 76.08 | 338.9 | 40.6 | 469.7 | 645.6 | 446.0 | 1280.1 | 835.7 | 149.4 | 132.3 | 61.5 | 629.4 | 740.4 |
|  | 170 | Long | -1 deg | Long | 62.68 | 76.49 | 344.8 | 34.7 | 474.3 | 642.3 | 443.6 | 1278.1 | 835.7 | 146.2 | 129.9 | 59.6 | 628.3 | 746.9 |
|  | 170 | Long | 0 deg | Short | 63.27 | 75.77 | 341.3 | 38.2 | 466.2 | 648.2 | 446.0 | 1268.6 | 824.0 | 141.6 | 126.5 | 56.9 | 630.3 | 742.3 |
|  | 170 | Long | 0 deg | Long | 63.67 | 76.17 | 347.2 | 32.3 | 470.8 | 644.9 | 443.6 | 1266.5 | 824.0 | 138.4 | 124.1 | 55.0 | 629.2 | 748.8 |
|  | 170 | Long | +1 deg | Short | 64.26 | 75.46 | 343.7 | 35.8 | 462.7 | 650.7 | 446.0 | 1257.0 | 812.3 | 133.9 | 120.6 | 52.4 | 631.1 | 744.1 |
|  | 170 | Long | +1 deg | Long | 64.67 | 75.87 | 349.5 | 30.0 | 467.4 | 647.3 | 443.6 | 1254.9 | 812.3 | 130.7 | 118.2 | 50.6 | 630.0 | 750.6 |

### Levo 4 EVO — all 12 configurations (mm and degrees)

| Stock | Fork | Horst | Cup | Shock ext | HTA | STA † | BB height | BB drop † | Reach † | Stack † | CS | WB † | FC † | Trail † | Mech trail † | Flop † | ETT † | Standover †* |
|---|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|  | 170 | Short | -1 deg | n/a | 63.00 | 76.72 | 350.5 | 29.5 | 478.1 | 640.0 | 435.0 | 1270.6 | 835.8 | 143.7 | 128.0 | 58.1 | 628.1 | 758.8 |
|  | 170 | Short | 0 deg | n/a | 64.01 | 76.41 | 352.9 | 27.1 | 474.6 | 642.6 | 435.0 | 1258.8 | 823.9 | 135.8 | 122.1 | 53.5 | 628.9 | 760.6 |
|  | 170 | Short | +1 deg | n/a | 65.02 | 76.10 | 355.2 | 24.8 | 471.2 | 645.2 | 435.0 | 1246.9 | 812.0 | 128.0 | 116.1 | 49.0 | 629.7 | 762.4 |
|  | 170 | Long | -1 deg | n/a | 62.18 | 75.90 | 338.5 | 41.5 | 468.9 | 646.8 | 446.0 | 1280.7 | 835.8 | 150.3 | 132.9 | 62.0 | 630.3 | 745.4 |
|  | 170 | Long | 0 deg | n/a | 63.18 | 75.58 | 341.0 | 39.0 | 465.3 | 649.4 | 446.0 | 1269.0 | 823.9 | 142.3 | 127.0 | 57.3 | 631.2 | 747.3 |
|  | 170 | Long | +1 deg | n/a | 64.18 | 75.27 | 343.4 | 36.6 | 461.7 | 652.0 | 446.0 | 1257.3 | 812.0 | 134.5 | 121.0 | 52.7 | 632.0 | 749.1 |
|  | 180 | Short | -1 deg | n/a | 62.60 | 76.32 | 353.6 | 26.4 | 473.6 | 643.3 | 435.0 | 1275.0 | 840.0 | 146.9 | 130.4 | 60.0 | 629.1 | 761.1 |
| **stock** | 180 | Short | 0 deg | n/a | 63.60 | 76.00 | 356.0 | 24.0 | 470.0 | 646.0 | 435.0 | 1263.0 | 828.0 | 139.0 | 124.5 | 55.4 | 630.0 | 763.0 |
|  | 180 | Short | +1 deg | n/a | 64.60 | 75.69 | 358.4 | 21.6 | 466.5 | 648.6 | 435.0 | 1251.0 | 815.9 | 131.2 | 118.5 | 50.8 | 630.9 | 764.8 |
|  | 180 | Long | -1 deg | n/a | 61.78 | 75.51 | 341.6 | 38.4 | 464.4 | 650.0 | 446.0 | 1285.3 | 840.0 | 153.4 | 135.2 | 63.9 | 631.4 | 747.7 |
|  | 180 | Long | 0 deg | n/a | 62.78 | 75.18 | 344.1 | 35.9 | 460.7 | 652.7 | 446.0 | 1273.4 | 828.0 | 145.5 | 129.4 | 59.2 | 632.3 | 749.7 |
|  | 180 | Long | +1 deg | n/a | 63.77 | 74.86 | 346.6 | 33.4 | 457.1 | 655.2 | 446.0 | 1261.5 | 815.9 | 137.6 | 123.5 | 54.6 | 633.2 | 751.5 |

† not published by Specialized for any adjustment. \* standover is indicative only — see [Assumptions and limitations](#assumptions-and-limitations).

<!-- END GENERATED: static-tables -->

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
