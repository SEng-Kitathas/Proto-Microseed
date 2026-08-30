# MS1925 — Full-Text Prior-Art Mechanism Comparison

Status: RESEARCH / EXTERNAL EVIDENCE. No organism mutation. No novelty promotion.
Date: 2026-08-27
Parent experimental head: `6b0f012980a625143ea7137be848d6f13b57325b` (MS1924).
Canonical Main-Dev remains MS1527.

## Purpose
Pressure the remaining Microseed distinctiveness hypotheses against primary/seminal mechanisms rather than topic-level similarity. This pass explicitly prefers demotion over novelty inflation.

Classification vocabulary:
- `ESTABLISHED_OVERLAP`
- `KNOWN_ANALOGUE`
- `POTENTIALLY_DISTINCTIVE_COMPOSITION`
- `UNRESOLVED`
- `NOT_ENTITLED_TO_CLAIM`

## 1. Capability / feasibility is not authorization

### Prior art
Saltzer & Schroeder, *The Protection of Information in Computer Systems* (1975): complete mediation requires every access to every object to be checked for authority; the paper explicitly includes recovery and warns that cached authority checks become unsafe when authority changes. It also states least privilege and distinguishes capabilities as unforgeable authorization tickets.

Anderson reference-monitor lineage: a reference validation mechanism is always invoked, tamperproof, and small enough to verify.

Lampson, *Dynamic Protection Structures* (1969): access permissions are protected objects/capabilities; domains hold changing capability sets and authority can be passed/manipulated without equating possession of ordinary program capability with arbitrary permission.

Appel & Felten (1999) and later proof-carrying authorization systems: a requester supplies a proof with an access request; the reference monitor verifies the proof/policy before access is granted.

Runtime-assurance/Simplex architectures: a capable advanced controller does not itself own final physical execution authority; a runtime decision module mediates/switches control based on safety conditions.

### Microseed comparison
Microseed’s `FEASIBLE_CAPABILITY != EXECUTION_AUTHORITY`, local-precheck/non-executable distinction, and execution-time currentness checks have strong functional prior art.

What remains narrower is that Microseed applies the mediation requirement to cognitive premises (current consequence ancestry, regulatory priority, information value, feasibility, source identity, observation currentness), not only a security policy or safety envelope.

Classification:
- ingredient: `ESTABLISHED_OVERLAP`
- cross-layer cognitive integration: `POTENTIALLY_DISTINCTIVE_COMPOSITION / UNRESOLVED`
- novelty claim: `NOT_ENTITLED_TO_CLAIM`

## 2. Current authorization / reauthorization versus historical permission

### Prior art
Saltzer & Schroeder complete mediation explicitly warns against remembering an old authority-check result when authority can change and includes recovery as part of the mediation surface.

Reference-monitor systems require every security-sensitive access to be mediated.

Proof-carrying authorization binds permission to a concrete request plus current proof/policy validation.

Modern runtime-assurance systems monitor system state at runtime and can revoke/switch control when safety conditions change.

### Microseed comparison
MS1917/MS1924 laws (`NOMINATION_CONTEXT != EXECUTION_CONTEXT`, `HISTORY != CURRENT_AUTHORITY`, `RESTARTED_STATE != REAUTHORIZED_STATE`) are not novel as general authorization principles.

Potentially distinctive detail: current cognitive action authority is re-derived from current learned relation content, exact source digests, current control-state evidence, and bound epistemic/regulatory premises rather than a conventional security credential or safety controller.

Classification:
- current-at-use authorization principle: `ESTABLISHED_OVERLAP`
- exact cognitive ancestry reauthorization composition: `UNRESOLVED / POTENTIALLY_DISTINCTIVE_COMPOSITION`

## 3. Provenance, source ancestry, derivation, revision

### Prior art
Buneman, Khanna & Tan (2001), *Why and Where: A Characterization of Data Provenance*: why-provenance tracks source data influencing result existence; where-provenance tracks source locations copied into outputs.

Green, Karvounarakis & Tannen (2007), *Provenance Semirings*: algebraic provenance representations propagate source annotations through relational calculations.

W3C PROV-DM (2013): explicit entities, activities, usage, generation, derivation, invalidation, revision, responsibility, and provenance-of-provenance. PROV notes that usage/generation chains alone are not sufficient for derivation; actual influence is required.

Doyle (1979) TMS: records reasons for beliefs and revises dependent belief sets when discoveries contradict assumptions.

De Kleer (1986) ATMS: tracks assumption sets and supports multiple simultaneous contexts/solutions without collapsing their justifications.

### Microseed comparison
Generic lineage, justification, revision, invalidation and source dependency are deep prior art.

Microseed’s narrower specialization is that exact source-relation/content ancestry is used as a mandatory premise for current executable epistemic action, not merely explanation, reproducibility, belief dependency, or data trust.

Classification:
- provenance/justification ingredients: `ESTABLISHED_OVERLAP`
- provenance as a current execution-authority premise inside developmental cognition: `KNOWN_ANALOGUE -> POTENTIALLY_DISTINCTIVE_COMPOSITION`, still `UNRESOLVED`

## 4. Explicit UNKNOWN / ABSTAIN / reject option

### Prior art
Chow (1970), *On optimum recognition error and reject tradeoff*: classical reject-option decision rule and error/reject tradeoff.

Selective classification literature (e.g. El-Yaniv & Wiener 2010) explicitly models classifiers that abstain/reject to control risk/coverage.

Truth-maintenance/nonmonotonic systems also distinguish unresolved/unsupported contexts rather than forcing one monotonic belief state.

### Microseed comparison
Microseed’s use of UNKNOWN/ABSTAIN is not novel as a decision posture.

Potentially narrower difference: abstention is often triggered by missing authority/currentness/provenance premises even when confidence or capability is high, rather than solely predictive uncertainty or expected classification risk.

Classification:
- abstention ingredient: `ESTABLISHED_OVERLAP`
- authority-factored abstention semantics: `KNOWN_ANALOGUE / UNRESOLVED`

## 5. Information-seeking / developmental epistemic action without a generic planner

### Prior art
Settles (2009) active learning: learners choose informative queries/data for labeling.

Schmidhuber (1991) curiosity/model-building controllers: learning progress/model improvement can drive action.

Oudeyer, Kaplan & Hafner / Oudeyer & Kaplan (2007): intrinsic motivation and learning-progress systems drive spontaneous developmental exploration; learning progress can itself generate reward/action selection.

Baranes & Oudeyer (2013) goal exploration: competence-progress-guided developmental exploration without requiring a conventional explicit task planner for every action.

Friston et al. (2015), *Active inference and epistemic value*: expected policy value contains epistemic/information-gain and extrinsic components; epistemic value drives exploration until further information gain disappears.

### Microseed comparison
Planner-free information acquisition, epistemic value, curiosity, learning-progress exploration, and developmental self-selected learning are established prior art families.

Microseed cannot claim novelty from acting for information or from developmental capability growth.

Potential distinction: Microseed explicitly refuses `UNCERTAINTY -> NORMATIVE_PRIORITY`, generic curiosity reward, or a unified scalar policy objective. Epistemic information, regulatory priority, feasibility/currentness, exact program ancestry, and execution authority remain separate premises.

Classification:
- information seeking / developmental exploration: `ESTABLISHED_OVERLAP`
- non-scalar authority-factored composition: `POTENTIALLY_DISTINCTIVE_COMPOSITION / UNRESOLVED`

## 6. Experiments chosen to discriminate rival models / HSP frontier

### Prior art
Atkinson & Fedorov (1975): T-optimal experimental design for discriminating rival models; model-discriminating experimental design is old, established work.

Ponce de Leon & Atkinson (1991): rival-model discrimination with prior information.

Myung & Pitt (2009): optimal experimental design explicitly maximizes model distinguishability; optimal design depends on model parameterization and especially the chosen utility function.

Robust model-discrimination literature (e.g. Ghosh & Dutta 2013) studies designs when the true model may not be one of the competing pair, directly addressing model-class misspecification.

Robust optimal design literature also treats parameter uncertainty and worst-case discrimination performance.

### Microseed / HSP comparison
Selecting discriminating experiments is not novel. Pareto/frontier construction for candidate experiments cannot claim novelty merely from selecting informative discriminators.

Campaign20’s `FRONTIER_OPTIMAL_UNDER_MODEL != WORLD_OPTIMAL` and model-adequacy amendment are strongly aligned with established sensitivity/robustness concerns in optimal experimental design.

Potentially distinctive HSP process detail is not yet established as novel and HSP auto-selection remains unqualified.

Classification:
- rival-model experiment selection: `ESTABLISHED_OVERLAP`
- model-misspecification concern: `ESTABLISHED_OVERLAP / KNOWN_ANALOGUE`
- HSP selection novelty: `NOT_ENTITLED_TO_CLAIM`

## 7. Restart/reentry / history without current authority

### Prior art
Complete mediation explicitly applies through recovery and warns against stale remembered authorization.

Capability/reference-monitor systems separate historical possession/configuration information from current permission checks.

PROV explicitly models invalidation and revision over time.

TMS/ATMS preserve historical reasons/assumptions while changing the currently believed context.

### Microseed comparison
`HISTORY != CURRENT_AUTHORITY` is not a novel general principle.

MS1924’s narrow implementation remains architecturally coherent: historical representation can be replayed while providers/contracts/current source ancestry must be re-earned through current owners. This resembles complete mediation plus provenance/TMS ideas composed inside a cognitive runtime.

Classification:
- principle: `ESTABLISHED_OVERLAP`
- exact cognitive implementation/composition: `KNOWN_ANALOGUE / UNRESOLVED`

## 8. Runtime assurance / shielding as nearest action-authority analogue

Simplex runtime assurance places an unverified/high-performance controller behind a verified decision module and safe fallback controller. The advanced controller may propose commands yet lack unconditional final control authority.

This is close in *control shape* to Microseed’s separation of proposal/capability from action authority, but different in semantics:
- Simplex mediates a safety invariant/envelope and may substitute a safe controller.
- Microseed mediates epistemic/regulatory/currentness/source-ancestry premises and may abstain without a generic safe-policy substitute.

Classification: `KNOWN_ANALOGUE`, not same mechanism.

## 9. Proof-carrying authorization as nearest lineage-to-authority analogue

Proof-carrying authorization requires the requester to provide a proof/certificates with a concrete request; a reference monitor checks the proof before access is granted.

This is a strong analogue for Microseed’s requirement that a concrete action/program carry exact current supporting premises before execution authority can exist.

Differences:
- PCA proves policy entailment, usually over credentials/principals/resources.
- Microseed’s premises include learned action-outcome ancestry, current operational state, epistemic deficit, priority/information, feasibility and observation lineage.
- Microseed does not currently expose a general authorization logic or proof language.

Classification:
- proof-supported per-request authorization: `ESTABLISHED_OVERLAP`
- specific learned-cognitive premise bundle: `POTENTIALLY_DISTINCTIVE_COMPOSITION / UNRESOLVED`

## Bounded novelty posture after MS1925

### Clearly demoted ingredient claims
Microseed SHALL NOT claim novelty merely for:
- capability vs authorization separation;
- runtime/current authorization checks;
- provenance / source ancestry;
- justification-bound revision;
- explicit UNKNOWN/ABSTAIN;
- information-seeking action;
- developmental intrinsic exploration;
- planner-free active learning;
- epistemic value;
- rival-model discriminating experiments;
- robust/misspecification-aware experimental design;
- history/recovery not automatically restoring authority.

These are all established or strongly analogous prior-art mechanisms.

### Remaining potentially distinctive composition — NOT a novelty claim
The strongest surviving hypothesis is an integration invariant:

> a minimal developmental cognitive substrate in which learned capabilities may compose and generate increasingly capable behavior while proposal, evidence, currentness, provenance, epistemic information, regulatory priority, qualification and execution authority remain separately represented and must be re-bound at the current action boundary, without a generic planner, curiosity scalar, global value policy or self-certifying model authority.

No source in this bounded pass was found to clearly instantiate that exact whole.

This is only:
`POTENTIALLY_DISTINCTIVE_COMPOSITION / UNRESOLVED`.

It is NOT sufficient for a novelty claim because:
1. the search is bounded, not exhaustive;
2. several close security/runtime-assurance/cognitive analogues exist;
3. combination novelty requires evidence beyond “I did not find the same combination”;
4. functional differences may be terminology or decomposition choices rather than deep mechanism differences;
5. independent specialist prior-art review remains open.

## Design pressure imported back into Microseed
1. Treat complete mediation / reference-monitor literature as a hostile analogue for every claim about current action authority.
2. Treat proof-carrying authorization as a hostile analogue for exact-premise-to-action binding.
3. Treat TMS/ATMS + PROV as hostile analogues for evidence ancestry/revision claims.
4. Treat selective classification as hostile analogue for abstention claims.
5. Treat active learning, intrinsic motivation and active inference as hostile analogues for information-seeking/developmental action.
6. Treat T-optimal/Bayesian/robust experimental design as hostile analogues for HSP/discriminator-selection claims.
7. Any future distinctiveness claim must state which *composition invariant* cannot be reduced to one of these known mechanisms and must survive an externally-derived counterexample.

## Source set contacted
Primary/seminal or authoritative contacts include:
- B. W. Lampson, “Dynamic Protection Structures,” AFIPS 1969, DOI 10.1145/1478559.1478563.
- J. H. Saltzer & M. D. Schroeder, “The Protection of Information in Computer Systems,” 1975.
- Anderson/reference-monitor lineage (1972) as summarized by NIST reference-monitor definition.
- A. W. Appel & E. W. Felten, “Proof-carrying authentication,” CCS 1999, DOI 10.1145/319709.319718; later proof-carrying authorization implementations.
- Simplex/runtime-assurance literature; modern Black-Box Simplex explicitly mediates controller authority at runtime.
- J. Doyle, “A truth maintenance system,” Artificial Intelligence 12(3), 1979, DOI 10.1016/0004-3702(79)90008-0.
- J. de Kleer, “An assumption-based TMS,” Artificial Intelligence 28(2), 1986.
- P. Buneman, S. Khanna, W.-C. Tan, “Why and Where: A Characterization of Data Provenance,” ICDT 2001.
- T. Green, G. Karvounarakis, V. Tannen, “Provenance Semirings,” PODS 2007.
- W3C PROV-DM Recommendation, 2013.
- C. K. Chow, “On optimum recognition error and reject tradeoff,” IEEE TIT 16(1), 1970.
- selective-classification literature including El-Yaniv & Wiener (2010).
- B. Settles, “Active Learning Literature Survey,” UW-Madison TR 1648, 2009.
- P.-Y. Oudeyer / F. Kaplan / V. Hafner developmental intrinsic-motivation work, 2007.
- K. Friston et al., “Active inference and epistemic value,” Cognitive Neuroscience 2015.
- A. C. Atkinson & V. V. Fedorov, model-discrimination experimental-design papers, Biometrika 62 (1975).
- A. C. Ponce de Leon & A. C. Atkinson (1991), rival-model discrimination with prior information.
- J. I. Myung & M. A. Pitt (2009), optimal experimental design for model discrimination.
- S. Ghosh & S. Dutta (2013), robustness of designs for model discrimination when the true model may lie outside the competing pair.

## Disposition
MS1925 is a RESEARCH / DEMOTION pass, not a production pass.

Novelty remains:
`UNKNOWN / NOT_ENTITLED_TO_CLAIM`.

The next useful move is not broader novelty narration. It is either:
- derive an externally-grounded bounded exploration-authority design from the now-contacted literature and pressure it against MS1922; or
- obtain an independent specialist prior-art challenge / blind external critique.

HSP remains advisory only; final frontier selection belongs to Attention Reservoir.
