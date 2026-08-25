"""Write the full configuration tables out: `python3 -m levo_geo.export`.

Writes the four CSVs in `output/` and refreshes the static tables in `README.md`.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .calibrate import calibrate
from .configs import DEFAULT_FORK_SAG_FRACTION, GEOMETRY_FIELDS, build_rows
from .data import MODELS

__all__ = [
    "COLUMNS",
    "MARKDOWN_COLUMNS",
    "write_csvs",
    "render_table",
    "render_markdown",
    "update_readme",
]

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


#: Row key -> README column label, in report order.  Matches the notebook's tables.
#: A dagger marks a column Specialized does not publish for any adjustment.
MARKDOWN_COLUMNS = {
    "fork_travel": "Fork",
    "horst_pivot": "Horst",
    "headset_cup": "Cup",
    "shock_extension": "Shock ext",
    "head_tube_angle": "HTA",
    "seat_tube_angle": "STA †",
    "bb_height": "BB height",
    "bb_drop": "BB drop †",
    "reach": "Reach †",
    "stack": "Stack †",
    "chainstay": "CS",
    "wheelbase": "WB †",
    "front_center": "FC †",
    "trail": "Trail †",
    "mechanical_trail": "Mech trail †",
    "wheel_flop": "Flop †",
    "effective_top_tube": "ETT †",
    "standover": "Standover †*",
}

#: The four configuration choices are left-aligned; every geometry column is a number.
_TEXT_COLUMNS = ("horst_pivot", "headset_cup", "shock_extension")

README_BEGIN = "<!-- BEGIN GENERATED: static-tables -->"
README_END = "<!-- END GENERATED: static-tables -->"

_README_FOOTNOTE = (
    "† not published by Specialized for any adjustment. "
    "\\* standover is indicative only — see [Assumptions and limitations]"
    "(#assumptions-and-limitations)."
)


def _cell(column: str, row: dict) -> str:
    if column == "fork_travel":
        return f"{row[column]:.0f}"
    return _format(column, row[column])


def render_table(rows: list[dict]) -> str:
    """One model's configurations as a GitHub markdown table."""
    header = ["Stock", *MARKDOWN_COLUMNS.values()]
    rule = ["---"] + [
        "---" if c in _TEXT_COLUMNS else "---:" for c in MARKDOWN_COLUMNS
    ]
    lines = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join(rule) + "|",
    ]
    for row in rows:
        cells = ["**stock**" if row["is_stock"] else ""]
        cells += [_cell(c, row) for c in MARKDOWN_COLUMNS]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render_markdown(*, fork_sag_fraction: float = DEFAULT_FORK_SAG_FRACTION) -> str:
    """The static tables for both models, as the README block between the markers."""
    blocks = []
    for model in MODELS:
        rows = build_rows(
            model, calibrate(model), sagged=False, fork_sag_fraction=fork_sag_fraction
        )
        blocks.append(
            f"### {model.name} — all {len(rows)} configurations (mm and degrees)\n\n"
            + render_table(rows)
        )
    return "\n\n".join(blocks) + "\n\n" + _README_FOOTNOTE


def update_readme(
    path: Path | str = Path(__file__).resolve().parent.parent / "README.md",
    *,
    fork_sag_fraction: float = DEFAULT_FORK_SAG_FRACTION,
) -> Path:
    """Rewrite the generated table block in the README in place.  Returns the path."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    start, end = text.find(README_BEGIN), text.find(README_END)
    if start < 0 or end < 0:
        raise ValueError(
            f"{path} has no {README_BEGIN} / {README_END} block to write into"
        )
    body = render_markdown(fork_sag_fraction=fork_sag_fraction)
    path.write_text(
        text[: start + len(README_BEGIN)] + f"\n\n{body}\n\n" + text[end:],
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    for path in write_csvs():
        print(f"wrote {path}")
    print(f"wrote {update_readme()}")
