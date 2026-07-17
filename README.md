# NMA Motor-RNN Connectivity

[![scientific checks](https://github.com/Thom-320/nma-motor-rnn-connectivity/actions/workflows/tests.yml/badge.svg)](https://github.com/Thom-320/nma-motor-rnn-connectivity/actions/workflows/tests.yml)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Thom-320/nma-motor-rnn-connectivity/blob/main/notebooks/Motor_RNN_Project.ipynb)

This project studies how recurrent connectivity affects motor learning in an RNN.

## Research question

> **When sparse and dense motor RNNs have the same number of trainable recurrent connections, does the difference in held-out reaching performance become smaller?**

Q2 showed a performance difference between densities, but denser networks also had more trainable connections. This follow-up tests whether that difference reflects network density, plasticity budget, or both. Neural-manifold measurements remain exploratory.

## Start here

1. Open the [guided project notebook](notebooks/Motor_RNN_Project.ipynb) or use the Colab badge above.
2. Leave `RUN_MODE = "view"` to inspect Q1, Q2, the committed results, and all four figures immediately.
3. Use `smoke` for a quick end-to-end run, `pilot` for the three-seed pilot, or `primary` only when intentionally reproducing the full experiment.
4. Read [Team workflow](docs/TEAM_WORKFLOW.md) before making a contribution.

## Current status

- **Q1 is resolved as a baseline reproduction.** A 50-trial network at \(p=0.10\) produces both the original-style online feedback loss and a separate held-out velocity-error curve.
- **Q2 is resolved for the current all-weights-plastic design.** The corrected experiment uses a fixed motor decoder, balanced held-out trials, nested density masks, and paired randomness across conditions.
- In the \(N=200\), eight-seed experiment, the H1 low-density contrast was positive in 8/8 seeds. H2, the proposed diminishing-returns contrast, was positive in only 3/8 seeds and is not supported.
- Manifold dimensionality decreased as performance improved. This is an exploratory association confounded with density, not a causal mechanism.

![Primary held-out learning curves](results/primary/figures/figure1_heldout_nmse.png)

The complete scientific assessment and claim boundary are in [Research overview](docs/RESEARCH_OVERVIEW.md).

## Repository map

```text
notebooks/Motor_RNN_Project.ipynb   canonical guided Colab notebook
src/nma_motor_rnn/connectivity.py   reusable model and analysis code
tests/                              scientific and result-integrity checks
results/q1/                         50-trial Q1 baseline
results/pilot/                      N=100, three-seed pilot
results/primary/                    N=200, eight-seed primary experiment
docs/                               research, literature, and team workflow
literature/                         citations, DOI links, and PDF manifest
notebooks/archive/                  source and historical notebooks
```

## Local setup

```bash
git clone https://github.com/Thom-320/nma-motor-rnn-connectivity.git
cd nma-motor-rnn-connectivity
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
python3 -m unittest discover -s tests -v
```

## Collaboration

Work from a labeled GitHub Issue, create a short branch, keep one scientific purpose per Pull Request, and request one peer review. CI must pass before merge. Exact commands are in [CONTRIBUTING.md](CONTRIBUTING.md).

The repository does not track publisher PDFs, credentials, runtime outputs, or machine-specific paths. See [Literature review](docs/LITERATURE_REVIEW.md), [source provenance](docs/RESEARCH_OVERVIEW.md#source-repositories), and [third-party attribution](THIRD_PARTY.md).

## Interpretation boundary

Every recurrent connection that exists is plastic. The current evidence therefore compares complete density-dependent architectures; it does not isolate structural density from plasticity budget, identify a critical density, or establish that manifold dimensionality causes performance differences.
