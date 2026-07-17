# NMA Motor-RNN Connectivity

[![scientific checks](https://github.com/Thom-320/nma-motor-rnn-connectivity/actions/workflows/tests.yml/badge.svg)](https://github.com/Thom-320/nma-motor-rnn-connectivity/actions/workflows/tests.yml)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Thom-320/nma-motor-rnn-connectivity/blob/main/notebooks/Motor_RNN_Project.ipynb)

A Neuromatch Academy project on recurrent connectivity and motor learning.

## Question

Dense networks performed better in our initial experiment, but they also had more trainable recurrent connections. We now ask:

> **How much does controlling the recurrent plasticity budget reduce the held-out performance gap between sparse and dense motor RNNs?**

This follows the NMA Motor-RNN template's **Q1 -> Q2** path: reproduce learning, test density, then examine a confound in the density comparison. Neural-manifold measurements remain exploratory.

## Status

- **Q1:** complete — 50 training trials with online loss separated from held-out velocity NMSE.
- **Q2:** complete under the all-existing-weights-plastic design — sparse networks had higher held-out error in the \(N=200\), eight-seed experiment.
- **Control:** implementation under review; the density pair and plastic budget will be frozen with the Project TA before the full run.
- **Claim boundary:** the current Q2 result does not separate structural density from the number of trainable synapses.

Methods, numerical results, and limitations are in the [research overview](docs/RESEARCH_OVERVIEW.md).

## Run the project

1. Open the [project notebook](notebooks/Motor_RNN_Project.ipynb) or use the Colab badge.
2. Keep `RUN_MODE = "view"` to inspect Q1, Q2, and the committed figures without retraining.
3. Use `smoke` for a quick end-to-end check or `control_smoke` to test the control pipeline. Do not start the full control until [the protocol](docs/CONTROL_PROTOCOL.md) is frozen.
4. To contribute, claim a [GitHub Issue](https://github.com/Thom-320/nma-motor-rnn-connectivity/issues) and follow [CONTRIBUTING.md](CONTRIBUTING.md).

This project builds on the [NMA Motor-RNN template](https://compneuro.neuromatch.io/projects/behavior_and_theory/README.html) and the [Feulner–Clopath model](https://github.com/babaf/neural-manifold-and-plasticity). Third-party sources are documented in [THIRD_PARTY.md](THIRD_PARTY.md).
