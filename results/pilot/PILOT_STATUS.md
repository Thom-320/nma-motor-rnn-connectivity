# The pilot disagreed

Worth keeping in plain sight: the small pilot pointed the *opposite* way from the main run.

$N=100$, three seeds, four densities, 40 trials.

| p | Final NMSE | AUC | D_PR |
|---:|---:|---:|---:|
| 0.05 | 0.768 | 0.863 | 3.537 |
| 0.10 | 0.816 | 0.990 | 3.482 |
| 0.20 | 0.784 | 0.955 | 3.129 |
| 0.40 | 0.911 | 1.202 | 3.561 |

Here the sparsest networks did *best* and the densest did *worst* — the reverse of what we later found at $N=200$. All three seeds went that way.

Three seeds prove nothing, and we didn't touch the plan because of it. But look at the numbers: everything sits near 0.8–0.9, and NMSE of 1.0 means "no better than guessing the average". At $N=100$ nothing really learns, so there's no gap for density to open up. That's a hunch about network size, not a result — we never tested it.

The main run is in the [research overview](../../docs/RESEARCH_OVERVIEW.md).
