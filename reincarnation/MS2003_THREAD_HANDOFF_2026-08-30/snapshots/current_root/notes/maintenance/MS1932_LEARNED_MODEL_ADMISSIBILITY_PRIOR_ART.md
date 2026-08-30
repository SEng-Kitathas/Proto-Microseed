# MS1932 — Learned-Model Admissibility Prior Art

Status: RESEARCH / DEMOTION PASS.
Date: 2026-08-28 ET.
No organism mutation. No canonical promotion.
Parent sealed organism head remains MS1924 `6b0f012980a625143ea7137be848d6f13b57325b`.
Upstream: MS1931 source-anchored adjudication identified a narrow missing-source question around learned/updated models directly gating present action admissibility.

## Question
Is there established prior art where a learned or continually updated model directly determines which present actions/decisions are admissible/safe to execute, rather than merely predicting utility?

## Result
YES — strong prior art exists.

This materially demotes the remaining cross-layer distinctiveness hypothesis.

## Source A — SafeOpt
Yanan Sui, Alkis Gotovos, Joel W. Burdick, Andreas Krause,
“Safe Exploration for Optimization with Gaussian Processes,” ICML 2015, PMLR 37:997–1005.
Primary page: https://proceedings.mlr.press/v37/sui15.html
PDF: https://proceedings.mlr.press/v37/sui15.pdf

Verified mechanism:
- unknown objective/safety-relevant function is learned from noisy samples with a Gaussian-process model;
- at each iteration the GP posterior defines predictive confidence intervals;
- those confidence intervals are used to classify the domain into current sets including `S_t`, the decisions certified safe;
- the current safe set is therefore a function of the learned/updated model state;
- SafeOpt selects its next decision only from current safe-set-derived candidate sets;
- the safe set expands only when enough evidence has accrued to establish additional decisions as safe;
- the paper explicitly notes that GP confidence intervals can themselves be used to certify a decision as safe when the lower confidence bound exceeds the safety threshold.

This establishes:
`LEARNED_MODEL_STATE -> CURRENT_DECISION_ADMISSIBILITY` as prior art in safe exploration.

Important difference from Microseed/System X:
- the admissibility semantics are safety-threshold / statistical-confidence semantics, not typed execution authority/provenance/current-source-digest semantics;
- SafeOpt begins with a specified safety threshold, seed safe set, and GP regularity assumptions;
- this is not permission bootstrapped from ignorance.

## Source B — SafeMDP
Matteo Turchetta, Felix Berkenkamp, Andreas Krause,
“Safe Exploration in Finite Markov Decision Processes with Gaussian Processes,” NeurIPS 2016.
Primary abstract: https://papers.nips.cc/paper_files/paper/2016/hash/9a49a25d845a483fae4be7e341368e36-Abstract.html
arXiv: https://arxiv.org/abs/1606.04753

Verified mechanism:
- safety is defined by an a priori unknown safety constraint depending on states and actions;
- the unknown constraint is modeled using a Gaussian-process prior and learned from noisy observations;
- the algorithm cautiously explores safe states and actions to gain statistical confidence about unvisited state-action pairs;
- reachability is explicitly considered so exploration does not enter states with no safe way out;
- the algorithm is proved to explore the safely reachable portion of the MDP without violating the safety constraint.

This is an even closer prior-art analogue for:
`LEARNED_STATE_ACTION_SAFETY_MODEL -> WHICH_STATE_ACTION_PAIRS_MAY_BE_EXPLORED_NOW`.

Important difference:
- the normative source is an explicit safety constraint/regularity model;
- this is safe-control admissibility, not Microseed’s multi-premise epistemic/regulatory execution-authority ontology.

## Source C — Safe model-based RL with stability guarantees
Felix Berkenkamp, Matteo Turchetta, Angela P. Schoellig, Andreas Krause,
“Safe Model-based Reinforcement Learning with Stability Guarantees,” NeurIPS 2017, pp. 908–918.
Primary abstract: https://papers.nips.cc/paper_files/paper/2017/hash/766ebcd59621e305170616ba3d3dac32-Abstract.html
Author/lab source: https://www.dynsyslab.org/wp-content/papercite-data/pdf/berkenkamp-nips17.pdf

Verified mechanism:
- uses statistical models of system dynamics to obtain high-performance policies with provable stability certificates;
- under GP regularity assumptions, the agent safely collects data to learn the dynamics, improve control performance, and expand the safe region of state space;
- learned model state and stability certification constrain which actions/policies are safe during learning.

Contemporary review text for the paper explicitly describes the learned model as constraining the policy to avoid actions that could bring the system into unsafe states, with both policy and exploratory actions affected by the safety constraint.

Important difference:
- again, safety/stability is the normative objective;
- the mechanism uses model-based control and Lyapunov/stability structure, not System X’s explicit current source-ancestry/priority/information/qualification binding.

## Source D — Shielding as complementary prior art
Mohammed Alshiekh et al., “Safe Reinforcement Learning via Shielding,” AAAI 2018.
Primary page: https://ojs.aaai.org/index.php/AAAI/article/view/11797
DOI: https://doi.org/10.1609/aaai.v32i1.11797

Verified mechanism:
- learning agent proposes actions;
- shield monitors them and corrects/blocks actions that violate an explicit temporal-logic safety specification;
- shield can provide a list of safe actions before the learner decides, or filter chosen actions afterward.

This is not primarily a learned-model-admissibility result because the shield is synthesized from a specification/environment abstraction rather than learned consequence evidence, but it reinforces the established separation:
`LEARNER_PROPOSAL != FINAL_ACTION_ADMISSIBILITY`.

## Demotion result
MS1931’s narrow missing-source hypothesis:

`NO_KNOWN_PRIOR_ART_FOR_LEARNED_MODEL_STATE_AS_PRESENT_ACTION_ADMISSIBILITY_PREMISE`

is REJECTED.

Earned demotion laws:
- `LEARNED_MODEL_GATES_CURRENT_ADMISSIBILITY` is established prior art.
- `LEARNED_STATE_ACTION_SAFETY_MODEL -> CURRENT_SAFE_ACTION_SET` is established prior art.
- `MODEL_UPDATE_CAN_EXPAND_OR_CONTRACT_WHAT_MAY_BE_SAMPLED_NOW` is established prior art under explicit safety assumptions.

## What remains different
The remaining difference is semantic/decompositional, not the broad gating mechanism:
- System X binds exact learned consequence/source ancestry together with current capability epoch, control-state evidence, operational scope, regulatory priority, information/discrimination and qualification premises;
- System X treats these as typed authority/currentness owners rather than a single safety-confidence set or global safety objective;
- System X explicitly distinguishes evidence, truth, qualification, currentness and execution authority;
- System X refuses to infer normative exploration permission from informativeness alone.

None of these remaining points is established novelty.

## Novelty consequence
The residual prior-art gap is now substantially smaller.

Current posture:
- capability/proposal vs authorization: established analogue/prior art;
- current-at-use mediation: established prior art;
- proof/premise-bearing authorization: established prior art;
- provenance/justification/revision: established prior art;
- information-seeking/model-discriminating action: established prior art;
- learned/updated model gating current safe action admissibility: established prior art;
- global-manager impossibility: not established;
- exact typed multi-premise Microseed integration: not matched in this bounded search, but absence is not novelty evidence.

Therefore novelty remains:
`UNKNOWN / NOT_ENTITLED_TO_CLAIM`.

The strongest scientifically defensible description is now:
`MOSTLY_KNOWN_MECHANISMS_WITH_A_SPECIFIC_AUTHORITY_FACTORIZATION_AND_DEVELOPMENTAL_INTEGRATION`.

## Next useful pressure
Another broad prior-art sweep is unlikely to be Pareto-useful.
If distinctiveness research continues, require either:
1. a genuinely independent specialist/source lineage reviewing the exact remaining semantic/factoring claim; or
2. a concrete measurable engineering discriminator (e.g. fault-localization, requalification blast radius, trace granularity, authority-coupling mutation resistance) against a named baseline architecture.

Do not continue novelty narration from the shrinking absence-of-exact-match residue.
