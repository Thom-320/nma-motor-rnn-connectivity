# Research overview

## Frozen questions

**Primary:** Under variance-normalized initialization and a fixed recurrent learning rule, how does recurrent connection probability \(p\) affect held-out learning of a six-direction center-out reaching task?

**Exploratory:** Are density-related performance differences accompanied by changes in task-evoked neural-manifold dimensionality?

## Source repositories

- [babaf/neural-manifold-and-plasticity](https://github.com/babaf/neural-manifold-and-plasticity) is the original paper implementation associated with Feulner and Clopath. It provides scientific provenance and figure-level simulation scripts.
- [steevelaquitaine/neural-manifold-and-plasticity](https://github.com/steevelaquitaine/neural-manifold-and-plasticity) is a lightly cleaned teaching fork that mainly adds setup support.

Neither source repository is a complete student collaboration workspace. This project links to them, credits their licenses, and places the new paired experiment, tests, results, and documentation in a separate team repository.

## Relationship to the NMA project map

The Motor-RNN image proposes a natural sequence. Q1 trains the reaching RNN and inspects loss; Q2 varies connection density and compares reaching error. Our project follows exactly that Q1 → Q2 path. Q3–Q9—optimizing sparsity, graph metrics, force tasks, task complexity, context switching, and multitask learning—are explicitly outside the primary scope.

The listed model/data databases (ModelDB, BioModels, Open Source Brain, CRCNS, INCF, and related resources) are useful discovery tools but are not project dependencies. This is a theory/simulation project with an existing published model, source code, and generated data. A new database search becomes necessary only if the team changes the model or adds external validation data.

## Q1 assessment

Q1 is feasible and resolved as a baseline reproduction. The canonical run uses \(N=100\), \(p=0.10\), seed 0, and 50 training trials. It reports:

- trial-level online feedback-space loss, matching the spirit of the template question;
- held-out velocity NMSE evaluated with a fixed decoder and no learning;
- explicit separation of training diagnostics from generalization performance.

The online curve need not decrease monotonically because targets and initial states vary and recurrent weights are updated during each trial. It is not sufficient evidence for a density effect.

## Q2 design and feasibility

Q2 is feasible on free Colab and already completed under the current contract:

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

H1 was positive in 8/8 primary seeds. The mean paired contrast was 0.177 with a seed-bootstrap 95% interval of [0.136, 0.219]. H2 was positive in 3/8 seeds; its mean contrast was 0.005 with interval [-0.081, 0.097], so diminishing returns are not supported.

Across the 32 primary conditions, final \(D_{PR}\) and final NMSE had descriptive Pearson \(r=0.671\): higher dimensionality accompanied worse performance. This is exploratory, confounded with density, and not causal. The contradictory \(N=100\) pilot remains visible and may indicate finite-size sensitivity.

## Defensible conclusion

Under paired initialization, variance scaling, a fixed motor decoder, and an all-existing-weights-plastic recurrent learning rule, very sparse \(N=200\) networks performed worse than moderate/higher-density networks on held-out six-direction reaching.

The experiment does not identify a critical density, support a performance plateau, isolate density from plasticity budget, or establish a causal manifold mechanism. Fixed-plasticity controls, task-complexity manipulations, BCI perturbations, graph metrics, and full \(N=800\) sweeps are future work.

## Official NMA context

- [NMA project daily guide](https://compneuro.neuromatch.io/projects/docs/project_guidance.html)
- [Behavior and Theory project guide](https://compneuro.neuromatch.io/projects/behavior_and_theory/README.html)
- [Google Colab FAQ](https://research.google.com/colaboratory/faq.html)
