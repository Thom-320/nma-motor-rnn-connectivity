# Equal-plasticity follow-up control

## Question

The primary Q2 experiment changes two things together when it raises the
recurrent connection probability $p$:

1. the number of structural recurrent edges; and
2. the number of recurrent weights available to the learning rule.

The follow-up asks whether the density contrast remains when the second
quantity is held fixed.

## Design

The control uses the primary configuration: $N=200$, $p \in
\{0.05, 0.10, 0.20, 0.40\}$, 60 training trials, 30 balanced held-out trials
per checkpoint, and eight network seeds. Within each seed, conditions share
the same underlying random weights, input weights, decoder, target order and
initial states, as in Q2.

For each seed, the smallest structural mask determines the recurrent
plasticity budget. Every density receives that same number of trainable
recurrent edges. The extra structural edges in denser conditions remain in
the recurrent matrix but are frozen during learning. The trainable mask is
selected from the existing paired randomness; the control does not draw a new
random stream.

This isolates the number of trainable recurrent edges from the density change
within this architecture. It does not make frozen dense edges equivalent to
plastic edges, and it does not establish a universal causal effect of density.

## Results

The table reports the mean final held-out velocity NMSE across the eight
network seeds. Lower is better.

| Connection probability $p$ | Primary: all existing edges plastic | Control: equal plasticity budget |
| ---: | ---: | ---: |
| 0.05 | 0.424 | 0.424 |
| 0.10 | 0.331 | 0.524 |
| 0.20 | 0.276 | 0.488 |
| 0.40 | 0.133 | 0.530 |

Under the equal-plasticity control, the sparse condition was not worse than
the denser conditions in this run. The seed-level contrast used by the
primary hypothesis, sparse NMSE minus the mean denser NMSE, averaged $-0.090$
with a seed-bootstrap 95% percentile interval of $[-0.113, -0.068]$. The
second contrast, which tests diminishing returns, averaged $-0.023$ with a
95% interval of $[-0.269, 0.202]$.

These are descriptive summaries from eight network seeds, not a general claim
that sparsity is better. They show that the primary all-edges-plastic result
cannot be interpreted as a density-only effect: changing the plasticity
budget changes the conclusion in this implementation.

## Reproduce

From the repository root:

```bash
uv run python scripts/generate_equal_plasticity_control.py
```

The script writes its own artifacts under `results/equal_plasticity/`:

- `checkpoints.csv` — held-out checkpoints for every seed and density;
- `conditions.csv` — final condition summaries, including structural and
  trainable edge counts;
- `hypothesis_contrasts.csv` — seed-level H1/H2 contrasts;
- `analysis.json` — reproducible bootstrap settings and summary intervals;
- `config.json` — the complete configuration and seed list; and
- `figures/` — the same four diagnostic figures used for Q2.

The command does not overwrite `results/primary/`. The notebook and primary
Q2 claim still refer to the all-existing-edges-plastic architecture; this
follow-up is an additional control, not a silent replacement.
