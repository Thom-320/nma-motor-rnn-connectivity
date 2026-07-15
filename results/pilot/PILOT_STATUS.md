# Pilot status

The preregistered pilot completed successfully with \(N=100\), three paired seeds, four densities, 40 training trials, and 30 balanced held-out trials per checkpoint.

- First complete runtime: 36.46 seconds.
- Deterministic repeat runtime: 34.89 seconds.
- Output: 108 checkpoint rows and 12 condition summaries.
- All four required figures and the seed-level H1/H2 contrast table were generated.

Mean final held-out NMSE across the three pilot seeds was:

| p | Mean final NMSE | Mean learning-curve AUC | Mean final D_PR |
|---:|---:|---:|---:|
| 0.05 | 0.768 | 0.863 | 3.537 |
| 0.10 | 0.816 | 0.990 | 3.482 |
| 0.20 | 0.784 | 0.955 | 3.129 |
| 0.40 | 0.911 | 1.202 | 3.561 |

All three H1 contrasts were negative, so this pilot does **not** support the preregistered prediction that \(p=0.05\) performs worse than the average moderate/higher-density condition. All three H2 contrasts were positive, but three pilot seeds are not a confirmatory result. The hypotheses and primary design must remain unchanged for the \(N=200\) run.
