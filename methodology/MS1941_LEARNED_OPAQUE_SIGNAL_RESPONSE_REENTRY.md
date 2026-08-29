# MS1941 — Learned Opaque Signal-Response Reentry

Date: 2026-08-29 ET
Status: bounded production bridge + hostile regression
Parent research head at start: `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`

## Question
Can the MS1940 opaque signal-response association be learned from actual admitted execution/outcome history, externally qualified, and then reused by ordinary bounded rehearsal with **zero supplied transition rows**, while preserving all modern evidence-premise ancestry and without promoting token meaning, reference, truth, or language?

Prewritten scars:
- `LEARNED_SIGNAL_RESPONSE != TOKEN_MEANING`;
- `LEARNED_ASSOCIATION != REFERENCE`;
- `MODEL_RESOLVED != TRUTH_AUTHORIZED`.

## Prior state
MS1940 established that signaling itself required no new production subsystem:
- supplied opaque token `T0` emitted through an existing EFFECT capability;
- current opaque counterparty/coordination relation;
- external observation changed `NO_ACK -> ACK`;
- drift staled the route;
- no reference/meaning/identity/language authority appeared.

But MS1940 still supplied rehearsal-transition evidence describing the signal-response relation.

## Learning path already present
The organism already contained:
1. actual bounded execution;
2. external outcome observation;
3. `ActionOutcomeExperience` extraction;
4. `ActionOutcomePredictiveCandidate` nomination;
5. exact subject-bound external holdout qualification;
6. `QualifiedActionOutcomePredictiveRelation`;
7. ordinary rehearsal supplementation from qualified learned relations.

No signal-specific learner was required.

## First MS1941 attempt — subject-binding failure
Durable job `job-eae464735826` reached learned candidate formation but external qualification was rejected.

Cause: the experimental holdout packet omitted the candidate's `evidence_premise_epochs` / `evidence_premise_signatures`.

The existing qualifier correctly treated those rows as a different subject and gave no qualifying support.

Classification:
`INVALID_EXPERIMENT_PACKET / SUBJECT_BINDING_INCOMPLETE`.

This directly confirms the adopted RAHL rule:
`WITNESS_SUBJECT_RESOLUTION_IS_PART_OF_WITNESS_CORRECTNESS`.

The holdout packet was corrected; qualification thresholds were not weakened.

## Second attempt — genuine architecture boundary
Durable job `job-e198e4b5169a` then:
- accumulated 12 actual signal executions/outcomes;
- nominated a 12-support / 1.0-consistency learned relation;
- passed exact subject-bound external holdout qualification;
- admitted a current learned relation;
- failed to produce ordinary rehearsal when supplied transition rows were empty.

Root cause:
`QualifiedActionOutcomePredictiveRelation.as_rehearsal_relation()` still returned `None` whenever evidence-premise ancestry was non-empty.

That refusal was historically justified by MS1620/MS1779 because the **durable `CounterfactualRehearsalProposal` did not carry evidence-premise ancestry**.

However, MS1780 later added exact `evidence_premise_epochs` and `evidence_premise_signatures` to `RehearsalTransitionRelation` for ephemeral epistemic alternatives. The edge carrier had evolved, but the durable ordinary proposal/currentness bridge had not.

Therefore the remaining seam was not a missing signaling mechanism. It was a stale loss-prevention boundary around an incomplete durable carrier.

## Minimum sufficient bridge
MS1941 changes only three production surfaces.

### 1. Durable proposal carrier
`CounterfactualRehearsalProposal` now optionally carries:
- `evidence_premise_epochs`;
- `evidence_premise_signatures`.

Empty ancestry remains backward-compatible: the new fields are omitted from digest input when empty so legacy proposal digest identity does not change.

Known pre-MS1941 legacy fixture digest preserved:
`22741c348c8efe347201c9e98fe27e4c21a0076ec2cba6f14338ff9fb093b8f7`.

### 2. Path aggregation
`propose_counterfactual_rehearsal` unions exact premise ancestry from chosen relations.

If the same premise ID appears with conflicting epochs or signatures inside one chosen path, proposal construction fails closed rather than choosing one silently.

### 3. Currentness / learned bridge
- `QualifiedActionOutcomePredictiveRelation.as_rehearsal_relation()` may now carry evidence-premise ancestry losslessly.
- `counterfactual_rehearsal_status()` rechecks premise qualification, epoch, and exact capability signature on every durable proposal readback.

No new planner, registry, signaling ontology, semantic token type, or language subsystem is added.

## Historical guard supersession
MS1620/MS1779's old enforcement—ordinary learned relation conversion must return `None` when evidence-premise ancestry is present—remains historically correct for the old durable carrier.

MS1941 supersedes **current enforcement**, not the historical scar:

`LOSSY_CONVERSION_FORBIDDEN` remains true.

What changed is that ordinary durable conversion is no longer lossy once the proposal itself carries/rechecks the ancestry.

This follows the adopted doctrine:
`SCAR_SURVIVES_AS_HISTORY != SCAR_ENFORCEMENT_SURVIVES_FOREVER`.

## Positive result
Durable job `job-9f82edc21ae2` after the bridge:
- training executions/outcomes: 12;
- learned candidate support: 12;
- consistency: 1.0;
- coordination ancestry: `R@0`;
- external qualification holdouts: 20;
- qualified relation: `ACTION-LAW-787256d3f7101553b22d` in that isolated run;
- supplied transition rows at reuse: 0;
- learned rehearsal sequence: `SIG-T0`;
- learned path: `S0 -> CP-ACK`;
- truth authority: NONE;
- execution authority: NONE;
- semantic-goal authority: NONE;
- coordination drift staled relation and removed it from rehearsal;
- language remained `DEFERRED_PRELINGUAL_COGNITION_ACTIVE`.

## New hostile requirements
Regression coverage additionally requires:
- evidence-premise epoch invalidation stales both learned relation and durable proposal;
- evidence-premise signature mutation stales durable proposal even without epoch change;
- legacy empty-ancestry proposal digest remains byte-identical;
- coordination drift still invalidates the signal capability/relation;
- zero-row learned rehearsal does not gain truth/execution/semantic-goal authority.

## Earned result
`LEARNED_OPAQUE_SIGNAL_RESPONSE_REENTERS_REHEARSAL` under the bounded synthetic fixture.

More precise statement:

> Repeated actual signal/outcome experience can nominate an opaque action-response predictive relation; independently subject-bound holdout evidence can qualify it; and the current relation can re-enter bounded rehearsal without supplied transition rows while exact evidence-premise ancestry remains durable and currentness-checked.

## Authority / semantic ceiling
This does **not** establish:
- token meaning;
- reference;
- object semantics;
- mutual semantic intention;
- persistent other-agent identity;
- endogenous token invention;
- endogenous coordination-contract creation;
- open-world truth;
- language.

The token, counterparty contract, coordination relation, regulatory value, observation channel, qualification boundary, and finite rehearsal grammar remain supplied/externally bounded.

## Next discriminator
The next signaling-specific seam is no longer predictive association. It is **convention currentness/discovery authority**:

> When repeated external outcomes contradict a previously qualified signal-response relation, can existing empirical predictive-currentness machinery expose that the learned operational association is stale without autonomously declaring a new token meaning or rewriting the externally supplied coordination contract?

This should be attacked through existing predictive-currentness/drift mechanisms before adding any convention learner.

Prewritten boundaries:
- `PREDICTIVE_DRIFT != SEMANTIC_CONVENTION_CHANGE`;
- `STALE_SIGNAL_MODEL != NEW_TOKEN_MEANING`;
- `MODEL_REPLACEMENT != COORDINATION_CONTRACT_REWRITE_AUTHORITY`.
