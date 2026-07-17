# W2D2 Motor-RNN Connectivity Project

## Current project framing

**Primary question:** How much does controlling the recurrent plasticity budget reduce the held-out performance gap between sparse and dense motor RNNs?

**Secondary exploratory question:** Are density-related performance differences accompanied by changes in task-evoked neural-manifold dimensionality?

**Confirmatory hypotheses**

Let \(\Delta^{all}_s\) be the paired low-minus-high-density NMSE contrast for seed \(s\) when all existing weights are plastic, and \(\Delta^{fixed}_s\) the same contrast under the controlled-plasticity regime. The primary contrast is \(\Psi_s=\Delta^{all}_s-\Delta^{fixed}_s\).

1. **Primary hypothesis:** \(\mathbb{E}[\Psi_s]>0\). Controlling plasticity attenuates the density gap.
2. **Secondary estimate:** \(\mathbb{E}[\Delta^{fixed}_s]\). This describes any residual density difference without making an equivalence claim.

Participation-ratio dimensionality and the number of PCs explaining 90% of activity variance will be reported without a directional hypothesis. Their relationship with performance is exploratory.

The completed all-weights-plastic Q2 experiment motivates these contrasts but does not test them. The exact control design, density conditions, and plastic budget remain pending Project-TA approval; see [CONTROL_PROTOCOL.md](CONTROL_PROTOCOL.md).

## Team use

The five core entries answer all six NMA reading fields explicitly. Assign papers according to the rotating literature role, but discuss every paper as a group before finalizing the proposal or abstract. Khona et al. is a bridge paper rather than direct evidence for the predicted density effect.

## Literature review

### 1. Feulner and Clopath (2021), *Neural manifold under plasticity in a goal driven learning behaviour*

**1. Research question and hypotheses**

The authors asked why monkeys adapt rapidly to brain-computer-interface perturbations that remain within an existing neural manifold but struggle with perturbations that require activity outside that manifold. They tested whether recurrent synaptic plasticity, guided by an error-feedback or credit-assignment signal, could reproduce this difference. Their central mechanistic hypothesis was that within-manifold adaptation is more robust when the feedback signal or plasticity is biologically constrained.

**2. Design and methodology**

They constructed a rate RNN with 800 units, 10% recurrent connection probability, gain \(g=1.5\), and six center-out reach targets. A fixed decoder converted neural activity into two-dimensional cursor velocity. Recurrent weights were modified using error-dependent learning. After initial training, the decoder was perturbed either within or outside the original ten-dimensional manifold. The study compared ideal, noisy, sparse, and learned feedback signals and also constrained the number of plastic connections.

**3. Results and relation to the hypotheses**

With an ideal feedback signal, recurrent plasticity learned within- and outside-manifold perturbations similarly, with comparable performance and total weight-change magnitude. Differences emerged when feedback was noisy, sparse, or learned from scratch, or when plastic connections were restricted: within-manifold adaptation was then more successful. The results therefore support a feedback/credit-assignment constraint rather than a universal prohibition on outside-manifold recurrent learning.

**4. Significance or excitement**

The study is significant because it separates the geometry of the desired activity change from the mechanism that assigns behavioral error to individual neurons. It also shows that recurrent weight changes need not rotate the entire neural manifold.

**5. Main message**

Fast within-manifold learning may arise because existing task-relevant activity modes are easier to access with imperfect feedback, not simply because recurrent synapses cannot generate outside-manifold activity.

**6. Open and follow-up question**

The reference model fixes recurrent density at \(p=0.1\). Our follow-up asks whether the initial ability to learn the reach task changes across recurrent densities when gain normalization and the learning rule are held fixed.

Reference: [Feulner and Clopath, 2021](https://doi.org/10.1371/journal.pcbi.1008621)

### 2. Sussillo and Abbott (2009), *Generating Coherent Patterns of Activity from Chaotic Neural Networks*

**1. Research question and hypotheses**

The authors asked whether initially chaotic recurrent activity could be reorganized rapidly into stable, coherent outputs while feedback loops remained active. They hypothesized that fast recursive least-squares updates could keep output error small during learning and stabilize useful trajectories.

**2. Design and methodology**

They introduced FORCE learning in rate RNNs and trained readout, feedback-network, or recurrent weights. Tasks included periodic and aperiodic functions, input-output transformations requiring memory, switchable outputs, and human motion-capture sequences. They varied recurrent coupling strength and compared initially chaotic with non-chaotic regimes.

**3. Results and relation to the hypotheses**

FORCE learning converted spontaneous chaotic dynamics into accurate target outputs across a wide range of tasks. In the examples examined, initially chaotic networks often trained faster and produced more accurate and robust outputs than weakly coupled non-chaotic networks, although excessive or insufficient feedback could prevent stabilization. These results supported the proposed fast error-control mechanism.

**4. Significance or excitement**

The method made difficult recurrent-learning problems computationally tractable and showed that spontaneous variability can provide a useful dynamical repertoire rather than merely acting as noise.

**5. Main message**

Online RLS updates can harness rich recurrent dynamics and stabilize task-producing activity without clamping the network's feedback loop.

**6. Open and follow-up question**

Does changing recurrent density alter how reliably this error-driven stabilization succeeds when the nonzero weight variance is normalized across densities?

Reference: [Sussillo and Abbott, 2009](https://doi.org/10.1016/j.neuron.2009.07.018)

### 3. Jaeger and Haas (2004), *Harnessing Nonlinearity: Predicting Chaotic Systems and Saving Energy in Wireless Communication*

**1. Research question and hypotheses**

The study asked whether a large random recurrent reservoir could model nonlinear dynamical systems efficiently when learning modified only a linear output readout. The working hypothesis was that richly varying reservoir responses provide a temporal basis from which desired outputs can be reconstructed.

**2. Design and methodology**

The authors used an echo-state network with a 1,000-unit reservoir and 1% recurrent connectivity for Mackey-Glass chaotic time-series prediction. They trained the output by linear regression and also tested a smaller echo-state network on nonlinear communication-channel equalization.

**3. Results and relation to the hypotheses**

The echo-state approach greatly improved prediction accuracy on the benchmark and reduced communication-channel error relative to earlier methods. This supported the idea that useful nonlinear temporal features can arise from a fixed sparse recurrent reservoir.

**4. Significance or excitement**

The striking result is that recurrent computation need not require training every recurrent connection. A large random dynamical system can be useful when paired with a simple learned readout.

**5. Main message**

Random recurrent dynamics can provide a rich computational basis, making readout learning efficient.

**6. Open and follow-up question**

The paper does not test density systematically and trains only the readout. It therefore motivates sparse-RNN background but does not predict the direction of our recurrent-density effect.

Reference: [Jaeger and Haas, 2004](https://doi.org/10.1126/science.1091277)

### 4. Waernberg and Kumar (2019), *Perturbing low dimensional activity manifolds in spiking neuronal networks*

**1. Research question and hypotheses**

The authors asked how low-dimensional activity manifolds arise from connectivity and why within-manifold patterns are easier to learn than outside-manifold patterns. They hypothesized that the intrinsic manifold is a direct consequence of circuit connectivity and that outside-manifold changes consequently require larger synaptic modifications.

**2. Design and methodology**

They studied three spiking-network frameworks: echo-state/FORCE networks, the Neural Engineering Framework, and efficient-coding networks. They related connectivity-defined neural modes to population activity and compared the synaptic changes required for within- and outside-manifold perturbations. Some analyses included sparse and Dale-compliant networks.

**3. Results and relation to the hypotheses**

Across the three frameworks, connectivity determined the activity modes that formed the intrinsic manifold. Producing outside-manifold patterns generally required substantially greater synaptic changes than producing within-manifold patterns. This supported their connectivity-based explanation of differential learning difficulty.

**4. Significance or excitement**

The work links a population-level geometric observation directly to circuit structure and makes a testable prediction about the synaptic cost of changing neural activity.

**5. Main message**

Low-dimensional neural modes can be consequences of recurrent connectivity, and leaving those modes can require extensive connectivity changes.

**6. Open and follow-up question**

Does global recurrent connection probability affect the ability of a goal-driven rate RNN to acquire task-performing dynamics, even before a within- or outside-manifold perturbation is introduced?

Reference: [Waernberg and Kumar, 2019](https://doi.org/10.1371/journal.pcbi.1007074)

### 5. Gao et al. (2017), *A theory of multineuronal dimensionality, dynamics and measurement*

**1. Research question and hypotheses**

The authors asked why recorded neural population activity is often much lower-dimensional than the number of recorded neurons and how dimensionality should depend on experimental task structure. They proposed neural task complexity (NTC) as an upper bound determined by task-parameter ranges and the correlation lengths of neural activity across those parameters.

**2. Design and methodology**

They developed a mathematical theory connecting manifold dimensionality, NTC, neuron count, and random projections. They then examined monkey motor and premotor cortical recordings from an eight-direction center-out reaching task and compared measured participation-ratio dimensionality with the predicted complexity frontier.

**3. Results and relation to the hypotheses**

They proved that measured dimensionality is bounded by the smaller of recorded neuron count and NTC under the theory's assumptions. In the motor data, dimensionality was far below neuron count and near the task-complexity scale. Restricting temporal duration or reach-angle range reduced both NTC and dimensionality in the predicted manner.

**4. Significance or excitement**

The framework warns against interpreting low dimensionality as evidence that a circuit is intrinsically simple. A simple and smoothly represented task can itself impose a low ceiling.

**5. Main message**

Neural dimensionality must be interpreted relative to task complexity and sampling. Recording more neurons during the same simple task need not reveal more dimensions.

**6. Open and follow-up question**

Does sparse connectivity impose an additional circuit constraint below the task-dependent ceiling? Importantly, Gao et al. do not establish that higher dimensionality causes better task performance, so our dimension-performance relationship remains exploratory.

Reference: [Gao et al., 2017 preprint](https://doi.org/10.1101/214262)

### Bridge paper: Khona et al. (2023), *Winning the lottery with neural connectivity constraints*

**1. Research question and hypothesis:** The authors asked whether biologically motivated spatial connectivity constraints could improve learning across cognitive tasks. They predicted that structured sparse connectivity could provide useful inductive biases.

**2. Methods:** Spatially embedded recurrent networks were trained across cognitive task batteries and compared with dense or differently constrained architectures.

**3. Results:** Sparse spatial constraints often improved training speed or efficiency, but the preferred architecture depended on task demands.

**4. Significance:** The study shows that maximum density is not automatically optimal and motivates examining architecture-dependent learning.

**5. Main message:** Connectivity constraints can function as inductive biases rather than merely reducing capacity.

**6. Follow-up:** Does global random connection probability affect a Feulner-style motor RNN under paired variance-normalized initialization? Because the topology, tasks, and learning rules differ, this paper motivates the question but does not predict our result directly.

Reference: [Khona et al., arXiv:2207.03523](https://arxiv.org/abs/2207.03523)

## Cross-paper synthesis

Feulner and Clopath supply the base motor RNN and show why recurrent feedback learning matters. Sussillo and Abbott supply the FORCE/RLS learning logic. Waernberg and Kumar motivate a relationship between circuit connectivity and neural activity modes. Gao et al. provide the correct caution for interpreting dimensionality: task complexity can impose a ceiling, and dimensionality is not automatically a performance mechanism. Jaeger and Haas demonstrate the computational value of sparse random reservoirs but do not directly test our manipulation because their recurrent weights remain fixed.

Together, the papers motivate testing recurrent density while leaving its mechanism open. The completed Q2 experiment found a low-density impairment, but density and the number of trainable recurrent synapses changed together. A matched-plasticity comparison is therefore needed to distinguish a structural-density contribution from a plasticity-budget contribution.

## Working proposal draft (258 words)

Motor behavior can be generated by low-dimensional population dynamics embedded within much larger recurrent circuits. Random recurrent networks can provide rich temporal representations, FORCE-style learning can stabilize desired outputs, and recurrent plasticity can support center-out reaching. The Neuromatch Motor-RNN template therefore asks how network connectivity affects learning. Our preliminary paired-seed experiment found that very sparse networks produced higher held-out motor error than moderate- and high-density networks. However, every existing recurrent connection was plastic, so increasing connection probability also increased the number of trainable synapses. The observed difference may therefore reflect recurrent structure, plasticity budget, or both. We will ask how much controlling the plasticity budget reduces the density-related performance gap. Using the same six-direction reaching task, fixed motor decoder, and FORCE-style recurrent learning rule, we will compare lower- and higher-density networks under all-existing-weights-plastic and controlled-plasticity regimes. Within each seed, conditions will share underlying weights, input weights, target schedules, and initial states; nonzero recurrent weights will retain variance-normalized scaling. The primary outcome will be final held-out velocity NMSE, evaluated on balanced trials with learning disabled; learning-curve area will be secondary. We will estimate how much the paired density gap changes after controlling plasticity and report any residual gap separately. Attenuation would be consistent with a contribution from plasticity budget, while persistence would be consistent with a contribution from recurrent structure or dynamics beyond trainable-parameter count. Participation-ratio dimensionality and the number of PCs explaining 90% of task-evoked variance will remain exploratory because an association with performance would not establish a causal mechanism.

## Interpretation boundaries

- A single-seed training-loss curve is not confirmatory evidence.
- The independent replicate is the network seed, not each trajectory or time point.
- The completed preliminary result concerns architectures in which every existing recurrent connection is plastic.
- The new primary question requires an exactly matched plastic in-degree; the control must not be described as completed before it is run.
- A refitted PCA decoder measures decodability; it must not replace the fixed training decoder in the primary performance evaluation.
- An uncertain density effect is inconclusive; it is not evidence of equivalence.
- Do not claim a critical density unless replicated held-out results actually display a reproducible transition.
