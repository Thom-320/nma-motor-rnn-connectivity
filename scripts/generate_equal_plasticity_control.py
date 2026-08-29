"""Generate the primary-sized equal-plasticity follow-up control."""

import json
from pathlib import Path

import numpy as np

from nma_motor_rnn.connectivity import (
    hypothesis_contrasts,
    plot_required_figures,
    primary_config,
    run_equal_plasticity_experiment,
    write_rows_csv,
)


def main() -> None:
    output = Path("results/equal_plasticity")
    checkpoints, conditions, elapsed = run_equal_plasticity_experiment(
        primary_config(), seeds=range(8), output_dir=output
    )
    contrasts = hypothesis_contrasts(conditions)
    write_rows_csv(output / "hypothesis_contrasts.csv", contrasts)
    rng = np.random.default_rng(20260829)
    analysis = {
        "network_seed_count": len(contrasts),
        "bootstrap_resamples": 200_000,
        "bootstrap_seed": 20260829,
        "h1_mean": float(np.mean([row["h1_contrast"] for row in contrasts])),
        "h2_mean": float(np.mean([row["h2_contrast"] for row in contrasts])),
    }
    for key in ("h1_contrast", "h2_contrast"):
        values = np.asarray([row[key] for row in contrasts], dtype=float)
        indices = rng.integers(0, len(values), size=(200_000, len(values)))
        bootstrap_means = values[indices].mean(axis=1)
        analysis[f"{key}_bootstrap_95_percentile"] = [
            float(value) for value in np.quantile(bootstrap_means, [0.025, 0.975])
        ]
    (output / "analysis.json").write_text(
        json.dumps(analysis, indent=2) + "\n", encoding="utf-8"
    )
    plot_required_figures(checkpoints, conditions, output / "figures")
    print(f"equal-plasticity control completed in {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
