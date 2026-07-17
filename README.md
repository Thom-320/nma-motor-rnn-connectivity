# NMA Motor-RNN Connectivity

[![scientific checks](https://github.com/Thom-320/nma-motor-rnn-connectivity/actions/workflows/tests.yml/badge.svg)](https://github.com/Thom-320/nma-motor-rnn-connectivity/actions/workflows/tests.yml)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Thom-320/nma-motor-rnn-connectivity/blob/main/notebooks/Motor_RNN_Project.ipynb)

## Question

> When sparse and dense motor RNNs have the same number of trainable recurrent connections, does the difference in held-out reaching performance become smaller?

Q2 found that denser networks reached better, but they also had more connections free to change. We are deciding whether to test this in [Issue #12](https://github.com/Thom-320/nma-motor-rnn-connectivity/issues/12).

## Status

- **Q1:** complete — 50-trial baseline with online loss and held-out velocity NMSE.
- **Q2:** complete — paired density comparison with a fixed decoder and balanced test trials.
- Very sparse \(N=200\) networks performed worse across eight seeds.
- The result does not separate density from the number of plastic connections.

## Start

1. Open the notebook with the Colab badge.
2. Keep `RUN_MODE = "view"` to inspect results or use `smoke` for a quick check.
3. Join the current work in [Issue #12](https://github.com/Thom-320/nma-motor-rnn-connectivity/issues/12).

Methods and limitations are in the [research overview](docs/RESEARCH_OVERVIEW.md). The required paper summaries are in the [literature review](docs/LITERATURE_REVIEW.md). See [CONTRIBUTING.md](CONTRIBUTING.md) before changing the repository.
