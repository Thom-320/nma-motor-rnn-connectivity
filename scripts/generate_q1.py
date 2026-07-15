"""Generate the committed 50-trial Q1 baseline artifacts."""

import json
from dataclasses import asdict
from pathlib import Path

import matplotlib.pyplot as plt

from nma_motor_rnn.connectivity import (
    ExperimentConfig,
    run_q1_baseline,
    write_rows_csv,
)


def main() -> None:
    config = ExperimentConfig(n_units=100, n_training_trials=50)
    trial_rows, checkpoints, summary = run_q1_baseline(
        config, seed=0, p_value=0.10
    )

    output = Path("results/q1")
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    write_rows_csv(output / "trial_history.csv", trial_rows)
    write_rows_csv(output / "checkpoints.csv", checkpoints)
    write_rows_csv(output / "condition.csv", [summary])
    payload = asdict(config)
    payload.update(
        {
            "n_training_trials": 50,
            "p_values": [0.10],
            "seed": 0,
            "p_value": 0.10,
        }
    )
    (output / "config.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(
        [row["trial"] for row in trial_rows],
        [row["online_feedback_loss"] for row in trial_rows],
        color="#365c8d",
    )
    axes[0].set(
        xlabel="Training trial",
        ylabel="Online feedback-space loss",
        title="Q1 diagnostic training loss",
    )
    axes[1].plot(
        [row["checkpoint_trial"] for row in checkpoints],
        [row["heldout_nmse"] for row in checkpoints],
        "o-",
        color="#1f9e89",
    )
    axes[1].set(
        xlabel="Training trial",
        ylabel="Held-out velocity NMSE",
        title="Q1 held-out evaluation",
    )
    for axis in axes:
        axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(figures / "q1_baseline.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
