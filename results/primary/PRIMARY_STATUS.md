# Primary experiment status

The preregistered primary experiment completed successfully with \(N=200\), eight paired seeds, four densities, 60 training trials, and 30 balanced held-out trials per checkpoint.

- Runtime: 357.91 seconds (5.97 minutes).
- Output: 416 checkpoint rows and 32 condition summaries.
- All four required figures and the seed-level hypothesis contrast table were generated.

## Primary performance results

| p | Mean final NMSE | Mean learning-curve AUC | Mean final D_PR | Mean final D90 |
|---:|---:|---:|---:|---:|
| 0.05 | 0.424 | 0.655 | 3.528 | 10.125 |
| 0.10 | 0.331 | 0.581 | 3.069 | 8.125 |
| 0.20 | 0.276 | 0.422 | 2.651 | 4.125 |
| 0.40 | 0.133 | 0.382 | 2.556 | 3.125 |

### H1: low-density impairment

For each seed, H1 was calculated as final NMSE at \(p=0.05\) minus the average final NMSE at \(p=0.10,0.20,0.40\). Positive values support H1.

- Positive in 8 of 8 seeds.
- Mean paired contrast: 0.177.
- Seed-bootstrap 95% interval for the mean: [0.136, 0.219].

Within this preregistered design, the result supports worse final held-out performance at \(p=0.05\) than the average moderate/higher-density condition.

### H2: diminishing returns

H2 compared the improvement from \(p=0.05\) to \(p=0.20\) with the improvement from \(p=0.20\) to \(p=0.40\). Positive values support diminishing returns.

- Positive in 3 of 8 seeds.
- Mean paired contrast: 0.005.
- Seed-bootstrap 95% interval for the mean: [-0.081, 0.097].

H2 is not supported consistently. The observed primary means continue to improve through \(p=0.40\), so these data do not justify a performance plateau within the tested range.

## Exploratory manifold result

Participation-ratio dimensionality decreased as density increased, while held-out performance improved. Across all 32 conditions, the descriptive Pearson correlation between final \(D_{PR}\) and final NMSE was \(r=0.671\): higher dimensionality was associated with larger error, not better performance. This is an exploratory association confounded with density and does not establish a causal manifold mechanism.

## Claim boundary

The defensible result is: under the paired initialization, variance scaling, fixed decoder, and all-existing-weights-plastic learning rule used here, very sparse \(N=200\) networks performed worse than moderate/higher-density networks on held-out six-direction reaching. The result does not identify a critical density, does not establish diminishing returns, and does not isolate structural density from the number of plastic weights.

The contradictory \(N=100\) pilot remains part of the record. It may indicate finite-size sensitivity, but testing a network-size-by-density interaction was not preregistered and is outside the current claim.
