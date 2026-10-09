# Does the sign reversal survive?

H1 = NMSE(p=0.05) - mean NMSE(p=0.10, 0.20, 0.40); positive = denser networks better.
Cells: mean [seed-bootstrap 95% CI], seeds with positive H1, exact two-sided sign-test p.
Reversal survives = all-trainable H1 CI > 0 and equal-budget H1 CI < 0.

| Check | N | Seeds | Trial | All edges trainable H1 | Equal budget H1 | Paired change (primary - control) | Reversal survives? |
|---|---:|---|---:|---|---|---|---|
| Original snapshot (R1 at 60) | 200 | 0-7 | 60 | +0.177 [+0.136, +0.220], 8/8 +, p=0.00781 | -0.090 [-0.113, -0.068], 0/8 +, p=0.00781 | +0.267 [+0.232, +0.304], 8/8 +, p=0.00781 | yes |
| R1 convergence | 200 | 0-7 | 100 | +0.208 [+0.179, +0.228], 8/8 +, p=0.00781 | -0.064 [-0.095, -0.034], 1/8 +, p=0.0703 | +0.272 [+0.244, +0.305], 8/8 +, p=0.00781 | yes |
| R1 convergence | 200 | 0-7 | 150 | +0.202 [+0.159, +0.242], 8/8 +, p=0.00781 | -0.069 [-0.091, -0.049], 0/8 +, p=0.00781 | +0.270 [+0.234, +0.311], 8/8 +, p=0.00781 | yes |
| R1 convergence | 200 | 0-7 | 200 | +0.199 [+0.157, +0.243], 8/8 +, p=0.00781 | -0.062 [-0.099, -0.028], 1/8 +, p=0.0703 | +0.261 [+0.228, +0.296], 8/8 +, p=0.00781 | yes |
| R2 gain-matched | 200 | 0-7 | 60 | +0.153 [+0.076, +0.224], 7/8 +, p=0.0703 | -0.068 [-0.117, -0.024], 0/8 +, p=0.00781 | +0.222 [+0.174, +0.273], 8/8 +, p=0.00781 | yes |
| R2 gain-matched | 200 | 0-7 | 200 | +0.184 [+0.098, +0.258], 7/8 +, p=0.0703 | -0.045 [-0.108, +0.009], 3/8 +, p=0.727 | +0.229 [+0.184, +0.279], 8/8 +, p=0.00781 | no (+ / 0) |
| R4 network size | 100 | 0-7 | 60 | +0.007 [-0.104, +0.118], 4/8 +, p=1 | -0.048 [-0.097, +0.002], 1/8 +, p=0.0703 | +0.055 [-0.028, +0.138], 5/8 +, p=0.727 | no (0 / 0) |
| R4 network size | 100 | 0-7 | 200 | +0.095 [-0.029, +0.216], 5/8 +, p=0.727 | -0.084 [-0.142, -0.023], 2/8 +, p=0.289 | +0.179 [+0.096, +0.273], 8/8 +, p=0.00781 | no (0 / -) |
| R4 network size | 400 | 0-7 | 60 | +0.062 [+0.043, +0.077], 8/8 +, p=0.00781 | -0.025 [-0.042, -0.008], 2/8 +, p=0.289 | +0.086 [+0.077, +0.097], 8/8 +, p=0.00781 | yes |
| R4 network size | 400 | 0-7 | 200 | +0.055 [+0.040, +0.068], 8/8 +, p=0.00781 | -0.014 [-0.027, -0.002], 2/8 +, p=0.289 | +0.069 [+0.060, +0.079], 8/8 +, p=0.00781 | yes |
| R5 more seeds | 200 | 0-15 | 60 | +0.190 [+0.154, +0.229], 16/16 +, p=3.05e-05 | -0.041 [-0.083, +0.011], 3/16 +, p=0.0213 | +0.231 [+0.193, +0.267], 16/16 +, p=3.05e-05 | no (+ / 0) |
| R5 more seeds | 200 | 0-15 | 200 | +0.173 [+0.135, +0.210], 16/16 +, p=3.05e-05 | -0.055 [-0.100, -0.011], 4/16 +, p=0.0768 | +0.229 [+0.191, +0.265], 16/16 +, p=3.05e-05 | yes |

Sign codes in the verdict: + CI above 0, - CI below 0, 0 CI includes 0 (primary / control).

## R3 frozen-drive ablation (N = 200, seeds 0-7)

density_f*: NMSE(p=0.10) - mean NMSE(p=0.20, 0.40) at a fixed frozen-variance share f (+ = denser better).
frozen_p*: NMSE(f=0) - mean NMSE(f=0.5, 0.75, 0.875) at fixed structural density (+ = more frozen drive better).
slope_logp: change in NMSE per doubling of density at fixed f; slope_f: change in NMSE per unit f at fixed density.
diag_h1: the equal-budget control H1 rebuilt from the factorial's diagonal.

| Contrast | Trial 60 | Trial 200 |
|---|---|---|
| density_f0.5 | +0.011 [-0.059, +0.088], 4/8 +, p=1 | +0.003 [-0.081, +0.116], 3/8 +, p=0.727 |
| density_f0.75 | +0.064 [-0.057, +0.187], 4/8 +, p=1 | +0.008 [-0.082, +0.094], 4/8 +, p=1 |
| density_f0.875 | +0.106 [-0.007, +0.215], 6/8 +, p=0.289 | +0.026 [-0.100, +0.152], 5/8 +, p=0.727 |
| frozen_p0.1 | -0.126 [-0.195, -0.051], 1/8 +, p=0.0703 | -0.068 [-0.132, -0.003], 3/8 +, p=0.727 |
| frozen_p0.2 | -0.034 [-0.103, +0.029], 3/8 +, p=0.727 | -0.033 [-0.107, +0.025], 3/8 +, p=0.727 |
| frozen_p0.4 | -0.098 [-0.181, -0.014], 2/8 +, p=0.289 | -0.078 [-0.150, -0.007], 2/8 +, p=0.289 |
| diag_h1 | -0.090 [-0.113, -0.068], 0/8 +, p=0.00781 | -0.062 [-0.099, -0.028], 1/8 +, p=0.0703 |
| slope_logp | -0.014 [-0.076, +0.055], 2/8 +, p=0.289 | +0.005 [-0.052, +0.064], 4/8 +, p=1 |
| slope_f | -0.050 [-0.189, +0.073], 3/8 +, p=0.727 | -0.013 [-0.070, +0.041], 4/8 +, p=1 |

## Initial spectral-radius gap vs H1 at trial 60 (N = 200)

- control, seeds 0-7: r = -0.43
- control, all 16 seeds: r = +0.20
- control_gain: radius gap is zero by construction.
- primary, seeds 0-7: r = -0.90
- primary, all 16 seeds: r = -0.26
- primary_gain: radius gap is zero by construction.

## Convergence: networks still improving between checkpoints

| Arm | N | From | To | Improving / networks | Median relative NMSE change |
|---|---:|---:|---:|---|---:|
| control | 100 | 50 | 60 | 24/32 | -0.018 |
| control | 100 | 150 | 200 | 25/32 | -0.032 |
| control | 100 | 190 | 200 | 21/32 | -0.006 |
| control | 200 | 50 | 60 | 49/64 | -0.043 |
| control | 200 | 150 | 200 | 53/64 | -0.059 |
| control | 200 | 190 | 200 | 34/64 | -0.006 |
| control | 400 | 50 | 60 | 30/32 | -0.111 |
| control | 400 | 150 | 200 | 31/32 | -0.090 |
| control | 400 | 190 | 200 | 26/32 | -0.014 |
| control_gain | 200 | 50 | 60 | 24/32 | -0.030 |
| control_gain | 200 | 150 | 200 | 26/32 | -0.071 |
| control_gain | 200 | 190 | 200 | 18/32 | -0.003 |
| frozen | 200 | 50 | 60 | 57/80 | -0.029 |
| frozen | 200 | 150 | 200 | 64/80 | -0.054 |
| frozen | 200 | 190 | 200 | 47/80 | -0.007 |
| primary | 100 | 50 | 60 | 22/32 | -0.026 |
| primary | 100 | 150 | 200 | 24/32 | -0.035 |
| primary | 100 | 190 | 200 | 20/32 | -0.014 |
| primary | 200 | 50 | 60 | 48/64 | -0.086 |
| primary | 200 | 150 | 200 | 54/64 | -0.140 |
| primary | 200 | 190 | 200 | 42/64 | -0.021 |
| primary | 400 | 50 | 60 | 25/32 | -0.121 |
| primary | 400 | 150 | 200 | 27/32 | -0.087 |
| primary | 400 | 190 | 200 | 21/32 | -0.019 |
| primary_gain | 200 | 50 | 60 | 24/32 | -0.064 |
| primary_gain | 200 | 150 | 200 | 22/32 | -0.075 |
| primary_gain | 200 | 190 | 200 | 15/32 | +0.001 |
