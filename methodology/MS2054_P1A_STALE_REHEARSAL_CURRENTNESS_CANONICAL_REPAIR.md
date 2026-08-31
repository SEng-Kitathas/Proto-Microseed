# MS2054 — P1A Stale-Rehearsal Currentness Canonical Repair

## Operator authority
Operator explicitly authorized P1A + N1A execution on 2026-08-31. This milestone performs P1A only. N1A embodiment follows from the repaired baseline and is not smuggled into this promotion.

## Problem promoted from research
Canonical PRELINGUAL_SUBSTRATE_V1 allowed a durable counterfactual rehearsal proposal to remain CURRENT after the learned predictive relation owning its transition premise became STALE under empirical drift.

Violation: `STALE_PREDICTIVE_RELATION_CAN_REMAIN_EXECUTION_PREMISE_THROUGH_DURABLE_REHEARSAL_REUSE`.

## Narrow repair
`Microseed.counterfactual_rehearsal_status()` resolves each owned transition-relation digest against learned predictive relations. If matching learned owners exist and none is current, the rehearsal becomes `UNKNOWN_INCOMPLETE` with no authority.

Law: `DURABLE_REHEARSAL_REUSE_DOES_NOT_OUTLIVE_THE_CURRENTNESS_OF_ITS_OWNED_LEARNED_TRANSITION_PREMISE`.

Supplied-row relations without a learned-registry owner continue through historical premise checks; no new currentness owner or manager is introduced.

## Historical fixture corrections
MS1452 and MS1943 no longer execute a stale learned zero-row proposal merely to collect recovery observations. Recovery sampling uses the retained supplied-row seed proposal.

Law: `RECOVERY_OBSERVATION_COLLECTION != STALE_MODEL_EXECUTION_AUTHORITY`.

## Promotion shape
Only `microseed/runtime/entity.py` changes production bytes relative to tagged V1. Soak scaffolding remains research history. The historical V1 tag remains immutable; MS2050 verifies that tagged V1 against its frozen whole-suite subject.

## Prior earned evidence
Research descendant `3e95bb520307b5b2a0dc4d292655f0d9c3a76014` earned focused 17/17 PASS, 1,200-episode soak PASS, and 912 applicable cleanup-neutral regressions with only the historical identity guard deselected.

This dedicated promotion reruns focused and whole regression before canonical push/tag.

## Authority boundary
P1A repairs stale-model authority leakage only. It grants no NAKED, language, semantic identity, or new selection authority.
