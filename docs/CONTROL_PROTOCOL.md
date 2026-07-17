# Plasticity-control protocol

**Status:** awaiting team and Project-TA decision. Do not run the full control until the fields marked **TBD** are approved by all four team members in a reviewed PR.

## Question

How much does controlling the recurrent plasticity budget reduce the held-out performance gap between sparse and dense motor RNNs?

The completed Q2 experiment varied recurrent density while allowing every existing recurrent connection to change. It therefore varied structural density and plasticity budget together.

## Estimands

For seed \(s\), let

\[
\Delta^{all}_s = E_{s,low,all} - E_{s,high,all}
\]

and

\[
\Delta^{fixed}_s = E_{s,low,fixed} - E_{s,high,fixed},
\]

where \(E\) is final held-out velocity NMSE. The primary contrast is

\[
\Psi_s = \Delta^{all}_s - \Delta^{fixed}_s.
\]

Positive \(\Psi\) means that controlling plasticity attenuates the observed density gap. The residual \(\Delta^{fixed}\) is a secondary estimate. A statistically uncertain residual is not evidence of equivalence.

## Frozen components

- Network size: \(N=200\).
- Seeds: 0–7, matching the completed Q2 experiment.
- Training: 60 trials with the existing recurrent RLS rule.
- Evaluation: final held-out velocity NMSE with the fixed motor decoder and learning disabled.
- Pairing: shared underlying weights, inputs, decoder, schedules, initial states, and nested structural masks within seed.
- Secondary outcome: learning-curve area.
- Exploratory outcomes: \(D_{PR}\), \(D_{90}\), and their change during learning.

## Decision required from the team and Project TA

- Control design: **TBD** — matched-mask comparison or fixed-\(k\) density-by-plasticity comparison.
- Density conditions: **TBD**.
- Matched plastic in-degree, if applicable: **TBD**.

Before the decision, every team member must post a preferred design, an observation that would count against the hypothesis, and one limitation in GitHub Issue #6. The final decision must use structural feasibility and scientific interpretability, not control outcomes. The chosen plastic indices must be paired across density conditions whenever the design requires the same trainable connections.

## Reporting

- Show every seed-level \(\Delta^{all}\), \(\Delta^{fixed}\), and \(\Psi\).
- Report the mean and median, plus a seed-bootstrap interval for mean \(\Psi\).
- Do not claim equivalence without a separate prespecified equivalence design.
- Do not claim that manifold dimensionality causes performance differences.
- Keep Q3–Q9, graph metrics, task-complexity manipulations, and full \(N=800\) sweeps out of scope.
