"""Robustness grid (R1-R5) for the density / plasticity-budget result.

Every network is trained for 200 trials.  The first 60 training trials and the
held-out test set are drawn exactly as in the committed 60-trial primary run
(:func:`make_extended_shared_randomness`), so the trial-60 checkpoint of the
N=200, seeds 0-7 arms reproduces ``results/primary`` and
``results/equal_plasticity``.

An *arm* is one way of building the networks of a seed:

``primary``   every existing recurrent edge is trainable (as in Q2);
``control``   every density gets the p=0.05 trainable-edge budget (as in the
              equal-plasticity control);
``control_random`` the same budget, but a random subset of each structural
              mask is trainable instead of the p=0.05 edges (session 2);
``*_gain``    the same, with every initial recurrent matrix rescaled to the
              spectral radius of that seed's p=0.05 network (R2);
``frozen``    the R3 frozen-drive ablation (see :func:`frozen_drive_weights`);
``frozen_unmatched`` the R3 variant whose trainable edges keep the p=0.05
              scale, so total gain grows with f (session 2).  Its f = 0 cell
              is the ``frozen`` arm's f = 0 network and is not run again.

Results are written per (arm, N, seed, condition) so that the grid is
resumable and can be split across machines; ``collect`` merges them.

Command line (also used by the Kaggle shards)::

    python -m nma_motor_rnn.robustness run --arms primary,control --n-units 200 \
        --seeds 0-7 --out results/robustness --workers 4
    python -m nma_motor_rnn.robustness collect --out results/robustness
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Sequence

import numpy as np

from .connectivity import (
    ExperimentConfig,
    frozen_drive_weights,
    gain_match_scale,
    initial_recurrent_weights,
    make_equal_plasticity_masks,
    make_random_subset_plasticity_masks,
    make_extended_shared_randomness,
    spectral_radius,
    train_condition,
    write_rows_csv,
)

P_VALUES = (0.05, 0.10, 0.20, 0.40)
BASE_TRIALS = 60
TOTAL_TRIALS = 200
EVAL_EVERY = 10
REPORT_CHECKPOINTS = (60, 100, 150, 200)
ARMS = (
    "primary",
    "control",
    "primary_gain",
    "control_gain",
    "frozen",
    "control_random",
    "frozen_unmatched",
)
FROZEN_ARMS = ("frozen", "frozen_unmatched")

# R3 factorial: frozen-drive fraction f x structural density, plastic set = p 0.05.
# f = 0 is the p = 0.05 network for every density, so it is run once (p = 0.40).
R3_FRACTIONS = (0.0, 0.5, 0.75, 0.875)
R3_DENSITIES = (0.10, 0.20, 0.40)


@dataclass(frozen=True)
class Condition:
    arm: str
    p_value: float
    frozen_fraction: float = float("nan")

    @property
    def label(self) -> str:
        if self.arm in FROZEN_ARMS:
            return f"p{self.p_value:.2f}_f{self.frozen_fraction:.3f}"
        return f"p{self.p_value:.2f}"


def robustness_config(n_units: int = 200) -> ExperimentConfig:
    return replace(
        ExperimentConfig(),
        n_units=int(n_units),
        n_training_trials=TOTAL_TRIALS,
        eval_every=EVAL_EVERY,
    )


def arm_conditions(arm: str) -> list[Condition]:
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}; expected one of {ARMS}")
    if arm not in FROZEN_ARMS:
        return [Condition(arm, p) for p in P_VALUES]
    conditions = [Condition(arm, 0.40, 0.0)] if arm == "frozen" else []
    for p_value in R3_DENSITIES:
        for fraction in R3_FRACTIONS[1:]:
            conditions.append(Condition(arm, p_value, fraction))
    return conditions


def build_network_inputs(
    config: ExperimentConfig,
    shared,
    condition: Condition,
) -> tuple[np.ndarray | None, np.ndarray | None, float]:
    """Return ``(plastic_mask, initial_weights, gain_scale)`` for one condition."""
    arm, p_value = condition.arm, condition.p_value
    if arm in FROZEN_ARMS:
        weights, plastic = frozen_drive_weights(
            config, shared, p_value, condition.frozen_fraction, p_plastic=P_VALUES[0],
            match_total_gain=(arm == "frozen"),
        )
        return plastic, weights, 1.0
    plastic = None
    if arm == "control_random":
        plastic = make_random_subset_plasticity_masks(shared, P_VALUES)[float(p_value)]
    elif arm.startswith("control"):
        plastic = make_equal_plasticity_masks(shared, P_VALUES)[float(p_value)]
    if not arm.endswith("_gain"):
        return plastic, None, 1.0
    reference = spectral_radius(initial_recurrent_weights(config, shared, P_VALUES[0]))
    weights = initial_recurrent_weights(config, shared, p_value)
    scale = 1.0 if p_value == P_VALUES[0] else gain_match_scale(weights, reference)
    return plastic, weights * scale, scale


def _raw_stem(out: Path, arm: str, n_units: int, seed: int, condition: Condition) -> Path:
    return out / "raw" / f"{arm}_N{n_units}" / f"seed{seed:02d}_{condition.label}"


def run_task(task: tuple[str, int, int, str, Condition]) -> tuple[str, float]:
    """Train one (arm, N, seed, condition) network and write its two CSVs."""
    out_text, n_units, seed, arm, condition = task
    stem = _raw_stem(Path(out_text), arm, n_units, seed, condition)
    summary_path = stem.with_name(stem.name + "_summary.csv")
    if summary_path.exists():
        return str(summary_path), 0.0
    start = time.perf_counter()
    config = robustness_config(n_units)
    shared = make_extended_shared_randomness(config, seed, BASE_TRIALS)
    plastic, weights, scale = build_network_inputs(config, shared, condition)
    rows, summary = train_condition(
        config, shared, condition.p_value, plastic_mask=plastic, initial_weights=weights
    )
    extra = {
        "arm": arm,
        "n_units": n_units,
        "condition": condition.label,
        "frozen_fraction": condition.frozen_fraction,
        "gain_scale": scale,
    }
    rows = [{**extra, **row} for row in rows]
    elapsed = time.perf_counter() - start
    summary = {**extra, **summary, "elapsed_seconds": elapsed}
    stem.parent.mkdir(parents=True, exist_ok=True)
    write_rows_csv(stem.with_name(stem.name + "_checkpoints.csv"), rows)
    tmp = summary_path.with_suffix(".tmp")
    write_rows_csv(tmp, [summary])
    os.replace(tmp, summary_path)  # summary marks the task as done
    return str(summary_path), elapsed


def make_tasks(
    out: str | Path, arms: Sequence[str], n_units: int, seeds: Sequence[int]
) -> list[tuple[str, int, int, str, Condition]]:
    tasks = []
    for arm in arms:
        for seed in seeds:
            for condition in arm_conditions(arm):
                tasks.append((str(out), int(n_units), int(seed), arm, condition))
    return tasks


def run_tasks(tasks: list, workers: int = 1) -> list[tuple[str, float]]:
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    if workers <= 1:
        return [_log(run_task(task)) for task in tasks]
    from multiprocessing import get_context

    with get_context("spawn").Pool(workers) as pool:
        return [_log(result) for result in pool.imap_unordered(run_task, tasks)]


def _log(result: tuple[str, float]) -> tuple[str, float]:
    path = Path(result[0])
    print(f"{result[1]:8.1f}s  {path.parent.name}/{path.name}", flush=True)
    return result


def collect(out: str | Path) -> list[Path]:
    """Merge raw per-condition CSVs into ``<out>/<arm>_N<N>/{checkpoints,conditions}.csv``."""
    out = Path(out)
    written = []
    for group in sorted((out / "raw").iterdir()):
        if not group.is_dir():
            continue
        checkpoints, conditions = [], []
        for summary_path in sorted(group.glob("*_summary.csv")):
            conditions.extend(_read(summary_path))
            checkpoints.extend(_read(summary_path.with_name(
                summary_path.name.replace("_summary.csv", "_checkpoints.csv"))))
        key = lambda row: (int(row["seed"]), row["condition"])
        conditions.sort(key=key)
        checkpoints.sort(key=lambda row: (*key(row), int(row["checkpoint_trial"])))
        target = out / group.name
        target.mkdir(parents=True, exist_ok=True)
        write_rows_csv(target / "conditions.csv", conditions)
        write_rows_csv(target / "checkpoints.csv", checkpoints)
        config = asdict(robustness_config(int(conditions[0]["n_units"])))
        config.update(
            p_values=list(P_VALUES),
            base_trials=BASE_TRIALS,
            arm=conditions[0]["arm"],
            seeds=sorted({int(row["seed"]) for row in conditions}),
            report_checkpoints=list(REPORT_CHECKPOINTS),
            core_seconds=float(sum(float(row["elapsed_seconds"]) for row in conditions)),
        )
        (target / "config.json").write_text(json.dumps(config, indent=2) + "\n")
        written.append(target)
    return written


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_seeds(text: str) -> list[int]:
    seeds: list[int] = []
    for part in text.split(","):
        if "-" in part:
            low, high = part.split("-")
            seeds.extend(range(int(low), int(high) + 1))
        elif part:
            seeds.append(int(part))
    return seeds


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--arms", required=True)
    run.add_argument("--n-units", type=int, default=200)
    run.add_argument("--seeds", default="0-7")
    run.add_argument("--out", default="results/robustness")
    run.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    gather = sub.add_parser("collect")
    gather.add_argument("--out", default="results/robustness")
    args = parser.parse_args(argv)
    if args.command == "collect":
        for path in collect(args.out):
            print(path)
        return
    tasks = make_tasks(args.out, args.arms.split(","), args.n_units, parse_seeds(args.seeds))
    start = time.perf_counter()
    run_tasks(tasks, args.workers)
    print(f"{len(tasks)} tasks finished in {time.perf_counter() - start:.1f}s wall")


if __name__ == "__main__":
    main()
