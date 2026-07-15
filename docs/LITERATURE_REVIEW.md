# W2D2 Motor-RNN Connectivity Project

## Frozen project framing

**Primary question:** Under variance-normalized initialization and a fixed recurrent learning rule, how does recurrent connection probability \(p\) affect held-out learning of a six-direction center-out reaching task?

**Secondary exploratory question:** Are density-related performance differences accompanied by changes in task-evoked neural-manifold dimensionality?

**Confirmatory hypotheses**

1. Final held-out velocity NMSE at \(p=0.05\) will exceed the average at \(p\in\{0.10,0.20,0.40\}\).
2. The reduction in NMSE from \(p=0.05\) to \(p=0.20\) will exceed any reduction from \(p=0.20\) to \(p=0.40\), consistent with diminishing returns.

Participation-ratio dimensionality and the number of PCs explaining 90% of activity variance will be reported without a directional hypothesis. Their relationship with performance is exploratory.

## Two-person division

- **Person 1:** Feulner and Clopath; Sussillo and Abbott; short Jaeger and Haas background entry; recurrent-learning code.
- **Person 2:** Waernberg and Kumar; Gao et al.; held-out evaluation and PCA/manifold code.
- **Together:** inspect paired-seed pilot results, revise the proposal in the group's own voice, and decide whether the final story is a density effect, diminishing returns, or a null result.

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

## Cross-paper synthesis

Feulner and Clopath supply the base motor RNN and show why recurrent feedback learning matters. Sussillo and Abbott supply the FORCE/RLS learning logic. Waernberg and Kumar motivate a relationship between circuit connectivity and neural activity modes. Gao et al. provide the correct caution for interpreting dimensionality: task complexity can impose a ceiling, and dimensionality is not automatically a performance mechanism. Jaeger and Haas demonstrate the computational value of sparse random reservoirs but do not directly test our manipulation because their recurrent weights remain fixed.

Together, the papers motivate testing recurrent density while leaving the result open. The experiment can support a low-density impairment, diminishing returns, or a robust null result. Only the held-out multi-seed comparison will decide among those stories.

## Working proposal draft (270 words)

Motor behavior can be generated by low-dimensional population dynamics embedded within much larger recurrent neural circuits. Previous work shows that random recurrent networks can supply rich temporal representations, that FORCE-style learning can stabilize desired outputs, and that recurrent plasticity can support center-out reaching. However, the Feulner and Clopath reference model fixes recurrent connection probability at 10%, leaving unclear how robust this learning mechanism is to changes in network density. We will test how recurrent connection probability affects learning of a six-direction center-out reaching task in a rate recurrent neural network. Networks will be initialized across four connection probabilities while scaling nonzero recurrent weights by \(g/\sqrt{pN}\), which approximately preserves recurrent input variance. For each random seed, density conditions will share input weights, the fixed motor decoder, target order, initial states, and underlying random weight matrices. Recurrent weights will be trained with the same FORCE-style recursive least-squares rule. Our primary outcomes will be held-out normalized velocity error and learning-curve area, evaluated on balanced trials without weight updates. We hypothesize that very sparse networks will have higher held-out error than moderate-density networks, while gains will diminish at higher densities. We will also measure participation-ratio dimensionality and the number of principal components explaining 90% of task-evoked activity variance. Because the literature does not establish that greater dimensionality causes better performance, this analysis will be exploratory rather than confirmatory. Changing density also changes the number of plastic recurrent weights, so conclusions will refer to the complete all-weights-plastic architecture rather than density independently of plasticity budget. This study will determine whether recurrent motor learning is sensitive to substantial structural sparsification or remains robust after variance normalization.

## Interpretation boundaries

- A single-seed training-loss curve is not confirmatory evidence.
- The independent replicate is the network seed, not each trajectory or time point.
- The main result concerns architectures in which every existing recurrent connection is plastic.
- A refitted PCA decoder measures decodability; it must not replace the fixed training decoder in the primary performance evaluation.
- A null density effect is interpretable evidence of robustness within the tested range.
- Do not claim a critical density unless replicated held-out results actually display a reproducible transition.
