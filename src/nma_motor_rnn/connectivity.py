"""Paired connectivity-density experiment for the NMA Motor RNN project.

The primary outcome is held-out velocity error under the *fixed random decoder*
used during recurrent FORCE/RLS learning.  PCA/manifold metrics are secondary
and never replace the fixed decoder when measuring task performance.
"""

from __future__ import annotations

import csv
import json
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class ExperimentConfig:
    n_units: int = 100
    p_values: tuple[float, ...] = (0.05, 0.10, 0.20, 0.40)
    g: float = 1.5
    tau: float = 0.1
    dt: float = 0.01
    trial_duration: float = 2.0
    pulse_duration: float = 0.2
    n_targets: int = 6
    target_max: float = 0.2
    n_training_trials: int = 40
    delta: float = 20.0
    eval_every: int = 5
    test_initial_states_per_target: int = 5
    decoder_scale: float = 0.04
    update_stride: int = 2

    @property
    def n_steps(self) -> int:
        return int(round(self.trial_duration / self.dt))

    @property
    def pulse_steps(self) -> int:
        return int(round(self.pulse_duration / self.dt))

    def validate(self) -> None:
        if self.n_units < 2:
            raise ValueError("n_units must be at least 2")
        if not self.p_values or any(not (0.0 < p <= 1.0) for p in self.p_values):
            raise ValueError("p_values must lie in (0, 1]")
        if self.n_training_trials < 1 or self.eval_every < 1:
            raise ValueError("training trials and eval_every must be positive")
        if self.n_steps <= self.pulse_steps:
            raise ValueError("trial_duration must exceed pulse_duration")


@dataclass(frozen=True)
class SharedRandomness:
    seed: int
    mask_uniform: np.ndarray
    weight_normal: np.ndarray
    input_weights: np.ndarray
    decoder: np.ndarray
    train_order: np.ndarray
    train_initial_states: np.ndarray
    test_target_indices: np.ndarray
    test_initial_states: np.ndarray


@dataclass(frozen=True)
class TestTrials:
    target_indices: np.ndarray
    initial_states: np.ndarray


def create_reaching_task(config: ExperimentConfig) -> tuple[np.ndarray, np.ndarray]:
    """Return one-hot cue stimuli and constant two-dimensional target velocities."""
    stimuli = np.zeros((config.n_targets, config.n_steps, config.n_targets), dtype=float)
    targets = np.zeros((config.n_targets, config.n_steps, 2), dtype=float)
    angles = np.linspace(0.0, 2.0 * np.pi, config.n_targets, endpoint=False)
    for target_id, angle in enumerate(angles):
        stimuli[target_id, : config.pulse_steps, target_id] = 1.0
        targets[target_id, config.pulse_steps :, 0] = config.target_max * np.cos(angle)
        targets[target_id, config.pulse_steps :, 1] = config.target_max * np.sin(angle)
    return stimuli, targets


def _balanced_order(n_trials: int, n_targets: int, rng: np.random.Generator) -> np.ndarray:
    order = np.resize(np.arange(n_targets, dtype=int), n_trials)
    rng.shuffle(order)
    return order


def make_shared_randomness(config: ExperimentConfig, seed: int) -> SharedRandomness:
    """Create all random quantities that must be paired across density conditions."""
    config.validate()
    rng = np.random.default_rng(seed)
    mask_uniform = rng.random((config.n_units, config.n_units))
    np.fill_diagonal(mask_uniform, 1.0)
    weight_normal = rng.standard_normal((config.n_units, config.n_units))
    input_weights = rng.uniform(-1.0, 1.0, (config.n_units, config.n_targets))
    decoder = rng.standard_normal((2, config.n_units))
    decoder *= config.decoder_scale * (config.target_max / 0.2) / np.linalg.norm(decoder)
    train_order = _balanced_order(config.n_training_trials, config.n_targets, rng)
    train_initial_states = rng.uniform(-1.0, 1.0, (config.n_training_trials, config.n_units))
    test_target_indices = np.repeat(
        np.arange(config.n_targets, dtype=int), config.test_initial_states_per_target
    )
    test_initial_states = rng.uniform(
        -1.0, 1.0, (test_target_indices.size, config.n_units)
    )
    return SharedRandomness(
        seed=seed,
        mask_uniform=mask_uniform,
        weight_normal=weight_normal,
        input_weights=input_weights,
        decoder=decoder,
        train_order=train_order,
        train_initial_states=train_initial_states,
        test_target_indices=test_target_indices,
        test_initial_states=test_initial_states,
    )


class MotorRNN:
    """Rate RNN with recurrent RLS updates following the NMA/Feulner notebook."""

    def __init__(
        self,
        config: ExperimentConfig,
        p_value: float,
        shared: SharedRandomness,
    ) -> None:
        if not (0.0 < p_value <= 1.0):
            raise ValueError("p_value must lie in (0, 1]")
        self.config = config
        self.p_value = float(p_value)
        self.mask = shared.mask_uniform < self.p_value
        np.fill_diagonal(self.mask, False)
        self.W = (
            config.g
            / np.sqrt(self.p_value * config.n_units)
            * shared.weight_normal
            * self.mask
        )
        self.W_initial = self.W.copy()
        self.W_in = shared.input_weights.copy()
        self.decoder = shared.decoder.copy()
        self.feedback = np.linalg.pinv(self.decoder)
        self.plastic_indices = [np.flatnonzero(row) for row in self.mask]
        self.P = [
            np.eye(indices.size, dtype=float) / config.delta
            for indices in self.plastic_indices
        ]
        self.r = np.zeros(config.n_units, dtype=float)
        self.z = np.zeros(config.n_units, dtype=float)

    def reset_state(self, r0: np.ndarray) -> None:
        self.r = np.asarray(r0, dtype=float).copy()
        self.z = np.tanh(self.r)

    def step(self, external_input: np.ndarray) -> None:
        c = self.config
        self.r += c.dt / c.tau * (-self.r + self.W @ self.z + self.W_in @ external_input)
        self.z = np.tanh(self.r)

    def simulate(self, stimulus: np.ndarray, r0: np.ndarray) -> np.ndarray:
        """Simulate without learning and return activation for every time step."""
        self.reset_state(r0)
        activity = np.empty((self.config.n_steps, self.config.n_units), dtype=float)
        activity[0] = self.z
        for step in range(1, self.config.n_steps):
            self.step(stimulus[step])
            activity[step] = self.z
        return activity

    def train_trial(self, stimulus: np.ndarray, target: np.ndarray, r0: np.ndarray) -> float:
        """Run one online recurrent-learning trial and return feedback-space loss."""
        self.reset_state(r0)
        online_feedback_loss = 0.0
        c = self.config
        for step in range(1, c.n_steps):
            self.step(stimulus[step])
            if step <= c.pulse_steps or step % c.update_stride:
                continue
            velocity_error = self.decoder @ self.z - target[step]
            assigned_error = self.feedback @ velocity_error
            online_feedback_loss += float(np.mean(assigned_error**2))
            for neuron, indices in enumerate(self.plastic_indices):
                if indices.size == 0:
                    continue
                z_plastic = self.z[indices]
                pz = self.P[neuron] @ z_plastic
                denominator = 1.0 + float(z_plastic @ pz)
                self.P[neuron] -= np.outer(pz, pz) / denominator
                self.W[neuron, indices] -= assigned_error[neuron] * pz / denominator
        return online_feedback_loss


def velocity_nmse(predicted: np.ndarray, target: np.ndarray) -> float:
    predicted = np.asarray(predicted, dtype=float)
    target = np.asarray(target, dtype=float)
    if predicted.shape != target.shape:
        raise ValueError("predicted and target velocity arrays must have the same shape")
    numerator = float(np.sum((predicted - target) ** 2))
    centered = target - np.mean(target, axis=tuple(range(target.ndim - 1)), keepdims=True)
    denominator = float(np.sum(centered**2))
    if denominator <= 0.0:
        raise ValueError("target variance is zero; NMSE is undefined")
    return numerator / denominator


def participation_ratio(eigenvalues: np.ndarray) -> float:
    eigenvalues = np.clip(np.asarray(eigenvalues, dtype=float), 0.0, None)
    denominator = float(np.sum(eigenvalues**2))
    return 0.0 if denominator == 0.0 else float(np.sum(eigenvalues) ** 2 / denominator)


def compute_manifold_metrics(activity: np.ndarray) -> dict[str, object]:
    """Compute sorted PCA spectrum, continuous PR, and dimensions explaining 90%."""
    activity = np.asarray(activity, dtype=float)
    if activity.ndim != 2 or activity.shape[0] < 2:
        raise ValueError("activity must have shape (observations, neurons)")
    centered = activity - activity.mean(axis=0, keepdims=True)
    covariance = np.cov(centered, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = np.clip(eigenvalues[order], 0.0, None)
    eigenvectors = eigenvectors[:, order]
    total = float(eigenvalues.sum())
    d90 = 0 if total == 0.0 else int(np.searchsorted(np.cumsum(eigenvalues) / total, 0.90) + 1)
    return {
        "covariance": covariance,
        "eigenvalues": eigenvalues,
        "eigenvectors": eigenvectors,
        "d_pr": participation_ratio(eigenvalues),
        "d90": d90,
    }


def evaluate_fixed_decoder(
    network: MotorRNN,
    test_trials: TestTrials,
    stimuli: np.ndarray,
    targets: np.ndarray,
) -> dict[str, object]:
    """Evaluate held-out motor output without fitting a decoder or changing weights."""
    if test_trials.target_indices.shape[0] != test_trials.initial_states.shape[0]:
        raise ValueError("test target indices and initial states must have equal trial count")
    predictions: list[np.ndarray] = []
    truths: list[np.ndarray] = []
    activities: list[np.ndarray] = []
    per_trial_mse: list[float] = []
    for target_id, r0 in zip(test_trials.target_indices, test_trials.initial_states):
        activity = network.simulate(stimuli[target_id], r0)
        post_activity = activity[network.config.pulse_steps :]
        predicted_velocity = post_activity @ network.decoder.T
        true_velocity = targets[target_id, network.config.pulse_steps :]
        predictions.append(predicted_velocity)
        truths.append(true_velocity)
        activities.append(post_activity)
        per_trial_mse.append(float(np.mean((predicted_velocity - true_velocity) ** 2)))
    predicted = np.stack(predictions)
    truth = np.stack(truths)
    trial_mse = np.asarray(per_trial_mse)
    per_target_mse = {
        int(target_id): float(trial_mse[test_trials.target_indices == target_id].mean())
        for target_id in np.unique(test_trials.target_indices)
    }
    return {
        "raw_mse": float(np.mean((predicted - truth) ** 2)),
        "nmse": velocity_nmse(predicted, truth),
        "per_trial_mse": trial_mse,
        "per_target_mse": per_target_mse,
        "predicted_velocity": predicted,
        "target_velocity": truth,
        "activity": np.concatenate(activities, axis=0),
    }


def _spectral_radius(weights: np.ndarray) -> float:
    return float(np.max(np.abs(np.linalg.eigvals(weights))))


def _condition_metadata(network: MotorRNN, seed: int) -> dict[str, object]:
    degrees = network.mask.sum(axis=1)
    return {
        "seed": int(seed),
        "p_value": network.p_value,
        "expected_in_degree": network.p_value * (network.config.n_units - 1),
        "realized_degree_mean": float(degrees.mean()),
        "realized_degree_min": int(degrees.min()),
        "realized_degree_max": int(degrees.max()),
        "synapse_count": int(network.mask.sum()),
        "plastic_weight_count": int(sum(x.size for x in network.plastic_indices)),
        "initial_spectral_radius": _spectral_radius(network.W_initial),
    }


def train_condition(
    config: ExperimentConfig,
    shared_randomness: SharedRandomness,
    p_value: float,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Train one paired density condition and return checkpoint and summary rows."""
    stimuli, targets = create_reaching_task(config)
    network = MotorRNN(config, p_value, shared_randomness)
    test_trials = TestTrials(
        target_indices=shared_randomness.test_target_indices,
        initial_states=shared_randomness.test_initial_states,
    )
    metadata = _condition_metadata(network, shared_randomness.seed)
    rows: list[dict[str, object]] = []
    online_losses: list[float] = []
    checkpoint_trials = {0, config.n_training_trials}
    checkpoint_trials.update(range(config.eval_every, config.n_training_trials + 1, config.eval_every))

    def record_checkpoint(trial: int) -> None:
        evaluation = evaluate_fixed_decoder(network, test_trials, stimuli, targets)
        manifold = compute_manifold_metrics(evaluation["activity"])
        rows.append(
            {
                **metadata,
                "checkpoint_trial": int(trial),
                "heldout_nmse": float(evaluation["nmse"]),
                "heldout_raw_mse": float(evaluation["raw_mse"]),
                "online_feedback_loss": float(online_losses[-1]) if online_losses else np.nan,
                "weight_change_fro": float(np.linalg.norm(network.W - network.W_initial)),
                "spectral_radius": _spectral_radius(network.W),
                "d_pr": float(manifold["d_pr"]),
                "d90": int(manifold["d90"]),
                "per_target_mse_json": json.dumps(evaluation["per_target_mse"], sort_keys=True),
            }
        )

    record_checkpoint(0)
    for trial in range(1, config.n_training_trials + 1):
        target_id = int(shared_randomness.train_order[trial - 1])
        loss = network.train_trial(
            stimuli[target_id],
            targets[target_id],
            shared_randomness.train_initial_states[trial - 1],
        )
        online_losses.append(loss)
        if trial in checkpoint_trials:
            record_checkpoint(trial)

    checkpoints = np.asarray([row["checkpoint_trial"] for row in rows], dtype=float)
    nmse_values = np.asarray([row["heldout_nmse"] for row in rows], dtype=float)
    auc = float(np.trapezoid(nmse_values, checkpoints) / checkpoints[-1])
    summary = {
        **metadata,
        "n_training_trials": config.n_training_trials,
        "final_heldout_nmse": float(nmse_values[-1]),
        "final_heldout_raw_mse": float(rows[-1]["heldout_raw_mse"]),
        "learning_curve_auc": auc,
        "final_weight_change_fro": float(rows[-1]["weight_change_fro"]),
        "final_spectral_radius": float(rows[-1]["spectral_radius"]),
        "final_d_pr": float(rows[-1]["d_pr"]),
        "final_d90": int(rows[-1]["d90"]),
    }
    return rows, summary


def run_experiment(
    config: ExperimentConfig,
    seeds: Iterable[int],
    output_dir: str | Path | None = None,
) -> tuple[list[dict[str, object]], list[dict[str, object]], float]:
    """Run all paired seeds/densities, optionally saving CSV and configuration JSON."""
    config.validate()
    start = time.perf_counter()
    checkpoint_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    seeds = tuple(int(seed) for seed in seeds)
    for seed in seeds:
        shared = make_shared_randomness(config, seed)
        for p_value in config.p_values:
            rows, summary = train_condition(config, shared, p_value)
            checkpoint_rows.extend(rows)
            summary_rows.append(summary)
    elapsed = time.perf_counter() - start
    if output_dir is not None:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        write_rows_csv(output_path / "checkpoints.csv", checkpoint_rows)
        write_rows_csv(output_path / "conditions.csv", summary_rows)
        payload = asdict(config)
        payload["p_values"] = list(config.p_values)
        payload["seeds"] = list(seeds)
        payload["elapsed_seconds"] = elapsed
        (output_path / "config.json").write_text(json.dumps(payload, indent=2) + "\n")
    return checkpoint_rows, summary_rows, elapsed


def write_rows_csv(path: str | Path, rows: Sequence[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot write an empty results table")
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def hypothesis_contrasts(summary_rows: Sequence[dict[str, object]]) -> list[dict[str, float]]:
    """Return seed-level preregistered H1 and H2 contrasts; positive supports each hypothesis."""
    by_seed: dict[int, dict[float, float]] = {}
    for row in summary_rows:
        by_seed.setdefault(int(row["seed"]), {})[float(row["p_value"])] = float(
            row["final_heldout_nmse"]
        )
    contrasts: list[dict[str, float]] = []
    required = {0.05, 0.10, 0.20, 0.40}
    for seed, values in sorted(by_seed.items()):
        missing = required.difference(values)
        if missing:
            raise ValueError(f"seed {seed} is missing p values: {sorted(missing)}")
        h1 = values[0.05] - np.mean([values[0.10], values[0.20], values[0.40]])
        h2 = (values[0.05] - values[0.20]) - (values[0.20] - values[0.40])
        contrasts.append({"seed": float(seed), "h1_contrast": float(h1), "h2_contrast": float(h2)})
    return contrasts


def plot_required_figures(
    checkpoint_rows: Sequence[dict[str, object]],
    summary_rows: Sequence[dict[str, object]],
    output_dir: str | Path,
) -> list[Path]:
    """Create the four required figures using only NumPy and Matplotlib."""
    import matplotlib.pyplot as plt

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    p_values = sorted({float(row["p_value"]) for row in summary_rows})
    seeds = sorted({int(row["seed"]) for row in summary_rows})
    colors = dict(zip(p_values, plt.cm.viridis(np.linspace(0.1, 0.9, len(p_values)))))
    saved: list[Path] = []

    fig, ax = plt.subplots(figsize=(8, 5))
    for p_value in p_values:
        curves = []
        checkpoints = None
        for seed in seeds:
            selected = sorted(
                (
                    row
                    for row in checkpoint_rows
                    if int(row["seed"]) == seed and float(row["p_value"]) == p_value
                ),
                key=lambda row: int(row["checkpoint_trial"]),
            )
            checkpoints = np.asarray([row["checkpoint_trial"] for row in selected])
            curve = np.asarray([row["heldout_nmse"] for row in selected], dtype=float)
            curves.append(curve)
            ax.plot(checkpoints, curve, color=colors[p_value], alpha=0.22, linewidth=1)
        curves_array = np.vstack(curves)
        mean = curves_array.mean(axis=0)
        sem = curves_array.std(axis=0, ddof=1) / np.sqrt(curves_array.shape[0]) if len(curves) > 1 else np.zeros_like(mean)
        ax.plot(checkpoints, mean, color=colors[p_value], linewidth=2.5, label=f"p={p_value:.2f}")
        ax.fill_between(checkpoints, mean - sem, mean + sem, color=colors[p_value], alpha=0.18)
    ax.set(xlabel="Training trial", ylabel="Held-out velocity NMSE", title="Held-out performance during recurrent learning")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    path = output_path / "figure1_heldout_nmse.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    saved.append(path)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for metric, ylabel, ax in [
        ("final_heldout_nmse", "Final held-out NMSE", axes[0]),
        ("learning_curve_auc", "Learning-curve AUC", axes[1]),
    ]:
        for seed in seeds:
            selected = sorted((row for row in summary_rows if int(row["seed"]) == seed), key=lambda row: float(row["p_value"]))
            ax.plot([row["p_value"] for row in selected], [row[metric] for row in selected], "o-", alpha=0.45)
        ax.set(xlabel="Connection probability p", ylabel=ylabel)
        ax.grid(alpha=0.25)
    fig.suptitle("Final performance and learning efficiency")
    fig.tight_layout()
    path = output_path / "figure2_final_and_auc.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    saved.append(path)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for metric, ylabel, ax in [("final_d_pr", "Participation-ratio dimension", axes[0]), ("final_d90", "PCs explaining 90%", axes[1])]:
        for seed in seeds:
            selected = sorted((row for row in summary_rows if int(row["seed"]) == seed), key=lambda row: float(row["p_value"]))
            ax.plot([row["p_value"] for row in selected], [row[metric] for row in selected], "o-", alpha=0.45)
        ax.set(xlabel="Connection probability p", ylabel=ylabel)
        ax.grid(alpha=0.25)
    fig.suptitle("Exploratory task-evoked manifold dimensionality")
    fig.tight_layout()
    path = output_path / "figure3_manifold_dimensions.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    saved.append(path)

    fig, ax = plt.subplots(figsize=(6, 5))
    for p_value in p_values:
        selected = [row for row in summary_rows if float(row["p_value"]) == p_value]
        ax.scatter(
            [row["final_d_pr"] for row in selected],
            [row["final_heldout_nmse"] for row in selected],
            label=f"p={p_value:.2f}",
            color=colors[p_value],
            s=45,
        )
    ax.set(xlabel="Participation-ratio dimension", ylabel="Final held-out NMSE", title="Exploratory dimension-performance association")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    path = output_path / "figure4_dimension_vs_nmse.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    saved.append(path)
    return saved


def pilot_config() -> ExperimentConfig:
    return ExperimentConfig()


def primary_config() -> ExperimentConfig:
    return replace(ExperimentConfig(), n_units=200, n_training_trials=60)
