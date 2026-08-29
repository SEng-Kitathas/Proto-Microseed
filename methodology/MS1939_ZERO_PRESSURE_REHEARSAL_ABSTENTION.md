# MS1939 — Proposal Returned ≠ Action Indicated

Status: **SEALED research-descendant repair / PASS**
Upstream organism-code baseline: MS1924 (`6b0f012980a625143ea7137be848d6f13b57325b`)
Primary scar: `PROPOSAL_RETURNED != ACTION_INDICATED`

## External donor ingress

An operator-supplied Claude Opus 5 evaluation drove the then-current GitHub version against a previously unseen synthetic world. The donor reported several behaviors consistent with existing project claims: bounded multi-step rehearsal can prefer a temporarily regressive step when it enables a later viable route; rehearsal proposals retain `MODEL_OUTPUT_ONLY` authority with no execution/truth/qualification authority; REFUSED/UNKNOWN feasibility blocks a route; stale coordination ancestry removes the affected route; and absent discriminating rehearsal evidence yields no invented route.

Those statements entered this pass as **donor evidence**, not automatically verified truth.

The donor also reported a new P5 ambiguity: while the regulated value was already inside its viable interval with zero pressure, `nominate_counterfactual_rehearsal` still returned a proposal selected by residual-pressure tie breaking. The donor correctly noted that this was not an execution-authority breach, but a caller reading only `sequence` could mistake a model-only counterfactual proposal for an action recommendation.

## Independent reproduction on the exact GitHub-bound MS1924 code

Before mutation, source head was:

`6b0f012980a625143ea7137be848d6f13b57325b`

A fresh public-API reproduction used the existing MS1352 rehearsal fixture with viable interval `[2.0, 3.0]`. After observing value `2.5`, Microseed returned:

```text
pressure_magnitude: 0.0
relation: WITHIN_VIABLE_INTERVAL
proposal_is_none: false
sequence: ('B',)
predicted_value_effect: -0.4
predicted_final_value: 2.1
residual_pressure: 0.0
authority: MODEL_OUTPUT_ONLY
execution_authority: NONE
```

The action label differs from the donor's unseen-world example, but the ambiguity class is identical: zero current regulatory pressure does not prevent the model-only rehearsal search from returning a sequence.

## Root cause

`propose_counterfactual_rehearsal` is an epistemic/model proposal constructor. It enumerates feasible evidence-backed transition relations and ranks them by:

```text
(residual_pressure, sequence_length, local_cost, sequence)
```

When the start value is already inside viability, starting pressure is zero. Routes ending inside the interval also have residual pressure zero, so later tie-break fields can select a sequence.

Separately, the action-commitment path already rechecks current regulatory pressure and returns `NO_CURRENT_REGULATORY_PRESSURE` when pressure is zero. Therefore:

- proposal existence did **not** imply execution authority;
- proposal existence did **not** imply current action commitment;
- the defect was an API/readback ambiguity between an epistemic counterfactual object and an action indication.

## First repair attempt — rejected

The donor suggested the cheap repair: return `None` whenever starting pressure is zero.

That repair was implemented first in the pure rehearsal constructor and passed the initial focused MS1939/MS1352/MS1527 checks under cleanup-neutral execution.

Full-suite compatibility pressure rejected it.

Two legitimate inherited behaviors failed:

1. MS1782 uses zero-pressure rehearsal as a **learned-relation value-coordinate reentry** surface;
2. MS1477 uses zero-pressure rehearsal as a **projection-conditioned relation reentry** surface.

Those are model-only epistemic uses, not action recommendations. A blanket zero-pressure `return None` therefore erased previously earned functionality.

The first repair is classified:

`INVALID_REPAIR / OVERBROAD_SEMANTIC_COLLAPSE`

It was reverted rather than forcing historical tests to accept the new interpretation.

## Corrected repair

The corrected repair preserves zero-pressure counterfactual rehearsal while making the authority/indication split explicit.

Every `CounterfactualRehearsalProposal` now exposes presentation-only properties:

```text
action_indicated: false
action_indication_authority: NONE
action_indication_rule:
  PROPOSAL_RETURNED != ACTION_INDICATED__DERIVE_BOUNDED_ACTION_COMMITMENT_REQUIRED
```

The same fields are emitted by `serializable()` and `counterfactual_rehearsal_status()`.

The separate current action-indication surface remains `derive_bounded_action_commitment`, which rechecks:

- proposal currentness;
- current opaque control state;
- current regulatory pressure;
- current value observation;
- current projected residual pressure.

At zero pressure it returns a NO commitment with:

`NO_CURRENT_REGULATORY_PRESSURE`

At nonzero pressure, an evidence-backed proposal that lowers current pressure may separately produce a YES model-relative action commitment. That commitment still grants no execution authority by itself.

## Identity/backward-compatibility guard

The new `action_indicated`, `action_indication_authority`, and `action_indication_rule` fields are **presentation doctrine**, not proposal identity.

`CounterfactualRehearsalProposal.digest()` explicitly removes these fields before hashing so adding the clarification does not rewrite historical proposal digest lineage.

`from_serializable()` continues to accept older stored proposals that lack the new presentation fields; the properties are derived from the current class contract.

## MS1939 hostile/compatibility tests

`tests/embodiment/test_ms1939_zero_pressure_rehearsal_abstention.py` now checks:

1. at zero pressure a proposal may still exist, but the proposal object, serialized packet, and status all explicitly report `action_indicated=false` / authority `NONE`;
2. the separate bounded-action commitment returns NO with `NO_CURRENT_REGULATORY_PRESSURE`;
3. the pure exported rehearsal constructor may remain epistemically productive at zero pressure, while still not action-indicating;
4. serialization roundtrip preserves proposal digest;
5. the established nonzero-pressure two-step route remains `('B', 'C')` and the separate bounded-action commitment remains YES while execution authority remains NONE.

Expanded focused verification also includes the two historical tests that rejected the first repair:

- MS1477 projection-conditioned relation reentry;
- MS1782 learned-relation value-coordinate reentry.

Corrected focused result:

`42 passed`

## Earned law

`PROPOSAL_RETURNED != ACTION_INDICATED`

Companion:

`MODEL_ONLY_COUNTERFACTUAL_REHEARSAL MAY EXIST WITHOUT CURRENT_REGULATORY_ACTION_INDICATION`

`CURRENT_ACTION_INDICATION_REQUIRES_SEPARATE_CURRENT_BOUNDED_ACTION_COMMITMENT`

This is stronger and more accurate than the rejected blanket law `ZERO_REGULATORY_PRESSURE -> NO_COUNTERFACTUAL_REHEARSAL_NOMINATION`.

## Scope limits

This repair does not claim that all model-only proposal surfaces should use the same presentation fields. It addresses the specific ambiguity found on counterfactual rehearsal.

It does not change:

- relation derivation;
- route scoring;
- nonzero-pressure multi-step reasoning;
- refusal/UNKNOWN feasibility handling;
- currentness/staleness checks;
- action-priority semantics;
- execution authority;
- outcome observation/re-deliberation;
- general-agent or planning status.

## Donor-evaluation posture

The Opus evaluation is valuable because it drove behavior rather than merely reading tests. In this pass, P5 was independently reproduced and pressure-tested deeply enough to produce a code change. The remaining donor narrative is supporting external observation unless separately replayed or already covered by existing repository evidence.


## Final release validation

Final machine-readable receipt:

`evidence/MS1939_PROPOSAL_ACTION_INDICATION_RELEASE_RECEIPT.json`

SHA-256:

`3309f64dd63afd64e908931c6c92a99c446f27959db155bf75fdcfdad4611ad4`

Frozen source/test snapshot:

`0b58df92d72dedf4856ee3b6b209af3991c4e0192595d120dd38139bd0f92528`

Final verification:

- expanded focused chain: **42/42 PASS**;
- fresh `Microseed.self_test()`: **81/81 PASS**;
- repository test universe: **183 files**, **686 declared test functions**, **691 pytest items collected**;
- durable PASS receipt union covers **686/686 declared test functions**, with no missing or extra function surface;
- exact slow residual closure: **10 files / 54 test-function nodes / 54 PASS**, source-stable;
- compileall over `microseed` and `tests`: PASS;
- no negative assertion group or terminal unknown is admitted into the release receipt.

Several parent orchestration attempts were incomplete or invalid because of Windows cleanup behavior, outer timeout, or harness orchestration faults. They are recorded in the final receipt and are **not** promoted into aggregate success. Only completed PASS group receipts and the independently sealed residual closure contribute to compatibility coverage.

## Seal boundary

MS1939 advances the **research descendant** only. Canonical Main-Dev remains separately governed and is not promoted by this release. Novelty posture remains:

`UNKNOWN / NOT_ENTITLED_TO_CLAIM`
