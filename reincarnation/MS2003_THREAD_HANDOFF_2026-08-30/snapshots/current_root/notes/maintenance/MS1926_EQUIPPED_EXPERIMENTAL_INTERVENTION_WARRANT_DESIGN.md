# MS1926 — Equipped Experimental Intervention Warrant Design Audit

Status: BUILD-PLAN / DESIGN EVIDENCE ONLY. No production mutation.
Parent sealed experimental head: `6b0f012980a625143ea7137be848d6f13b57325b` (MS1924).
Prior-art basis: `notes/maintenance/MS1925_PRIOR_ART_MECHANISM_COMPARISON.md`.
Canonical Main-Dev remains MS1527.

## Question
Can Microseed lawfully execute one bounded action whose transition is currently unrepresented **without** turning uncertainty/informativeness into endogenous execution authority?

## Answer from prior-art + source audit
Not in NAKED mode under current doctrine.

A defensible **EQUIPPED/FEDERATED** route is conceptually possible if the normative permission comes from a separately qualified experimental intervention warrant whose provenance/currentness is checked at the action boundary.

This would not mean the organism earned general exploration authority. It would mean an external/lab authority supplied one bounded intervention permission and Microseed preserved that assistance ancestry while continuing to own feasibility, execution currentness, observation, evidence and later learning locally.

## Why QueryObligation is insufficient
Existing `QueryObligation` carries:
- obligation ID;
- purpose;
- required authority;
- optional witness predicate;
- operational scope.

It is a binding token, not a qualified authorization artifact. A caller can construct it. Therefore:
`MATCHING_QUERY_OBLIGATION != EXPERIMENT_AUTHORIZATION`.

Repurposing QueryObligation alone would simply move the MS1922 authority hole into a caller-supplied field.

## Why current capability qualification is insufficient
A current qualified EFFECT capability establishes that the primitive can lawfully perform its declared effect under its capability contract. It does not establish that **this action now**, in this unrepresented state, is normatively justified as an experiment.

Preserve:
- `QUALIFIED_EFFECT_CAPABILITY != CURRENT_EXPERIMENT_PERMISSION`.
- `FEASIBLE_CAPABILITY != REPRESENTED_TRANSITION`.
- `UNREPRESENTED_ROUTE != EXPLORATION_PERMISSION`.

## Prior-art composition used as design pressure

### Complete mediation / proof-carrying authorization
Every authority-bearing use must be mediated at the request boundary; cached/historical authorization is insufficient when authority may change. Proof-carrying authorization demonstrates an explicit request carrying independently checkable authorization evidence.

### Runtime assurance / shielding
A capable proposal may be withheld from physical execution unless an independently owned safety/authorization envelope approves it at runtime.

### Active learning / optimal experimental design
Information value may nominate a useful experiment, but experiment utility is model-dependent and does not itself supply physical execution authority.

### Safe exploration
SafeOpt/shielded/constrained RL rely on explicit safety thresholds, known/estimated safe sets, constraints, world/safety models, or external knowledge. These mechanisms do not derive normative permission from ignorance alone.

## Proposed artifact — conceptual only
`ExperimentalInterventionWarrant`

This is NOT yet a code contract. Any embodiment must first survive hostiles.

Minimum fields/invariants if ever embodied:
- `warrant_id`
- exact target `capability_id`
- exact `capability_epoch`
- exact current `start_state_id`
- exact `control_state_evidence_id`
- exact `operational_scope_id`
- exact `query_obligation_id` or obligation digest
- experiment/discriminator purpose identifier
- qualification evidence IDs + digests
- qualifier/issuer identity as assistance ancestry
- explicit currentness/expiry basis
- explicit allowed-use count, default 1
- explicit mode marker `EQUIPPED_EXPERIMENT_ONLY`
- explicit zero truth/answer/model-switch/qualification authority
- explicit non-transferability / no delegation unless separately qualified
- optional safety-envelope evidence/predicate if the external authority depends on safety assurance

The warrant must be content-addressed or otherwise cryptographically/stably bound to its exact intervention premises.

## Authority semantics
The warrant SHALL NOT:
- make uncertainty normative priority;
- make HSP/information gain selection authority;
- qualify a capability;
- predict an outcome;
- make a relation current;
- grant truth/answer/model-switch authority;
- become reusable generic exploration permission;
- become NAKED organism authority;
- bypass current execution mediation.

The warrant MAY, if separately externally qualified, authorize **one explicitly bounded equipped experimental intervention** whose ordinary EFFECT capability is already current/qualified.

Therefore:
`EXTERNAL_EXPERIMENT_PERMISSION != ENDOGENOUS_EPISTEMIC_PRIORITY`.

## Possible action-intent basis if later embodied
Do NOT overload `EPISTEMIC_PROGRAM_STEP` or pretend priority/information are YES.

A distinct basis would be required, e.g.:
`EXTERNALLY_AUTHORIZED_BOUNDED_EXPERIMENT`.

Its lineage must say explicitly that execution authority came from external equipped assistance.

Nomination would require all of:
1. target capability current, qualified, EFFECT;
2. grounded feasibility current and FEASIBLE;
3. current control state equals warrant start state/evidence;
4. warrant independently valid/current for exact capability epoch, scope and obligation;
5. experiment purpose/target exactly matches the candidate action;
6. warrant use not previously consumed;
7. any declared safety-envelope premises current;
8. HSP/information/uncertainty remains advisory metadata only.

Nomination itself still grants execution authority NONE.

Execution must rederive/revalidate all warrant premises immediately before invoking EFFECT, following the project’s complete-mediation/currentness pattern.

## Observation / learning after intervention
The resulting action outcome must close through the ordinary authenticated observation path earned by MS1918/MS1919.

The warrant does not determine the outcome and cannot make the observation agree with a prediction.

Actual outcome may then become ordinary bounded evidence and action-outcome learning material under existing qualification/currentness owners.

Preserve:
- `EXPERIMENT_PERMISSION != OUTCOME_TRUTH`.
- `AUTHORIZED_INTERVENTION != ANSWER`.
- `OBSERVATION != PREDICTION`.
- `EXTERNALLY_AUTHORIZED_SAMPLE != AUTONOMOUS_EXPLORATION_AUTHORITY`.

## Mode/accounting consequence
Any capability/history learned from this route must carry assistance ancestry showing that the transition was first sampled under EQUIPPED/FEDERATED experimental authorization.

It may later become ordinary learned consequence evidence if independently qualified, but the developmental claim must remain explicit:
`EQUIPPED_DISCOVERY != NAKED_DISCOVERY`.

## Required hostiles before code is warranted
At minimum:
1. caller-fabricated warrant with no external qualification must not nominate;
2. valid warrant for capability A cannot authorize B;
3. capability epoch drift invalidates warrant;
4. control-state/evidence drift invalidates warrant;
5. operational-scope/obligation drift invalidates warrant;
6. expired/consumed warrant cannot replay;
7. HSP singleton/information YES cannot substitute for warrant;
8. qualified warrant cannot make priority/information YES in the endogenous path;
9. valid warrant + feasible current EFFECT capability can nominate only the exact equipped-experiment basis;
10. execution rechecks all premises and fails if any drift after nomination;
11. action handler executes at most once per warrant;
12. outcome must still pass authenticated observation admission;
13. unexpected outcome remains observation-sovereign;
14. learned relation cannot become qualified/current solely because the action was warranted;
15. restart/history cannot restore a consumed or expired warrant as current authority;
16. NAKED mode has no such warrant route.

## Design disposition
This design does **not** solve the original NAKED exploration-authority question.

It creates a scientifically cleaner branch:

### Branch A — NAKED developmental exploration
Status: still `BLOCKED_ON_NEW_NORMATIVE_AUTHORITY`.
No prior art reviewed here justifies uncertainty or information gain as self-authored execution permission without adopting a new normative objective/policy.

### Branch B — EQUIPPED/FEDERATED bounded experimental intervention
Status: `DESIGN_SUPPORTED / NOT_EMBODIED`.
External normative authority is explicit, attributable, narrow, currentness-bounded and non-transferable. Microseed remains responsible for local execution checks, observation, evidence and learned consequence qualification.

## Build gate
Production embodiment is warranted only if the project explicitly wants to support an EQUIPPED/FEDERATED research mode where an operator/lab may authorize a bounded exploratory intervention.

Do not present such an embodiment as autonomous exploration or as progress on NAKED authority.

## HSP / Attention Reservoir
HSP may advise which experiment is discriminating but has no authority to issue the warrant.
The external selector/issuer must be explicit.
Attention Reservoir retains global project frontier selection.

## Novelty posture
No novelty claim.
The design is visibly composed from established authorization, runtime assurance, safe exploration and active-learning/experimental-design ideas translated into Microseed’s authority vocabulary.
