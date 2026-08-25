"""Run the model's self-test: `python3 -m levo_geo`."""

from .configs import self_test

raise SystemExit(0 if self_test() else 1)
