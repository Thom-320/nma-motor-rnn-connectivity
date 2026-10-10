"""Analyse the R1-R5 robustness grid.

Reads ``results/robustness/<arm>_N<N>/checkpoints.csv`` and writes, under
``results/robustness/analysis/``:

- ``seed_contrasts.csv``     seed-level H1/H2 (and R3) contrasts per arm, N, checkpoint;
- ``contrast_summary.csv``   mean, seed-bootstrap 95 % CI, n positive, exact sign test;
- ``paired_change.csv``      primary-minus-control H1/H2 per seed, summarised the same way;
- ``r3_summary.csv``         frozen-drive ablation contrasts and two-way slopes, for the
                             gain-matched (``frozen``) and unmatched-gain
                             (``frozen_unmatched``) variants, and their difference;
- ``radius_gap.csv``         initial spectral-radius gap vs H1 per seed and arm;
- ``summary_table.md``       one table: does the sign reversal survive each check?
- ``analysis.json``          bootstrap settings and headline numbers;

and one figure per robustness axis under ``results/robustness/figures/``.
Arms that have not been run yet (e.g. Kaggle shards) are skipped.

H1 = NMSE(0.05) - mean NMSE(0.10, 0.20, 0.40); positive = denser is better.
H2 = (NMSE(0.05) - NMSE(0.20)) - (NMSE(0.20) - NMSE(0.40)); positive =
diminishing returns.  Both are exploratory contrasts (see
``hypothesis_contrasts``); nothing here is preregistered.
"""

from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

BOOTSTRAP_RESAMPLES = 100_000
BOOTSTRAP_SEED = 20261009
REPORT = (60, 100, 150, 200)
P_VALUES = (0.05, 0.10, 0.20, 0.40)
R3_FRACTIONS = (0.5, 0.75, 0.875)
R3_DENSITIES = (0.10, 0.20, 0.40)
FROZEN_ARMS = ("frozen", "frozen_unmatched")
# (primary arm, equal-budget arm, pair suffix) compared in the summary table.
PAIRS = (("primary", "control", ""), ("primary_gain", "control_gain", "_gain"),
         ("primary", "control_random", "_random"))
BLUE, ORANGE = "#2a78d6", "#eb6834"
BLUE_LIGHT, ORANGE_LIGHT = "#86b6ef", "#f2a07f"
DENSITY_RAMP = {0.05: "#86b6ef", 0.10: "#5598e7", 0.20: "#256abf", 0.40: "#0d366b"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"


# ---------------------------------------------------------------- statistics
def bootstrap_ci(values: np.ndarray, rng: np.random.Generator | None = None) -> tuple[float, float]:
    """Percentile CI of the mean.  A fresh generator per call keeps every
    interval independent of how many other contrasts were computed first."""
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    values = np.asarray(values, dtype=float)
    if values.size < 2:
        return (float("nan"), float("nan"))
    idx = rng.integers(0, values.size, size=(BOOTSTRAP_RESAMPLES, values.size))
    low, high = np.quantile(values[idx].mean(axis=1), [0.025, 0.975])
    return float(low), float(high)


def sign_test(values: np.ndarray) -> tuple[int, int, float]:
    """Exact two-sided binomial sign test; zeros are dropped."""
    values = np.asarray(values, dtype=float)
    positive = int(np.sum(values > 0))
    n = int(np.sum(values != 0))
    if n == 0:
        return positive, n, 1.0
    k = min(positive, n - positive)
    p = 2.0 * sum(comb(n, i) for i in range(k + 1)) / 2.0**n
    return positive, n, float(min(1.0, p))


def summarise(values, rng) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    low, high = bootstrap_ci(values, rng)
    positive, n, p = sign_test(values)
    return {
        "n_seeds": int(values.size),
        "mean": float(values.mean()),
        "sd": float(values.std(ddof=1)) if values.size > 1 else float("nan"),
        "ci_low": low,
        "ci_high": high,
        "n_positive": positive,
        "sign_test_p": p,
    }


def sign_label(row) -> str:
    if row["ci_low"] > 0:
        return "+"
    if row["ci_high"] < 0:
        return "-"
    return "0"


# ---------------------------------------------------------------- loading
def load_checkpoints(root: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(root.glob("*_N*/checkpoints.csv")):
        frames.append(pd.read_csv(path))
    if not frames:
        raise SystemExit(f"no robustness results under {root}")
    data = pd.concat(frames, ignore_index=True)
    data["p_value"] = data["p_value"].round(4)
    return data


def h_contrasts(table: pd.DataFrame) -> pd.DataFrame:
    """table: index seed, columns p_value -> NMSE."""
    v = {p: table[p] for p in P_VALUES}
    return pd.DataFrame(
        {
            "h1": v[0.05] - (v[0.10] + v[0.20] + v[0.40]) / 3.0,
            "h2": (v[0.05] - v[0.20]) - (v[0.20] - v[0.40]),
        }
    )


def seed_contrasts(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    standard = data[~data["arm"].isin(FROZEN_ARMS)]
    for (arm, n_units, trial), group in standard.groupby(["arm", "n_units", "checkpoint_trial"]):
        table = group.pivot(index="seed", columns="p_value", values="heldout_nmse")
        if not set(P_VALUES) <= set(table.columns):
            continue
        table = table.dropna()
        contrasts = h_contrasts(table)
        for seed, row in contrasts.iterrows():
            rows.append(
                {"arm": arm, "n_units": n_units, "checkpoint_trial": trial, "seed": seed,
                 "h1": row["h1"], "h2": row["h2"]}
            )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- R3
def r3_cells(data: pd.DataFrame, trial: int, arm: str = "frozen") -> pd.DataFrame:
    """Seed x (p, f) NMSE table.  The f = 0 cell is the p = 0.05 network and is
    taken from the ``frozen`` arm for both variants (it is the same network)."""
    at_trial = data[data["checkpoint_trial"] == trial]
    frozen = at_trial[at_trial["arm"] == arm]
    if arm != "frozen":
        base = at_trial[(at_trial["arm"] == "frozen") & (at_trial["frozen_fraction"] == 0.0)]
        frozen = pd.concat([base[base["seed"].isin(frozen["seed"])], frozen])
    cells = frozen.pivot_table(
        index="seed", columns=["p_value", "frozen_fraction"], values="heldout_nmse"
    )
    needed = [(0.40, 0.0)] + [(p, f) for p in R3_DENSITIES for f in R3_FRACTIONS]
    if any(key not in cells.columns for key in needed):
        return None  # factorial not complete yet
    return cells[needed].dropna()


def r3_contrasts(cells: pd.DataFrame) -> pd.DataFrame:
    """Seed-level R3 contrasts.

    density_f{f}: NMSE(p=0.10, f) - mean NMSE(p=0.20/0.40, f); + = denser better
                  at a fixed frozen-drive fraction.
    frozen_p{p}:  NMSE(f=0) - mean NMSE(p, f in {0.5, 0.75, 0.875}); + = more
                  frozen drive is better at fixed density.
    diag_h1:      the control-equivalent H1 rebuilt from the diagonal cells.
    slope_logp / slope_f: per-seed least-squares slopes of NMSE on log2(p) and f
                  over the 3x3 factorial; slope_logp < 0 = denser better.
    """
    base = cells[(0.40, 0.0)]
    out = pd.DataFrame(index=cells.index)
    for f in R3_FRACTIONS:
        out[f"density_f{f}"] = cells[(0.10, f)] - (cells[(0.20, f)] + cells[(0.40, f)]) / 2
    for p in R3_DENSITIES:
        out[f"frozen_p{p}"] = base - sum(cells[(p, f)] for f in R3_FRACTIONS) / 3
    diag = [(0.10, 0.5), (0.20, 0.75), (0.40, 0.875)]
    out["diag_h1"] = base - sum(cells[c] for c in diag) / 3
    design = np.array([[1.0, np.log2(p / 0.10), f] for p in R3_DENSITIES for f in R3_FRACTIONS])
    y = np.stack([cells[(p, f)].to_numpy() for p in R3_DENSITIES for f in R3_FRACTIONS])
    coef, *_ = np.linalg.lstsq(design, y, rcond=None)
    out["slope_logp"] = coef[1]
    out["slope_f"] = coef[2]
    return out


def r3_gain_contrasts(matched: pd.DataFrame, unmatched: pd.DataFrame) -> pd.DataFrame:
    """Seed-level gain-matched minus unmatched NMSE, averaged over density.

    shrink_f{f}: mean over p of NMSE(matched, p, f) - NMSE(unmatched, p, f);
                 + = the unmatched network (full-size trainable weights, extra
                 total gain) is better.
    """
    seeds = matched.index.intersection(unmatched.index)
    out = pd.DataFrame(index=seeds)
    for f in R3_FRACTIONS:
        out[f"shrink_f{f}"] = sum(
            matched.loc[seeds, (p, f)] - unmatched.loc[seeds, (p, f)] for p in R3_DENSITIES
        ) / len(R3_DENSITIES)
    out["shrink_mean"] = out[[f"shrink_f{f}" for f in R3_FRACTIONS]].mean(axis=1)
    return out


def convergence_table(data: pd.DataFrame) -> pd.DataFrame:
    """Networks whose held-out NMSE still fell between two checkpoints."""
    rows = []
    for (arm, n_units), group in data.groupby(["arm", "n_units"]):
        table = group.pivot_table(index=["seed", "condition"], columns="checkpoint_trial",
                                  values="heldout_nmse")
        for start, end in ((50, 60), (150, 200), (190, 200)):
            if start not in table or end not in table:
                continue
            change = (table[end] - table[start]) / table[start]
            rows.append({"arm": arm, "n_units": n_units, "from_trial": start, "to_trial": end,
                         "n_networks": int(change.size), "n_improving": int((change < 0).sum()),
                         "median_relative_change": float(change.median())})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- figures
def _style(ax):
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED)
    ax.axhline(0.0, color=MUTED, linewidth=0.8) if ax.get_ylim()[0] < 0 < ax.get_ylim()[1] else None


def _mean_ci(frame, column, rng):
    stats = summarise(frame[column].to_numpy(), rng)
    return stats["mean"], stats["ci_low"], stats["ci_high"]


def figure_r1(contrasts, data, figures, rng):
    import matplotlib.pyplot as plt

    sel = contrasts[(contrasts["n_units"] == 200) & (contrasts["seed"] < 8)]
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    ax = axes[0]
    for arm, color, name in (("primary", BLUE, "All edges trainable"), ("control", ORANGE, "Equal trainable budget")):
        part = sel[sel["arm"] == arm]
        if part.empty:
            continue
        trials, means, lows, highs = [], [], [], []
        for trial, group in part.groupby("checkpoint_trial"):
            if trial == 0:
                continue
            m, lo, hi = _mean_ci(group, "h1", rng)
            trials.append(trial); means.append(m); lows.append(lo); highs.append(hi)
        ax.plot(trials, means, color=color, linewidth=2, label=name)
        ax.fill_between(trials, lows, highs, color=color, alpha=0.18, linewidth=0)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.axvline(60, color=MUTED, linewidth=0.8, linestyle=":")
    ax.text(62, ax.get_ylim()[1] * 0.92, "original snapshot", color=MUTED, fontsize=8)
    ax.set(xlabel="Training trial", ylabel="H1 contrast (+ = denser better)",
           title="H1 over training (8 seeds, 95% CI)")
    ax.legend(frameon=False, fontsize=8)
    for ax, arm, title in ((axes[1], "primary", "All edges trainable"), (axes[2], "control", "Equal trainable budget")):
        part = data[(data["arm"] == arm) & (data["n_units"] == 200) & (data["seed"] < 8)]
        for p in P_VALUES:
            curve = part[part["p_value"] == p].groupby("checkpoint_trial")["heldout_nmse"].mean()
            ax.plot(curve.index, curve.values, color=DENSITY_RAMP[p], linewidth=2, label=f"p = {p:.2f}")
        ax.axvline(60, color=MUTED, linewidth=0.8, linestyle=":")
        ax.set(xlabel="Training trial", ylabel="Held-out NMSE (mean of 8 seeds)", title=title)
        ax.legend(frameon=False, fontsize=8)
    for ax in axes:
        _style(ax)
    fig.tight_layout()
    path = figures / "R1_convergence.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def figure_r2(contrasts, radius, figures, rng):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    ax = axes[0]
    arms = [("primary", BLUE, "o", "All trainable"), ("primary_gain", BLUE_LIGHT, "s", "All trainable, gain-matched"),
            ("control", ORANGE, "o", "Equal budget"), ("control_gain", ORANGE_LIGHT, "s", "Equal budget, gain-matched")]
    seeds = sorted(set(contrasts[contrasts["arm"] == "primary_gain"]["seed"]))
    sel = contrasts[(contrasts["n_units"] == 200) & contrasts["seed"].isin(seeds)]
    for offset, (arm, color, marker, name) in enumerate(arms):
        part = sel[sel["arm"] == arm]
        if part.empty:
            continue
        trials, means, lows, highs = [], [], [], []
        for trial in REPORT:
            group = part[part["checkpoint_trial"] == trial]
            m, lo, hi = _mean_ci(group, "h1", rng)
            trials.append(trial + (offset - 1.5) * 4); means.append(m); lows.append(lo); highs.append(hi)
        ax.errorbar(trials, means, yerr=[np.subtract(means, lows), np.subtract(highs, means)],
                    color=color, marker=marker, markersize=7, linewidth=2, capsize=0, label=name)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.set(xlabel="Training trial", ylabel="H1 contrast (+ = denser better)",
           title=f"Gain matching ({len(seeds)} seeds, 95% CI)", xticks=REPORT)
    ax.legend(frameon=False, fontsize=7.5, loc="center", ncol=2)
    ax = axes[1]
    for arm, color in (("primary", BLUE), ("control", ORANGE)):
        part = radius[radius["arm"] == arm]
        ax.scatter(part["radius_gap"], part["h1_t60"], s=55, color=color,
                   edgecolor="white", linewidth=1.5, label=f"{arm}: r = {part['radius_gap'].corr(part['h1_t60']):+.2f}")
    ax.set(xlabel="Initial radius gap  rho(0.05) - mean rho(denser)", ylabel="H1 at trial 60",
           title="Un-matched networks: radius gap vs H1")
    ax.legend(frameon=False, fontsize=8)
    for ax in axes:
        _style(ax)
    fig.tight_layout()
    path = figures / "R2_gain_matched.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def figure_r3(data, figures, arm="frozen"):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    ramp = {0.10: DENSITY_RAMP[0.10], 0.20: DENSITY_RAMP[0.20], 0.40: DENSITY_RAMP[0.40]}
    variant = "" if arm == "frozen" else ", unmatched gain"
    for ax, trial in zip(axes, (60, 200)):
        cells = r3_cells(data, trial, arm)
        base = cells[(0.40, 0.0)].mean()
        for p in R3_DENSITIES:
            means = [base] + [cells[(p, f)].mean() for f in R3_FRACTIONS]
            sems = [cells[(0.40, 0.0)].sem()] + [cells[(p, f)].sem() for f in R3_FRACTIONS]
            ax.errorbar((0.0,) + R3_FRACTIONS, means, yerr=sems, color=ramp[p], marker="o",
                        markersize=7, linewidth=2, capsize=0, label=f"structural p = {p:.2f}")
        diag = [(0.10, 0.5), (0.20, 0.75), (0.40, 0.875)]
        ax.plot([0.0] + [f for _, f in diag], [base] + [cells[c].mean() for c in diag],
                color=ORANGE, linestyle="--", linewidth=1.5,
                label="equal-budget control (diagonal)" if arm == "frozen" else "diagonal")
        ax.set(xlabel="Frozen share f" + (" of recurrent input variance" if arm == "frozen"
                                          else " (trainable part fixed; total variance g^2(1+f))"),
               title=f"Frozen-drive ablation{variant}, trial {trial}")
        _style(ax)
    axes[0].set_ylabel(f"Held-out NMSE ({len(cells)} seeds, mean +/- SEM)")
    axes[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    path = figures / ("R3_frozen_drive.png" if arm == "frozen" else "R3_unmatched_gain.png")
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def figure_random_subset(contrasts, data, figures, rng):
    import matplotlib.pyplot as plt

    seeds = sorted(set(contrasts[contrasts["arm"] == "control_random"]["seed"]))
    sel = contrasts[(contrasts["n_units"] == 200) & contrasts["seed"].isin(seeds)]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    ax = axes[0]
    arms = (("primary", BLUE, "All edges trainable"), ("control", ORANGE, "Equal budget: sparse edges"),
            ("control_random", ORANGE_LIGHT, "Equal budget: random subset"))
    for arm, color, name in arms:
        part = sel[sel["arm"] == arm]
        trials, means, lows, highs = [], [], [], []
        for trial, group in part.groupby("checkpoint_trial"):
            if trial == 0:
                continue
            m, lo, hi = _mean_ci(group, "h1", rng)
            trials.append(trial); means.append(m); lows.append(lo); highs.append(hi)
        ax.plot(trials, means, color=color, linewidth=2, label=name)
        ax.fill_between(trials, lows, highs, color=color, alpha=0.18, linewidth=0)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.set(xlabel="Training trial", ylabel="H1 contrast (+ = denser better)",
           title=f"Budget-matching schemes ({len(seeds)} seeds, 95% CI)")
    ax.legend(frameon=False, fontsize=8)
    ax = axes[1]
    part = data[(data["arm"] == "control_random") & (data["n_units"] == 200)]
    for p in P_VALUES:
        curve = part[part["p_value"] == p].groupby("checkpoint_trial")["heldout_nmse"].mean()
        ax.plot(curve.index, curve.values, color=DENSITY_RAMP[p], linewidth=2, label=f"p = {p:.2f}")
    ax.set(xlabel="Training trial", ylabel=f"Held-out NMSE (mean of {len(seeds)} seeds)",
           title="Equal budget, random subset")
    ax.legend(frameon=False, fontsize=8)
    for ax in axes:
        _style(ax)
    fig.tight_layout()
    path = figures / "B3_random_subset.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def figure_r4(contrasts, figures, rng):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ax, trial in zip(axes, (60, 200)):
        for offset, (arm, color, name) in enumerate((("primary", BLUE, "All edges trainable"),
                                                     ("control", ORANGE, "Equal trainable budget"))):
            part = contrasts[(contrasts["arm"] == arm) & (contrasts["checkpoint_trial"] == trial)
                             & (contrasts["seed"] < 8)]
            sizes, means, lows, highs = [], [], [], []
            for n_units, group in part.groupby("n_units"):
                m, lo, hi = _mean_ci(group, "h1", rng)
                sizes.append(n_units * (1 + (offset - 0.5) * 0.06)); means.append(m); lows.append(lo); highs.append(hi)
            ax.errorbar(sizes, means, yerr=[np.subtract(means, lows), np.subtract(highs, means)],
                        color=color, marker="o", markersize=7, linewidth=2, capsize=0, label=name)
        ax.set_xscale("log")
        ax.set_xticks([100, 200, 400], labels=["100", "200", "400"])
        ax.xaxis.set_minor_locator(plt.NullLocator())
        ax.axhline(0, color=MUTED, linewidth=0.8)
        ax.set(xlabel="Network size N", title=f"H1 vs network size, trial {trial} (8 seeds, 95% CI)")
        _style(ax)
    axes[0].set_ylabel("H1 contrast (+ = denser better)")
    axes[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    path = figures / "R4_network_size.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def figure_r5(contrasts, figures):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ax, trial in zip(axes, (60, 200)):
        part = contrasts[(contrasts["n_units"] == 200) & (contrasts["checkpoint_trial"] == trial)
                         & contrasts["arm"].isin(["primary", "control"])]
        table = part.pivot(index="seed", columns="arm", values="h1")
        for seed, row in table.iterrows():
            ax.plot([0, 1], [row["primary"], row["control"]], color=GRID, linewidth=1.2, zorder=1)
        for x, arm, color in ((0, "primary", BLUE), (1, "control", ORANGE)):
            ax.scatter(np.full(len(table), x), table[arm], s=55, color=color,
                       edgecolor="white", linewidth=1.5, zorder=2)
        ax.axhline(0, color=MUTED, linewidth=0.8)
        ax.set_xticks([0, 1], labels=["All edges trainable", "Equal trainable budget"])
        ax.set(title=f"Per-seed H1, N = 200, {len(table)} seeds, trial {trial}")
        _style(ax)
    axes[0].set_ylabel("H1 contrast (+ = denser better)")
    fig.tight_layout()
    path = figures / "R5_sixteen_seeds.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


# ---------------------------------------------------------------- main
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="results/robustness")
    args = parser.parse_args()
    root = Path(args.root)
    out = root / "analysis"
    figures = root / "figures"
    out.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(BOOTSTRAP_SEED)

    data = load_checkpoints(root)
    contrasts = seed_contrasts(data)
    contrasts.to_csv(out / "seed_contrasts.csv", index=False)

    # Seed sets: "8" = seeds 0-7 (R1-R4), "16" = seeds 0-15 where available (R5).
    def seed_sets(frame):
        yield "0-7", frame[frame["seed"] < 8]
        if frame["seed"].max() >= 8:
            yield f"0-{int(frame['seed'].max())}", frame

    summary_rows = []
    for (arm, n_units, trial), group in contrasts.groupby(["arm", "n_units", "checkpoint_trial"]):
        if trial not in REPORT:
            continue
        for label, subset in seed_sets(group):
            for key in ("h1", "h2"):
                summary_rows.append({"arm": arm, "n_units": n_units, "checkpoint_trial": trial,
                                     "seeds": label, "contrast": key, **summarise(subset[key], rng)})
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out / "contrast_summary.csv", index=False)

    paired_rows = []
    for primary_arm, control_arm, suffix in PAIRS:
        primary = contrasts[contrasts["arm"] == primary_arm]
        control = contrasts[contrasts["arm"] == control_arm]
        merged = primary.merge(control, on=["n_units", "checkpoint_trial", "seed"], suffixes=("_p", "_c"))
        for (n_units, trial), group in merged.groupby(["n_units", "checkpoint_trial"]):
            if trial not in REPORT:
                continue
            for label, subset in seed_sets(group):
                for key in ("h1", "h2"):
                    diff = subset[f"{key}_p"] - subset[f"{key}_c"]
                    paired_rows.append({"pair": "primary-control" + suffix, "n_units": n_units,
                                        "checkpoint_trial": trial, "seeds": label, "contrast": key,
                                        **summarise(diff, rng)})
    paired = pd.DataFrame(paired_rows)
    paired.to_csv(out / "paired_change.csv", index=False)

    r3_rows = []

    def r3_seed_sets(frame):
        yield "0-7", frame[frame.index < 8]
        if frame.index.max() >= 8:
            yield f"0-{int(frame.index.max())}", frame

    for arm in FROZEN_ARMS:
        if not (data["arm"] == arm).any():
            continue
        for trial in REPORT:
            cells = r3_cells(data, trial, arm)
            if cells is None or len(cells) < 2:
                continue
            r3 = r3_contrasts(cells)
            if arm != "frozen":
                matched = r3_cells(data, trial, "frozen")
                r3 = r3.join(r3_gain_contrasts(matched, cells), how="inner")
            for label, subset in r3_seed_sets(r3):
                for column in r3.columns:
                    r3_rows.append({"arm": arm, "seeds": label, "checkpoint_trial": trial,
                                    "contrast": column, **summarise(subset[column], rng)})
    r3_summary = pd.DataFrame(r3_rows)
    if not r3_summary.empty:
        r3_summary.to_csv(out / "r3_summary.csv", index=False)

    # Radius gap vs H1 (unmatched arms, trial 60, N = 200, seeds 0-7).
    initial = data[data["checkpoint_trial"] == 0].drop_duplicates(["arm", "n_units", "seed", "condition"])
    radius_rows = []
    for arm in ("primary", "control", "primary_gain", "control_gain"):
        part = initial[(initial["arm"] == arm) & (initial["n_units"] == 200)]
        if part.empty:
            continue
        rho = part.pivot(index="seed", columns="p_value", values="initial_spectral_radius")
        gap = rho[0.05] - (rho[0.10] + rho[0.20] + rho[0.40]) / 3
        h1 = contrasts[(contrasts["arm"] == arm) & (contrasts["n_units"] == 200)
                       & (contrasts["checkpoint_trial"] == 60)].set_index("seed")["h1"]
        h1_200 = contrasts[(contrasts["arm"] == arm) & (contrasts["n_units"] == 200)
                           & (contrasts["checkpoint_trial"] == 200)].set_index("seed")["h1"]
        for seed in rho.index:
            radius_rows.append({"arm": arm, "seed": seed, "radius_gap": gap[seed],
                                "h1_t60": h1.get(seed, np.nan), "h1_t200": h1_200.get(seed, np.nan)})
    radius = pd.DataFrame(radius_rows)
    radius.to_csv(out / "radius_gap.csv", index=False)

    convergence = convergence_table(data)
    convergence.to_csv(out / "convergence.csv", index=False)

    write_summary_table(summary, paired, r3_summary, radius, out, convergence)

    headline = {
        "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "ci": "seed-bootstrap 95% percentile interval of the mean",
        "sign_test": "exact two-sided binomial sign test, zeros dropped",
        "radius_gap_vs_h1_t60_r": {
            arm: float(g["radius_gap"].corr(g["h1_t60"])) for arm, g in radius.groupby("arm")
            if g["radius_gap"].std() > 1e-12
        },
        "radius_gap_vs_h1_t60_r_seeds0_7": {
            arm: float(g[g["seed"] < 8]["radius_gap"].corr(g[g["seed"] < 8]["h1_t60"]))
            for arm, g in radius.groupby("arm") if g["radius_gap"].std() > 1e-12
        },
    }
    (out / "analysis.json").write_text(json.dumps(headline, indent=2) + "\n")

    import matplotlib

    matplotlib.use("Agg")
    arms = set(data["arm"])
    made = []
    if {"primary", "control"} <= arms:
        made.append(figure_r1(contrasts, data, figures, rng))
        made.append(figure_r5(contrasts, figures))
        if contrasts["n_units"].nunique() > 1:
            made.append(figure_r4(contrasts, figures, rng))
    if {"primary_gain", "control_gain"} & arms:
        made.append(figure_r2(contrasts, radius[radius["arm"].isin(["primary", "control"])], figures, rng))
    for arm in FROZEN_ARMS:
        if arm in arms and r3_cells(data, 200, arm) is not None:
            made.append(figure_r3(data, figures, arm))
    if "control_random" in arms:
        made.append(figure_random_subset(contrasts, data, figures, rng))
    for path in made:
        print(path)


def _fmt(row) -> str:
    return (f"{row['mean']:+.3f} [{row['ci_low']:+.3f}, {row['ci_high']:+.3f}], "
            f"{row['n_positive']}/{row['n_seeds']} +, p={row['sign_test_p']:.3g}")


def write_summary_table(summary, paired, r3_summary, radius, out: Path, convergence=None) -> None:
    def pick(frame, **keys):
        sel = frame
        for key, value in keys.items():
            sel = sel[sel[key] == value]
        return None if sel.empty else sel.iloc[0]

    lines = [
        "# Does the sign reversal survive?",
        "",
        "H1 = NMSE(p=0.05) - mean NMSE(p=0.10, 0.20, 0.40); positive = denser networks better.",
        "Cells: mean [seed-bootstrap 95% CI], seeds with positive H1, exact two-sided sign-test p.",
        "Reversal survives = all-trainable H1 CI > 0 and equal-budget H1 CI < 0.",
        "",
        "| Check | N | Seeds | Trial | All edges trainable H1 | Equal budget H1 | Paired change (primary - control) | Reversal survives? |",
        "|---|---:|---|---:|---|---|---|---|",
    ]
    checks = []
    for trial in REPORT:
        checks.append(("R1 convergence" if trial != 60 else "Original snapshot (R1 at 60)", "", 200, "0-7", trial))
    seeds16 = sorted(set(summary["seeds"]) - {"0-7"})
    for label in ["0-7"] + seeds16:
        for trial in (60, 200):
            checks.append(("R2 gain-matched", "_gain", 200, label, trial))
    for trial in (60, 200):
        checks.append(("B3 random-subset budget", "_random", 200, "0-7", trial))
    for n_units in (100, 400):
        for trial in (60, 200):
            checks.append(("R4 network size", "", n_units, "0-7", trial))
    for label in seeds16:
        for trial in (60, 200):
            checks.append(("R5 more seeds", "", 200, label, trial))
    arms_of = {suffix: (primary_arm, control_arm) for primary_arm, control_arm, suffix in PAIRS}
    for name, suffix, n_units, seeds, trial in checks:
        primary_arm, control_arm = arms_of[suffix]
        p = pick(summary, arm=primary_arm, n_units=n_units, checkpoint_trial=trial, seeds=seeds, contrast="h1")
        c = pick(summary, arm=control_arm, n_units=n_units, checkpoint_trial=trial, seeds=seeds, contrast="h1")
        d = pick(paired, pair="primary-control" + suffix, n_units=n_units, checkpoint_trial=trial, seeds=seeds, contrast="h1")
        if p is None or c is None:
            if seeds != "0-7":
                continue  # extra seed set for an arm that has none
            lines.append(f"| {name} | {n_units} | {seeds} | {trial} | not run | not run | not run | pending |")
            continue
        verdict = "yes" if (sign_label(p), sign_label(c)) == ("+", "-") else f"no ({sign_label(p)} / {sign_label(c)})"
        lines.append(f"| {name} | {n_units} | {seeds} | {trial} | {_fmt(p)} | {_fmt(c)} | "
                     f"{_fmt(d) if d is not None else 'n/a'} | {verdict} |")
    lines += ["", "Sign codes in the verdict: + CI above 0, - CI below 0, 0 CI includes 0 (primary / control).",
              "B3: equal-budget arm = a random subset of each structural mask (same per-seed budget as p = 0.05),",
              "compared with the all-trainable arm of the same seeds.", ""]
    titles = {
        "frozen": "## R3 frozen-drive ablation (N = 200, total gain matched)",
        "frozen_unmatched": ("## R3 variant with unmatched total gain (N = 200): trainable edges keep the "
                             "p = 0.05 scale, frozen edges as in R3, total variance g^2 (1 + f)"),
    }
    for arm in FROZEN_ARMS:
        part = r3_summary[r3_summary["arm"] == arm] if not r3_summary.empty else r3_summary
        if part.empty:
            continue
        seed_labels = list(dict.fromkeys(part["seeds"]))
        lines += [
            titles[arm],
            "",
            "density_f*: NMSE(p=0.10) - mean NMSE(p=0.20, 0.40) at a fixed frozen share f (+ = denser better).",
            "frozen_p*: NMSE(f=0) - mean NMSE(f=0.5, 0.75, 0.875) at fixed structural density (+ = more frozen drive better).",
            "slope_logp: change in NMSE per doubling of density at fixed f; slope_f: change in NMSE per unit f at fixed density.",
            "diag_h1: f = 0 minus the factorial's diagonal (for the gain-matched arm, the equal-budget control H1).",
        ]
        if arm != "frozen":
            lines.append("shrink_f*: mean over p of NMSE(gain-matched R3) - NMSE(unmatched) at fixed f "
                         "(+ = keeping full-size trainable weights is better).")
        header = " | ".join(f"Seeds {label}, trial {trial}" for label in seed_labels for trial in (60, 200))
        lines += ["", f"| Contrast | {header} |", "|---|" + "---|" * (2 * len(seed_labels))]
        for contrast in part["contrast"].unique():
            cells = []
            for label in seed_labels:
                for trial in (60, 200):
                    row = pick(part, contrast=contrast, checkpoint_trial=trial, seeds=label)
                    cells.append(_fmt(row) if row is not None else "n/a")
            lines.append(f"| {contrast} | " + " | ".join(cells) + " |")
        lines.append("")
    if not radius.empty:
        lines += ["## Initial spectral-radius gap vs H1 at trial 60 (N = 200)", ""]
        for arm, group in radius.groupby("arm"):
            if group["radius_gap"].std() < 1e-12:
                lines.append(f"- {arm}: radius gap is zero by construction.")
                continue
            subsets = [("seeds 0-7", group[group["seed"] < 8])]
            if len(group) > 8:
                subsets.append((f"all {len(group)} seeds", group))
            for label, part in subsets:
                lines.append(f"- {arm}, {label}: r = {part['radius_gap'].corr(part['h1_t60']):+.2f}")
        lines.append("")
    if convergence is not None and not convergence.empty:
        lines += ["## Convergence: networks still improving between checkpoints", "",
                  "| Arm | N | From | To | Improving / networks | Median relative NMSE change |",
                  "|---|---:|---:|---:|---|---:|"]
        for _, row in convergence.iterrows():
            lines.append(f"| {row['arm']} | {row['n_units']} | {row['from_trial']} | {row['to_trial']} | "
                         f"{row['n_improving']}/{row['n_networks']} | {row['median_relative_change']:+.3f} |")
        lines.append("")
    (out / "summary_table.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
