# MS2024 — SELECTED OPPORTUNITY PERSISTENCE AND ORDINARY NOMINATION

## Question
Can the bounded MS2023 cross-deficit selection commitment be composed into the existing durable deficit + ordinary epistemic nomination path without introducing a cross-deficit scheduler or persistent opportunity registry?

## Intended composition
1. Enumerate current owned referent epistemic opportunities ephemerally.
2. Re-derive strict same-value regulatory dominance.
3. Require one MS2023 YES selection commitment.
4. Match the commitment's exact selected deficit/probe to one current opportunity.
5. Materialize a content-bound endogenous `UNKNOWN_INCOMPLETE` evidence record for the selected ambiguity, following the existing endogenous-discovery pattern that marks self-generated structure as proposal/unknown rather than external support.
6. Persist only that selected deficit with existing `record_action_limited_unknown`.
7. Reuse `nominate_endogenous_epistemic_program_step_intent_from_current_surface` unchanged.

## Laws
- tie => persist nothing, nominate nothing;
- selection commitment grants no execution authority;
- the adapter may not change hypothesis/discriminator/probe/decision content;
- no caller supplies the winner; matching is from the commitment's content-bound selected deficit/probe ids;
- raw observation remains provenance, not the durable UNKNOWN record itself;
- the endogenous UNKNOWN record must be content-bound to the selected deficit, binding, probe, trial digest, priority/information/step commitments, raw source evidence, and cross-deficit selection commitment;
- no generic queue/scheduler/opportunity registry is introduced.

## Hostiles
- symmetric P2/P4 tie: no durable deficit and no intent;
- asymmetric same-value strict dominance: exactly one durable selected deficit and exactly one P2 intent, with zero handler calls;
- current value observation drift before selection: no durable deficit and no intent.

## First execution result — LIFECYCLE FAILURE, preserved
The symmetric tie path abstained as intended. The asymmetric selected path reached durable registration and then failed in `record_action_limited_unknown` with `EPISTEMIC_DEFICIT_REQUIRES_UNKNOWN_INCOMPLETE_EVIDENCE`.

The transient MS2021/MS2022 opportunity's `EpistemicDeficitRecord` is constructed over a current owned raw-evidence premise for read-only opportunity evaluation. The durable deficit owner, correctly, requires its `unknown_evidence_id` to name an explicit evidence record whose disposition is `UNKNOWN_INCOMPLETE`.

Classification: `EPHEMERAL_OPPORTUNITY_PREMISE != DURABLE_UNKNOWN_EVIDENCE_LIFECYCLE`.

## Repair hypothesis 1 — endogenous UNKNOWN materialization
Source audit found an existing precedent in `discover_capability_candidates`: Microseed writes its own derived proposal as `UNKNOWN_INCOMPLETE` evidence so self-generated inference cannot masquerade as external support. MS2024 therefore attempted to materialize a selected, content-bound UNKNOWN record after strict cross-deficit selection and before durable deficit registration.

### Repair attempt 1 result — HARNESS SHAPE FAILURE, preserved
The attempt did not reach UNKNOWN materialization. It assumed the selected MS2021 opportunity contained MS2014-style `opportunity_id` / `content_signature_sha256` fields; the live MS2021 opportunity object does not expose `opportunity_id`, raising `KeyError: 'opportunity_id'`.

Classification: `REPAIR_ADAPTER_ASSUMED_LATER_OPPORTUNITY_SHAPE__NO_SCIENTIFIC_VERDICT`.

## Repair attempt 2 — actual live opportunity schema
The UNKNOWN payload was rebound only to fields the MS2021 opportunity actually owns: selected ephemeral deficit id/content, binding id, probe id, trial id/digest, priority commitment id, owned-observable information commitment id, step commitment id, source raw observation evidence id, and MS2023 selection commitment id.

### Result — PASS
- symmetric P2/P4 tie: `ABSTAIN`; deficit/intent/execution deltas all zero;
- asymmetric same-value strict dominance: exactly one endogenous UNKNOWN evidence record, exactly one durable selected ACTION_LIMITED deficit, exactly one P2 action intent, zero executions and zero handler calls;
- fresh current value observation inside the viable interval before selection: opportunity surface disappears and no durable deficit/intent is created;
- ordinary nomination re-derives priority and owned observable information from the newly persisted deficit; no new nomination/execution owner is required.

Earned distinction:
`SELECTED EPHEMERAL OPPORTUNITY != DURABLE DEFICIT UNTIL ENDOGENOUS UNKNOWN IS MATERIALIZED`.

No scheduler, weighted utility, persistent opportunity registry, or execution authority is earned.
