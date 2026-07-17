# Research overview

## Current project question

**Primary:** How much does controlling the recurrent plasticity budget reduce the held-out performance gap between sparse and dense motor RNNs?

**Exploratory:** Are density-related performance differences accompanied by changes in task-evoked neural-manifold dimensionality?

The completed all-weights-plastic Q2 experiment motivates this question but does not answer it. It changes structural density and plasticity budget together. The control interface is implemented locally, but the exact conditions remain pending Project-TA review and no full control result is committed.

Let

\[
\Delta^{all}_s=E_{s,low,all}-E_{s,high,all}
\]

and

\[
\Delta^{fixed}_s=E_{s,low,fixed}-E_{s,high,fixed},
\]

where \(E\) is final held-out velocity NMSE. The primary seed-level contrast is

\[
\Psi_s=\Delta^{all}_s-\Delta^{fixed}_s.
\]

The primary hypothesis is \(\mathbb{E}[\Psi_s]>0\): controlling plasticity attenuates the density gap. The residual \(\Delta^{fixed}\) is a secondary estimate. These outcomes are not mutually exclusive, and an uncertain residual does not establish equivalence.

## Plasticity-control design

The components already fixed are \(N=200\), seeds 0–7, 60 training trials, the existing FORCE/RLS rule, fixed decoder, balanced held-out evaluation, shared schedules and initial states, and variance-normalized recurrent weights. Structural masks remain nested within seed.

The Project TA must still approve the control design, density conditions, and matched plastic budget. Those decisions will be recorded in [CONTROL_PROTOCOL.md](CONTROL_PROTOCOL.md) before the full run. The software therefore requires the density pair and plastic in-degree explicitly instead of supplying a scientific default.

If fixed \(k\) is selected, every neuron must have at least \(k\) structural inputs in the sparse condition, and the same plastic indices must be used in both densities. \(D_{PR}\) and \(D_{90}\) remain descriptive and exploratory.

## Source repositories

- [babaf/neural-manifold-and-plasticity](https://github.com/babaf/neural-manifold-and-plasticity) is the original paper implementation associated with Feulner and Clopath. It provides scientific provenance and figure-level simulation scripts.
- [steevelaquitaine/neural-manifold-and-plasticity](https://github.com/steevelaquitaine/neural-manifold-and-plasticity) is a lightly cleaned teaching fork that mainly adds setup support.

Neither source repository is a complete student collaboration workspace. This project links to them, credits their licenses, and places the new paired experiment, tests, results, and documentation in a separate team repository.

## Relationship to the NMA project map

The Motor-RNN image proposes a natural sequence. Q1 trains the reaching RNN and inspects loss; Q2 varies connection density and compares reaching error; Q3 asks how much sparsity can be tolerated while maintaining performance. Our project follows Q1 → Q2. The plasticity-budget experiment is a follow-up control for Q2, not Q3. Q3 would require a reference architecture, a prespecified acceptable-performance margin, and a finer density search or an explicit pruning procedure. It has not been answered.

The source image contains two distinct boxes both labeled **Q5**. To avoid silently renumbering the official map, this repository refers to them as **Q5a** (the oscillating-force task) and **Q5b** (linear versus `tanh` units). Q4, Q5a, Q5b, Q6, Q7, Q8, and Q9 remain outside the current project scope.

| Project-map question | Faithful interpretation | Repository status |
|---|---|---|
| Q1 | Train the reaching RNN for 50 trials and inspect loss/convergence | Completed baseline, with held-out evaluation added |
| Q2 | Increase connection density and compare post-learning target-versus-cursor velocity MSE | Completed preliminary paired experiment; matched-plasticity control implemented |
| Q3 | Maximize sparsity during training while maintaining performance | Not answered |
| Q4 | Relate sparsity to path length, weighted path length, modularity, propagation, and structural evolution | Out of scope |
| Q5a | Train an oscillating-force task and compare learning/manifold dimensionality with reaching | Out of scope |
| Q5b | Replace linear units with `tanh` and examine dynamics, chaos, and learning | Out of scope; the current implementation already uses `tanh` |
| Q6 | Fix recurrent weights and train only decoder weights | Out of scope |
| Q7 | Manipulate task complexity and relate it to learning and manifold dimensionality | Out of scope |
| Q8 | Learn and switch between two tasks with minimal cross-talk | Out of scope |
| Q9 | Give one cue context-dependent reaching/force meanings | Out of scope |

The listed model/data databases (ModelDB, BioModels, Open Source Brain, CRCNS, INCF, and related resources) are useful discovery tools but are not project dependencies. This is a theory/simulation project with an existing published model, source code, and generated data. A new database search becomes necessary only if the team changes the model or adds external validation data.

## Q1 assessment

Q1 is feasible and resolved as a baseline reproduction. The committed run uses \(N=100\), \(p=0.10\), seed 0, and 50 training trials. It reports:

- trial-level online feedback-space loss, matching the spirit of the template question;
- held-out velocity NMSE evaluated with a fixed decoder and no learning;
- explicit separation of training diagnostics from generalization performance.

The online curve need not decrease monotonically because targets and initial states vary and recurrent weights are updated during each trial. It is not sufficient evidence for a density effect.

## Completed Q2 evidence

The initial Q2 comparison is feasible on free Colab and complete under its original contract:

- \(p\in\{0.05,0.10,0.20,0.40\}\);
- nested masks and shared random matrices within each seed;
- nonzero weights scaled by \(g/\sqrt{pN}\);
- shared input weights, fixed motor decoder, schedule, and initial states;
- evaluation every five trials on 30 balanced held-out trials;
- primary outcomes: final velocity NMSE and learning-curve area;
- secondary outcomes: raw MSE, weight change, degree, synapse count, spectral radius, \(D_{PR}\), and \(D_{90}\).

The pilot used \(N=100\), three seeds, and 40 trials. The primary experiment used \(N=200\), eight seeds, and 60 trials.

## Results

| p | Mean final NMSE | Mean AUC | Mean D_PR | Mean D90 |
|---:|---:|---:|---:|---:|
| 0.05 | 0.424 | 0.655 | 3.528 | 10.125 |
| 0.10 | 0.331 | 0.581 | 3.069 | 8.125 |
| 0.20 | 0.276 | 0.422 | 2.651 | 4.125 |
| 0.40 | 0.133 | 0.382 | 2.556 | 3.125 |

The original Q2 H1 was positive in 8/8 primary seeds. Its mean contrast—\(p=0.05\) minus the average of \(p\in\{0.10,0.20,0.40\}\)—was 0.177 with a seed-bootstrap 95% interval of [0.136, 0.219]. This is not the pairwise contrast for the new control. The original H2 was positive in 3/8 seeds; its mean contrast was 0.005 with interval [-0.081, 0.097], so diminishing returns are not supported.

Across the 32 primary conditions, final \(D_{PR}\) and final NMSE had descriptive Pearson \(r=0.671\): higher dimensionality accompanied worse performance. This is exploratory, confounded with density, and not causal. The contradictory \(N=100\) pilot remains visible and may indicate finite-size sensitivity.

## Defensible conclusion

Under paired initialization, variance scaling, a fixed motor decoder, and an all-existing-weights-plastic recurrent learning rule, very sparse \(N=200\) networks performed worse than moderate/higher-density networks on held-out six-direction reaching.

The experiment does not identify a critical density, support a performance plateau, isolate density from plasticity budget, or establish a causal manifold mechanism. The control implementation is under review and its exact design is pending Project-TA approval. Task-complexity manipulations, BCI perturbations, graph metrics, and full \(N=800\) sweeps remain future work.

## Official NMA context

- [NMA project daily guide](https://compneuro.neuromatch.io/projects/docs/project_guidance.html)
- [Behavior and Theory project guide](https://compneuro.neuromatch.io/projects/behavior_and_theory/README.html)
- [Google Colab FAQ](https://research.google.com/colaboratory/faq.html)
