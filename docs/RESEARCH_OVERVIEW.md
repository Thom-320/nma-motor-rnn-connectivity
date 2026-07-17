# Research overview

## What we're asking

Denser networks learned to reach better than sparse ones. But raising the connection probability $p$ raises two things at once: how many connections exist, and how many the learning rule can change. So the result we have is about whole architectures, not about density on its own.

> **When sparse and dense networks have the same number of trainable connections, does the gap get smaller?**

The team is deciding in [Issue #12](https://github.com/Thom-320/nma-motor-rnn-connectivity/issues/12) whether to test this. Until then, Q2 below is what we have.

We also track how many dimensions the population activity spans. That stays exploratory — we report it, we don't build a claim on it.

## What we built on

- [babaf/neural-manifold-and-plasticity](https://github.com/babaf/neural-manifold-and-plasticity) — the original Feulner & Clopath implementation.
- [steevelaquitaine/neural-manifold-and-plasticity](https://github.com/steevelaquitaine/neural-manifold-and-plasticity) — a lightly cleaned teaching fork.

Neither is a place four students can work in together, so we link to them and keep our experiment, tests and results here.

## Where this sits in the NMA template

The Motor-RNN template walks from Q1 (train the network, look at the loss) to Q2 (vary density, compare reaching error). We did exactly that and stopped. Q3–Q9 — optimizing sparsity, graph metrics, force tasks, task complexity, multitask — are out of scope. Not because they're uninteresting, but because nine half-finished questions beat no one.

## Q1 — does it learn?

Yes. The committed run is $N=100$, $p=0.10$, seed 0, 50 trials. It reports two things that are easy to confuse:

- the **online loss** the network uses while learning, and
- the **held-out velocity NMSE**, measured on fresh trials with the fixed decoder and learning switched off.

The online curve doesn't fall smoothly, and it shouldn't: targets and starting states change every trial, and the weights move during the trial itself. It's a diagnostic, not a performance measure. Only the held-out number tells you whether the network actually learned.

## Q2 — does density matter?

Runs fine on free Colab. What we fixed:

- $p \in \{0.05, 0.10, 0.20, 0.40\}$;
- inside a seed, every condition shares the same underlying weights, nested masks, inputs, decoder, trial order and starting states;
- non-zero weights scale as $g/\sqrt{pN}$, so total recurrent input stays comparable across densities;
- evaluation every five trials, on 30 balanced held-out trials, with learning off;
- main outcomes: final NMSE and learning-curve area. Everything else — weight change, degree, synapse count, spectral radius, $D_{PR}$, $D_{90}$ — is secondary.

The pilot was $N=100$, three seeds, 40 trials. The main run was $N=200$, eight seeds, 60 trials.

**The replicate is the network seed.** Fifty trajectories from one network are fifty looks at one network, not fifty networks.

## Results

| p | Final NMSE | AUC | D_PR | D90 |
|---:|---:|---:|---:|---:|
| 0.05 | 0.424 | 0.655 | 3.528 | 10.125 |
| 0.10 | 0.331 | 0.581 | 3.069 | 8.125 |
| 0.20 | 0.276 | 0.422 | 2.651 | 4.125 |
| 0.40 | 0.133 | 0.382 | 2.556 | 3.125 |

H1 held in 8/8 seeds — the sparsest networks did worst. Mean paired contrast 0.177, seed-bootstrap 95% interval [0.136, 0.219].

H2 — diminishing returns above some density — held in only 3/8 seeds. Mean contrast 0.005, interval [-0.081, 0.097]. Not supported.

Across the 32 conditions, $D_{PR}$ and final NMSE correlate at $r = 0.671$: the networks that spanned more dimensions did worse. That's a description, not a mechanism — dimensionality and density move together here, so we can't separate them. The $N=100$ pilot pointed the other way and stays in the record; it may just be a small-network effect.

## What we can and can't say

We can say: with paired initialization, variance scaling, a fixed decoder, and every existing connection free to learn, very sparse $N=200$ networks reached worse than denser ones.

We can't say: that there's a critical density, that returns plateau, that dimensionality causes the difference, or that any of it is about wiring rather than the number of trainable weights. That last one is the open question above.

## NMA links

- [Project daily guide](https://compneuro.neuromatch.io/projects/docs/project_guidance.html)
- [Behavior and Theory guide](https://compneuro.neuromatch.io/projects/behavior_and_theory/README.html)
- [Colab FAQ](https://research.google.com/colaboratory/faq.html)
