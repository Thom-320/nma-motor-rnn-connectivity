"""Build the canonical English project notebook from versioned cell sources."""

import json
from pathlib import Path


def markdown(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


cells = [
    markdown(
        """# NMA Motor-RNN Connectivity Project

**Question:** When sparse and dense motor RNNs have the same number of trainable recurrent connections, does the difference in held-out reaching performance become smaller?

**Exploratory question:** Are density-related performance differences accompanied by changes in task-evoked neural-manifold dimensionality?

This is the team's canonical notebook. It explains the resolved Q1 baseline and the paired-seed Q2 experiment. It loads committed results by default, so a new collaborator can understand the project immediately without spending Colab compute.
"""
    ),
    code(
        """# Repository-aware setup for local Jupyter and public Google Colab.
import os
import subprocess
import sys
from pathlib import Path

REPOSITORY_URL = "https://github.com/Thom-320/nma-motor-rnn-connectivity.git"

def find_repository_root():
    candidates = [Path.cwd(), Path.cwd().parent]
    return next(
        (path for path in candidates if (path / "src/nma_motor_rnn").exists()),
        None,
    )

repository_root = find_repository_root()
if repository_root is None and "google.colab" in sys.modules:
    checkout = Path("nma-motor-rnn-connectivity")
    if not checkout.exists():
        subprocess.run(["git", "clone", REPOSITORY_URL, str(checkout)], check=True)
    repository_root = checkout.resolve()
    os.chdir(repository_root)
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)

if repository_root is None:
    raise FileNotFoundError("Run Jupyter from the repository root.")

os.chdir(repository_root)
sys.path.insert(0, str((repository_root / "src").resolve()))

import pandas as pd
from IPython.display import Image, display
from nma_motor_rnn.connectivity import (
    ExperimentConfig,
    hypothesis_contrasts,
    pilot_config,
    plot_required_figures,
    primary_config,
    run_experiment,
    run_q1_baseline,
)
"""
    ),
    markdown(
        """## How to use this notebook

Choose one mode and run all cells:

- `view`: load the committed Q1/Q2 results; recommended for onboarding.
- `smoke`: run a tiny end-to-end check in under a minute.
- `pilot`: reproduce the $N=100$, three-seed pilot.
- `primary`: reproduce the $N=200$, eight-seed primary experiment; this is intentionally opt-in.

Set `RUN_Q1=True` only when you want to regenerate the 50-trial baseline in memory.
"""
    ),
    code(
        """RUN_MODE = "view"  # one of: view, smoke, pilot, primary
RUN_Q1 = False

valid_modes = {"view", "smoke", "pilot", "primary"}
if RUN_MODE not in valid_modes:
    raise ValueError(f"RUN_MODE must be one of {sorted(valid_modes)}")
"""
    ),
    markdown(
        """## Q1 — Baseline reaching-network learning

Q1 asks whether the reaching RNN can be trained and whether its loss converges. The left panel is the **online feedback-space loss** used during recurrent updates. It fluctuates because targets and initial states vary and because the network learns inside each trial. The right panel is held-out velocity NMSE evaluated with the fixed motor decoder and no weight updates. Therefore, online loss is a diagnostic—not the primary generalization measure.
"""
    ),
    code(
        """q1_trials = pd.read_csv("results/q1/trial_history.csv")
q1_checkpoints = pd.read_csv("results/q1/checkpoints.csv")
q1_condition = pd.read_csv("results/q1/condition.csv")
display(q1_condition)
display(Image(filename="results/q1/figures/q1_baseline.png"))

if RUN_Q1:
    q1_config = ExperimentConfig(n_units=100, n_training_trials=50)
    regenerated_trials, regenerated_checkpoints, regenerated_summary = run_q1_baseline(
        q1_config, seed=0, p_value=0.10
    )
    display(pd.DataFrame(regenerated_trials).head())
    display(pd.DataFrame([regenerated_summary]))
"""
    ),
    markdown(
        """## Q2 — Recurrent connectivity and held-out learning

Within each seed, density conditions share the underlying random weight matrix, nested masks, input weights, fixed decoder, target schedule, and initial states. Nonzero recurrent weights scale as $g/\\sqrt{pN}$. Evaluation occurs every five trials on 30 balanced held-out trials with learning disabled.

**H1:** final NMSE at $p=0.05$ exceeds the mean at $p=0.10,0.20,0.40$.

**H2:** improvement from $p=0.05$ to $0.20$ exceeds improvement from $p=0.20$ to $0.40$.

$D_{PR}$, $D_{90}$, and their association with performance are exploratory.
"""
    ),
    code(
        """if RUN_MODE == "view":
    checkpoint_df = pd.read_csv("results/primary/checkpoints.csv")
    condition_df = pd.read_csv("results/primary/conditions.csv")
    contrast_df = pd.read_csv("results/primary/hypothesis_contrasts.csv")
    figure_paths = sorted(Path("results/primary/figures").glob("figure*.png"))
else:
    if RUN_MODE == "smoke":
        config = ExperimentConfig(
            n_units=24,
            p_values=(0.10, 0.40),
            n_training_trials=4,
            eval_every=2,
            test_initial_states_per_target=1,
            trial_duration=0.3,
            pulse_duration=0.1,
        )
        seeds = range(1)
    elif RUN_MODE == "pilot":
        config, seeds = pilot_config(), range(3)
    else:
        config, seeds = primary_config(), range(8)

    runtime_output = Path("runtime_results") / RUN_MODE
    checkpoints, conditions, elapsed = run_experiment(
        config, seeds=seeds, output_dir=runtime_output
    )
    checkpoint_df = pd.DataFrame(checkpoints)
    condition_df = pd.DataFrame(conditions)
    contrast_df = (
        pd.DataFrame(hypothesis_contrasts(conditions))
        if set(config.p_values) == {0.05, 0.10, 0.20, 0.40}
        else pd.DataFrame()
    )
    figure_paths = plot_required_figures(
        checkpoints, conditions, runtime_output / "figures"
    )
    print(f"{RUN_MODE} completed in {elapsed:.2f} seconds")

display(condition_df)
if not contrast_df.empty:
    display(contrast_df)
for figure_path in figure_paths:
    display(Image(filename=str(figure_path)))
"""
    ),
    markdown(
        """## Current result and interpretation boundary

In the preregistered $N=200$ experiment, H1 was positive in 8/8 paired seeds: very sparse $p=0.05$ networks had worse final held-out performance than the average moderate/higher-density network. H2 was positive in only 3/8 seeds and is not supported. Participation-ratio dimensionality decreased while performance improved; this association is exploratory and confounded with density.

The defensible conclusion concerns complete architectures in which every existing recurrent connection is plastic. It does **not** establish a critical density, diminishing returns, a causal manifold mechanism, or an effect independent of plasticity budget. The contradictory $N=100$ pilot remains part of the record.

## Team handoff

Before starting work, read `README.md` and `CONTRIBUTING.md`. Use the current GitHub Issue, keep changes focused, run the tests, and request one peer review.
"""
    ),
]

for index, cell in enumerate(cells):
    cell["id"] = f"nma-cell-{index:02d}"


notebook = {
    "cells": cells,
    "metadata": {
        "colab": {"name": "Motor_RNN_Project.ipynb", "provenance": []},
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

output = Path("notebooks/Motor_RNN_Project.ipynb")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
