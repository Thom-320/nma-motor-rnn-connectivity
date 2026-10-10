# Cloud session, 9 October 2026: robustness checks R1–R5

Branch `robustness-2026-10`, created from `main` at `0cd97e0`. Nothing on
`main` was changed and no existing results file was modified. All new outputs
are under `results/robustness/`.

## Environment and timing

- **Machine.** Cloud container with 4 CPU cores and 15 GB RAM; Python 3.13,
  NumPy/pandas/matplotlib; BLAS pinned to one thread per process.
- **One primary run first.** Seed 0, $N=200$, four densities, 60 trials took
  **82 s** serially (13.2 / 15.5 / 19.3 / 34.5 s for p = 0.05 / 0.10 / 0.20 /
  0.40). The final NMSEs matched `results/primary/conditions.csv` exactly.
- **Further probes.** $N=400$, $p=0.40$ costs 3.5 s per training trial, about
  7× the $N=200$ cost. Four parallel processes scale about 3.5× (5.1 s alone vs 5.4–6.0 s each with four at once).
- **Estimate.** The full grid at 200 trials is about 24 000 core-seconds,
  i.e. 100–120 min of wall time on 4 cores. That is at the edge of the
  ~2 h budget. I therefore ran everything here in priority order
  (R1 → R2 → R3 → R5 → R4 $N=100$ → R4 $N=400$) and also wrote Kaggle shards
  for R4/R5 as a fallback and for independent replication.

Wall-clock times (4 workers, start 16:34:20 UTC):

| Block | Networks | Finished (UTC) | Wall time | Core-seconds |
|---|---:|---|---:|---:|
| R1: primary + control, $N=200$, seeds 0–7 | 64 | 16:48:49 | 14.5 min | ≈ 3 400 |
| R2: gain-matched primary + control | 64 | 17:03:17 | 14.5 min | 3 443 |
| R3: frozen-drive factorial (10 cells) | 80 | 17:17:40 | 14.4 min | 3 459 |
| R5: primary + control, seeds 8–15 | 64 | 17:31:40 | 14.0 min | ≈ 3 400 |
| R4: $N=100$, primary + control, seeds 0–7 | 64 | 17:37:24 | 5.7 min | 1 409 |
| R4: $N=400$, primary + control, seeds 0–7 | 64 | 18:29:27 | 52.0 min | 12 413 |
| **Total** | **400** | | **115.1 min (6 904 s)** | |

The R1 + R5 core-seconds are recorded together in
`results/robustness/{primary,control}_N200/config.json` (4 084 + 2 704).

## What was added

**Code**
- `src/nma_motor_rnn/connectivity.py`:
  - `make_extended_shared_randomness`: 200-trial runs whose first 60 trials and
    held-out set are identical to the 60-trial runs;
  - `initial_recurrent_weights`, `spectral_radius`, `gain_match_scale` (R2);
  - `frozen_drive_weights` (R3);
  - an optional `initial_weights` argument to `MotorRNN` / `train_condition`.

  Default behaviour is unchanged: the 15 original tests pass, and seed 0
  reproduces the committed primary run exactly.
- `src/nma_motor_rnn/robustness.py`: the arm definitions and a resumable
  per-network runner (`python -m nma_motor_rnn.robustness run|collect`).
- **Scripts:**
  - `scripts/run_robustness_grid.py` runs the whole grid in priority order;
  - `scripts/analyze_robustness.py` produces every table and figure;
  - `scripts/make_kaggle_shards.py` writes `kaggle/`.
- **Tests:** `tests/test_robustness.py` adds 14 tests (29 in total, all
  passing). They cover:
  - prefix identity of the extended randomness, including an exact checkpoint
    match;
  - equal spectral radii after gain matching;
  - R3 reducing exactly to the control on its diagonal and to $p=0.05$ at
    $f=0$;
  - an identical trainable sub-network across density at fixed $f$;
  - the frozen variance share;
  - frozen edges never changing during training;
  - rejection of degenerate arguments.

**Configurations** (every network: 200 trials, evaluated every 10 trials;
the reported checkpoints are 60 / 100 / 150 / 200)

| ID | Arms | N | Seeds |
|---|---|---|---|
| R1 | `primary`, `control` | 200 | 0–7 |
| R2 | `primary_gain`, `control_gain`: initial $W$ rescaled to $\rho(W_{0.05})$ of the same seed | 200 | 0–7 |
| R3 | `frozen`: $p\in\{0.10,0.20,0.40\}\times f\in\{0.5,0.75,0.875\}$ plus $f=0$ | 200 | 0–7 |
| R4 | `primary`, `control` | 100, 400 (200 = R1) | 0–7 |
| R5 | `primary`, `control` | 200 | 0–15 |

Masks stay nested and all randomness is shared within a seed across every
condition and arm.

### Why R3 isolates the mechanism

In the equal-budget control, increasing $p$ changes three things together:
1. the number of frozen edges (density);
2. the share of recurrent input variance that is frozen,
   $f_p = (p-0.05)/p$ = 0, 0.5, 0.75 or 0.875;
3. the size of the trainable weights.

R3 sets the trainable weights to $g\sqrt{1-f}/\sqrt{0.05N}\,G$ on the
$p=0.05$ edges and the frozen weights to $g\sqrt{f}/\sqrt{(p-0.05)N}\,G$ on
the remaining edges of $M_p$.
- **Fixed $f$, varying $p$.** The trainable sub-network is bit-identical and
  the frozen variance is the same. Only the number of edges carrying it
  changes, which is pure density.
- **Fixed $p$, varying $f$.** The edge set is identical. Only the frozen share
  changes.
- **Anchors.** The diagonal reproduces the control networks exactly (verified:
  identical NMSE in all 8 seeds), and $f=0$ reproduces the $p=0.05$ network.
- **No degenerate design.** We do not delete the frozen edges, which would
  collapse every condition to $p=0.05$. Total input variance stays $g^2$, so
  "more frozen input" is not confounded with "more gain".

## Results (exact numbers)

All numbers come from `results/robustness/analysis/` (bootstrap: 100 000
resamples, seed 20261009; exact two-sided sign test). H1 > 0 means denser is
better.

### Reproduction of the existing results

The trial-60 checkpoints of the R1 runs match `results/primary` and
`results/equal_plasticity` within 1.2e-12 on all 224 overlapping checkpoints.
They reproduce the published contrasts:
- primary: +0.177 [0.136, 0.220], 8/8;
- control: −0.090 [−0.113, −0.068], 0/8 positive.

### Summary: does the sign reversal survive?

Reversal = primary CI above 0 *and* control CI below 0.

| Check | All edges trainable H1 | Equal-budget H1 | Paired change | Reversal |
|---|---|---|---|---|
| Original (R1 @ 60, 8 seeds) | +0.177 [0.136, 0.220], 8/8 | −0.090 [−0.113, −0.068], 0/8 | +0.267 [0.232, 0.304], 8/8 | yes |
| R1 @ 100 | +0.208 [0.179, 0.228], 8/8 | −0.064 [−0.095, −0.034], 1/8 | +0.272, 8/8 | yes |
| R1 @ 150 | +0.202 [0.159, 0.242], 8/8 | −0.069 [−0.091, −0.049], 0/8 | +0.270, 8/8 | yes |
| R1 @ 200 | +0.199 [0.157, 0.243], 8/8 | −0.062 [−0.099, −0.028], 1/8 | +0.261 [0.228, 0.296], 8/8 | yes |
| R2 gain-matched @ 60 | +0.153 [0.076, 0.224], 7/8 | −0.068 [−0.117, −0.024], 0/8 | +0.222 [0.174, 0.273], 8/8 | yes |
| R2 gain-matched @ 200 | +0.184 [0.098, 0.258], 7/8 | −0.045 [−0.108, +0.009], 3/8 | +0.229 [0.184, 0.279], 8/8 | **no** (control CI includes 0) |
| R5 16 seeds @ 60 | +0.190 [0.154, 0.229], 16/16 | −0.041 [−0.083, +0.011], 3/16 | +0.231 [0.193, 0.267], 16/16 | **no** (control CI includes 0) |
| R5 16 seeds @ 200 | +0.173 [0.135, 0.210], 16/16 | −0.055 [−0.100, −0.011], 4/16 | +0.229 [0.191, 0.265], 16/16 | yes |
| R4 $N=100$ @ 60 | +0.007 [−0.104, 0.118], 4/8 | −0.048 [−0.097, +0.002], 1/8 | +0.055 [−0.028, 0.138], 5/8 | **no** (neither CI excludes 0) |
| R4 $N=100$ @ 200 | +0.095 [−0.029, 0.216], 5/8 | −0.084 [−0.142, −0.023], 2/8 | +0.179 [0.096, 0.273], 8/8 | **no** (primary CI includes 0) |
| R4 $N=400$ @ 60 | +0.062 [0.043, 0.077], 8/8 | −0.025 [−0.042, −0.008], 2/8 | +0.086 [0.077, 0.097], 8/8 | yes |
| R4 $N=400$ @ 200 | +0.055 [0.040, 0.068], 8/8 | −0.014 [−0.027, −0.002], 2/8 | +0.069 [0.060, 0.079], 8/8 | yes |

The full table, including sign-test p-values, is in
`results/robustness/analysis/summary_table.md`.

### R3: frozen drive vs density (8 seeds)

| Contrast | Trial 60 | Trial 200 |
|---|---|---|
| density at f = 0.5 (+ = denser better) | +0.011 [−0.059, 0.088] | +0.003 [−0.081, 0.116] |
| density at f = 0.75 | +0.064 [−0.057, 0.187] | +0.008 [−0.082, 0.094] |
| density at f = 0.875 | +0.106 [−0.007, 0.215] | +0.026 [−0.100, 0.152] |
| NMSE slope per doubling of p (fixed f) | −0.014 [−0.076, 0.055] | +0.005 [−0.052, 0.064] |
| frozen drive at p = 0.10: NMSE(f=0) − mean NMSE(f ≥ 0.5) | −0.126 [−0.195, −0.051] | −0.068 [−0.132, −0.003] |
| frozen drive at p = 0.20 | −0.034 [−0.103, 0.029] | −0.033 [−0.107, 0.025] |
| frozen drive at p = 0.40 | −0.098 [−0.181, −0.014] | −0.078 [−0.150, −0.007] |
| NMSE slope per unit f (fixed p, f ∈ [0.5, 0.875]) | −0.050 [−0.189, 0.073] | −0.013 [−0.070, 0.041] |

**Reading.** Density at a fixed frozen share has no detectable effect.
Adding frozen drive (f: 0 → ≥ 0.5) costs about 0.03–0.13 NMSE, and the cost
does not grow with f. The control's negative H1 is the $f=0$ vs $f>0$ step,
not a density effect. Caveat: 8 seeds, so the individual sign tests are not
significant.

### Convergence (R1, $N=200$, seeds 0–7, 32 networks per arm)

| Arm | Improving 50→60 | Improving 150→200 | Improving 190→200 |
|---|---|---|---|
| primary | 23/32 (median −6.1 %) | 23/32 (−11.4 %) | 17/32 (−1.4 %) |
| control | 22/32 (−2.3 %) | 26/32 (−7.1 %) | 15/32 (+0.1 %) |

Mean NMSE keeps falling to trial 200. H1 has been flat since about trial 40
in both arms.

### Spectral radius

- **Seeds 0–7.** The sparse-minus-denser initial radius gap correlates with
  the trial-60 H1 at r = −0.90 (primary), reproducing the audit, and
  r = −0.43 (control).
- **All 16 seeds.** r = −0.26 (primary) and +0.20 (control).

The strong correlation does not replicate. R2, which removes the gap by
construction, leaves the primary advantage and the paired change intact.

## Things that contradict or qualify the existing README and docs

1. **"Sign reversal" is too strong.** README and `EQUAL_PLASTICITY_CONTROL.md`
   report the control H1 from 8 seeds (−0.090). With 16 seeds it is −0.041 at
   trial 60, with a CI that includes 0. Seeds 8–15 alone average +0.008. The
   direction holds (12–13/16 seeds) and is clearer after 200 trials (−0.055
   [−0.100, −0.011]), but it is not robust to gain matching at trial 200. I
   updated the README to state the 8-seed reversal precisely and to point
   here; the defensible headline is that the advantage *disappears* (paired
   change +0.23, 16/16), with a small residual reversal.
2. **The reversal is not a density effect.** The README's earlier framing
   ("can't tell which of the two did the work") is now answered for this
   model: the number of trainable edges does the work. The residual reversal
   comes from frozen recurrent drive (R3).
3. **"Preregistered" / "Confirmatory".** Neither is supported by git history
   (both appeared in `3021081` together with the results). Fixed in:
   - the `hypothesis_contrasts` docstring;
   - the notebook text and its generator (`scripts/build_notebook.py`);
   - a provenance paragraph in `RESEARCH_OVERVIEW.md`.

   The original "Confirmatory hypotheses" heading lived in
   `docs/LITERATURE_REVIEW.md` at `3021081` and was already removed from
   `main`.
4. **The $N=100$ pilot.** `results/pilot/PILOT_STATUS.md` guessed that at
   $N=100$ "nothing really learns". R4 confirms it: NMSE 0.75–0.85 at trial
   60, and the primary H1 is not distinguishable from 0 (+0.007
   [−0.104, 0.118]). The pilot's opposite sign is consistent with noise in a
   poorly-learning regime, not with a robust size interaction.
5. **The r = −0.90 radius correlation** cited by the audit does not hold
   beyond seeds 0–7.
6. **RESEARCH_OVERVIEW** gives the primary H1 CI as [0.136, 0.219]; the
   bootstrap here gives [0.136, 0.220]. That is ordinary Monte-Carlo
   variation, not a discrepancy.

## What remains

- **Nothing is required on Kaggle:** the full grid ran here.
  `kaggle/` contains four shards that reproduce R4/R5 independently:
  - `r4-n400-seeds0-3`
  - `r4-n400-seeds4-7`
  - `r4-n100-seeds0-7`
  - `r5-n200-seeds8-15`

  Each `run.py` clones this branch, installs it, runs its slice on 4 CPU
  workers and writes CSVs plus `SOURCE_COMMIT.txt` to `/kaggle/working`.
  `kernel-metadata.json` is set to CPU, no GPU, internet on, private. Replace
  `KAGGLE_USERNAME` in every `kernel-metadata.json`, then run
  `kaggle kernels push -p kaggle/<shard>`. Copy the downloaded
  `robustness/raw/<arm>_N<N>/` folders into `results/robustness/raw/`, then
  run `python -m nma_motor_rnn.robustness collect` and
  `python scripts/analyze_robustness.py`. Expected wall time per $N=400$
  shard: about 30 min.
- **Worth running before submission** (not requested, not run):
  - 16 seeds for R2 and R3: R3 at 8 seeds is the weakest link of the new
    story;
  - training beyond 200 trials;
  - an alternative budget-matching scheme (a random subset of each dense mask
    instead of the sparse edges);
  - an R3 variant with unmatched total gain, to separate "frozen drive" from
    "smaller trainable weights".
- **Thomas:** fill in the authorship block in `paper/NOTE.md` and check the
  reference list.

## Session 2 (10 October 2026)

Same branch, same container type (4 cores). This session ran the four
"worth running before submission" checks above, in that priority order. Training
beyond 200 trials was not requested and was not run.

### Wall time

Budget: stop adding blocks past about 2.5 h. All four blocks fit, so nothing
was skipped.

| Block | Networks | Start → end (UTC) | Wall time | Core-seconds |
|---|---:|---|---:|---:|
| R2x: R2 gain-matched primary + control, seeds 8–15 | 64 | 15:35:04 → 15:52:02 | 1 017.7 s (17.0 min) | 4 042 |
| R3x: R3 frozen-drive factorial, seeds 8–15 | 80 | 15:52:02 → 16:06:30 | 866.8 s (14.4 min) | 3 439 |
| B3: equal budget, random subset of each mask, seeds 0–7 | 32 | 16:06:34 → 16:12:49 | 374.6 s (6.2 min) | 1 478 |
| B4: R3 with unmatched total gain, seeds 0–7 | 72 | 16:12:49 → 16:26:35 | 826.5 s (13.8 min) | 3 244 |
| **Total** | **248** | | **3 085.6 s (51.4 min)** | **12 203** |

Per-block logs are in `results/robustness/logs/session2_*.log`. R2x ran
slightly slower than R2 did in session 1 because an extra process was running
for part of it.

### What was added

- **`make_random_subset_plasticity_masks`** (`connectivity.py`). Equal-budget
  masks whose trainable edges are a uniform random subset of each structural
  mask $M_p$. The budget per seed is the same as in the original control, the
  size of $M_{0.05}$. The subset is chosen by a priority field drawn from
  `default_rng([seed, 2])`, so the shared stream is untouched. At $p=0.05$ the
  subset is the whole mask. Arm: `control_random`.
- **`frozen_drive_weights(..., match_total_gain=False)`.** In this variant the
  trainable edges keep the $p=0.05$ scale $g/\sqrt{0.05N}$ and the frozen edges
  are exactly as in R3, so the total variance is $g^2(1+f)$. On the diagonal
  both edge sets keep their original scales. Arm: `frozen_unmatched`, 9 cells.
  Its $f=0$ cell is the `frozen` arm's $f=0$ network (the same network) and is
  not re-run.
- **`scripts/run_robustness_grid.py`.** New blocks `R2x`, `R3x`, `B3` and
  `B4`. The default `--only` remains R1–R5.
- **`scripts/analyze_robustness.py`.**
  - Reports R2 and R3 for seeds 0–7 and 0–15.
  - Adds the B3 pair (primary vs `control_random`) to the summary table.
  - Adds an R3 section for the unmatched variant, with `shrink_f*`
    (gain-matched minus unmatched NMSE at fixed $f$).
  - New figures: `B3_random_subset.png` and `R3_unmatched_gain.png`.
  - With the old data, all old numbers are reproduced unchanged.
- **Tests.** 11 new tests (40 in total, all passing):
  - the random-subset budget equals the sparse mask size;
  - the subsets lie inside their masks and contain no self-connections;
  - $p=0.05$ is fully trainable;
  - dense subsets overlap the sparse edges at about the rate $0.05/p$;
  - reproducibility, and the shared stream is untouched;
  - the arm wiring is correct;
  - in the unmatched variant: the trainable part is the sparse network at
    every $f$, the frozen part matches R3, both scales hold on the diagonal,
    total variance is $g^2(1+f)$, and the arm wiring is correct.

**Identity checks on the new runs (all exact, max |Δ NMSE| = 0):**
- the $p=0.05$ cells of `primary_gain` and `control_gain` for seeds 0–15
  against `primary` (336 checkpoints each);
- the R3 diagonal and $f=0$ cells against `control` for all 16 seeds;
- `control_random` at $p=0.05$ against `primary` (168 checkpoints).

### Results (exact numbers)

Same statistics as in session 1: bootstrap with 100 000 resamples, seed
20261009, and an exact two-sided sign test.

**1. R2 with 16 seeds.**

| | Trial 60 | Trial 200 |
|---|---|---|
| Primary (gain-matched) H1 | +0.178 [0.127, 0.227], 15/16 + | +0.175 [0.128, 0.218], 15/16 + |
| Control (gain-matched) H1 | −0.027 [−0.073, +0.019], 6/16 +, p = 0.45 | −0.039 [−0.086, +0.004], 7/16 +, p = 0.80 |
| Paired change | +0.205 [0.169, 0.242], 16/16 | +0.214 [0.184, 0.249], 16/16 |

- The advantage disappears in 16/16 seeds.
- The gain-matched reversal is gone at both checkpoints, not only at trial 200
  as with 8 seeds.

**2. R3 with 16 seeds.**

*Density at fixed $f$: still null, with tighter intervals.*

| Contrast | Trial 60 | Trial 200 |
|---|---|---|
| density, $f=0.5$ | −0.003 [−0.069, 0.062] | −0.029 [−0.093, 0.042] |
| density, $f=0.75$ | +0.027 [−0.049, 0.104] | −0.021 [−0.077, 0.034] |
| density, $f=0.875$ | +0.041 [−0.038, 0.121] | −0.008 [−0.078, 0.065] |
| `slope_logp` (per doubling of $p$) | +0.002 [−0.037, 0.043] | +0.014 [−0.018, 0.047] |

*Frozen-drive step: weaker than with 8 seeds.* The contrast is $f=0$ minus
the mean over $f \ge 0.5$.

| Density | Trial 60 | Trial 200 |
|---|---|---|
| $p=0.10$ | −0.056 [−0.116, 0.003] | −0.045 [−0.092, 0.001] |
| $p=0.20$ | −0.009 [−0.067, 0.052] | −0.056 [−0.110, −0.001] |
| $p=0.40$ | −0.061 [−0.124, 0.007] | −0.074 [−0.129, −0.022] |

- 4–7 of 16 seeds are positive in each cell; every sign test has $p \ge 0.077$.
- `slope_f` is −0.058 [−0.151, 0.029] at trial 60 and −0.005 [−0.058, 0.043]
  at trial 200.

**3. B3, random-subset budget, 8 seeds.**

| | Trial 60 | Trial 200 |
|---|---|---|
| Equal-budget H1 | −0.069 [−0.125, −0.015], 2/8 + | −0.049 [−0.083, −0.017], 2/8 + |
| Paired change vs primary | +0.246 [0.170, 0.317], 8/8 | +0.248 [0.207, 0.285], 8/8 |

- Mean NMSE at trial 200 for $p$ = 0.05 / 0.10 / 0.20 / 0.40: 0.334 / 0.384 /
  0.332 / 0.432.
- For comparison, the sparse-edge control gives 0.334 / 0.397 / 0.375 / 0.415.

**4. B4, unmatched total gain, 8 seeds.**

- **Mean NMSE at trial 200.** 0.53–0.72 for the nine cells, against 0.334 at
  $f=0$. The initial spectral radius is 1.90–2.16, against about 1.56 in R3.
- **Frozen-drive cost** ($f=0$ minus the mean over $f \ge 0.5$), 8/8 seeds in
  every cell:

  | Density | Trial 60 | Trial 200 |
  |---|---|---|
  | $p=0.10$ | −0.350 [−0.433, −0.261] | −0.321 [−0.391, −0.252] |
  | $p=0.20$ | −0.303 [−0.378, −0.230] | −0.304 [−0.349, −0.262] |
  | $p=0.40$ | −0.332 [−0.382, −0.282] | −0.335 [−0.381, −0.288] |

- **`slope_f`:** +0.310 [0.203, 0.434] at trial 60 and +0.350 [0.273, 0.426]
  at trial 200, 8/8. More frozen drive is monotonically worse.
- **`slope_logp`:** −0.009 [−0.045, 0.023] and +0.007 [−0.024, 0.037]. Density
  is again null.
- **`shrink_mean`** (gain-matched R3 minus unmatched, averaged over cells):
  −0.242 [−0.294, −0.195] at trial 60 and −0.260 [−0.300, −0.222] at trial 200,
  8/8. The gain-matched cells, with their smaller trainable weights, are
  better.

### Change to the story

**Headline kept and strengthened.** "The density advantage disappears under an
equal trainable budget" now holds:
- under gain matching with 16 seeds (16/16);
- under a second budget-matching scheme (8/8).

**Second half weakened.** The old wording was "the residual reversal comes
from frozen recurrent drive". Three things changed:
- The residual reversal itself is not robust. With gain matching and 16 seeds
  its interval includes 0 at both checkpoints, and 9–10 of 16 seeds are
  negative. The B3 reversal (8 seeds) is about as large as the original 8-seed
  control was before it halved.
- "Not a density effect" is now the best-supported R3 claim: the 16-seed
  density contrasts and slopes are all near 0 with narrower intervals.
- The frozen-drive step, with 16 seeds, is distinguishable from 0 only at trial
  200, and only for $p$ = 0.20 and 0.40, with no significant sign test.
  B4 rules out "smaller trainable weights" as its source: at equal frozen drive,
  full-size trainable weights are much worse. B4 cannot separate frozen drive
  from the extra total gain it introduces.

**New headline in `paper/NOTE.md`:** "the density advantage disappears under an
equal trainable budget; any residual handicap of denser equal-budget networks
is small, not robust to gain matching, and not a density effect — most
plausibly a cost of frozen recurrent drive, but that attribution is weak."

### Still open

- **The missing 2 × 2 cell.** Shrunken trainable weights with the frozen edges
  deleted would separate frozen drive from total gain. It costs about 24
  networks at $p=0.05$, roughly 5 min on 4 cores.
- **B3 and B4 at 16 seeds.** About 6 and 14 min.
- **Training beyond 200 trials.**
