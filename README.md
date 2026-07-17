# NMA Motor-RNN Connectivity

[![scientific checks](https://github.com/Thom-320/nma-motor-rnn-connectivity/actions/workflows/tests.yml/badge.svg)](https://github.com/Thom-320/nma-motor-rnn-connectivity/actions/workflows/tests.yml)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Thom-320/nma-motor-rnn-connectivity/blob/main/notebooks/Motor_RNN_Project.ipynb)

A Neuromatch Academy project about how a recurrent network's wiring affects the way it learns to move.

## The question

We train a network to make reaching movements, then change how densely its neurons connect to each other. Denser networks learned better. But they also had more connections free to change, so we can't yet tell which of the two did the work.

> **When sparse and dense networks have the same number of trainable connections, does the gap get smaller?**

We're deciding whether to test that in [Issue #12](https://github.com/Thom-320/nma-motor-rnn-connectivity/issues/12).

## Where we are

- **Q1** — the network learns the task. Done.
- **Q2** — denser networks reach more accurately, in all eight seeds. Done.
- What we can't say yet: whether that's the wiring itself, or just the extra trainable weights.

## Start here

1. Open the notebook with the Colab badge above.
2. Leave `RUN_MODE = "view"` to look at the results without retraining. Use `smoke` if you want to check that everything runs.
3. Pick something up in [Issue #12](https://github.com/Thom-320/nma-motor-rnn-connectivity/issues/12).

How we ran things, and what the results don't show: [research overview](docs/RESEARCH_OVERVIEW.md). The papers: [literature review](docs/LITERATURE_REVIEW.md). Before changing anything: [CONTRIBUTING.md](CONTRIBUTING.md).
