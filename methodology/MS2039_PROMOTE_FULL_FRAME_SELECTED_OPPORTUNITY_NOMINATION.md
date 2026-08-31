# MS2039 — PROMOTE FULL-FRAME SELECTED OPPORTUNITY NOMINATION

## Goal
Promote the MS2038 research-only lifecycle into the runtime while preserving existing ownership boundaries:
- full-frame selection remains read-only selection authority only;
- endogenous UNKNOWN materialization remains the durability boundary;
- ordinary current epistemic step nomination remains the intent owner;
- execution remains zero.

## Runtime method
`Microseed.nominate_current_strict_full_frame_referent_epistemic_opportunity(...)`

The method SHALL:
1. rederive the current full-frame selection surface;
2. require `STRICT_FULL_FRAME_PARETO_REGULATORY_DOMINANCE_ONLY`;
3. recover the exact selected current owned opportunity;
4. materialize a content-bound endogenous `UNKNOWN_INCOMPLETE` including frame digest and selection commitment ancestry;
5. persist the selected ACTION_LIMITED deficit with marker `ENDOGENOUS_UNKNOWN_MATERIALIZED_AFTER_STRICT_FULL_FRAME_PARETO_SELECTION`;
6. delegate to ordinary current epistemic step intent nomination;
7. remain idempotent;
8. grant no execution authority.

## Hostiles
- trade-off -> ABSTAIN / zero deltas;
- dominance -> exactly one deficit + one intent + zero execution;
- second call -> zero deltas;
- incomplete current value frame -> ABSTAIN / zero deltas;
- selected UNKNOWN payload authority/frame digest exact;
- historical same-value nomination remains green.

## Nonclaim
Effect-time full-frame selection currentness is intentionally not repaired here. MS2040 shall attack stale execution after this production nomination path exists.


## First focused run — HARNESS TEST-PATH FAILURE
The first focused launcher failed before collecting tests because it referenced a non-existent historical path `test_ms2029_promote_selected_opportunity_persistence_and_nomination.py`; the live historical test is `test_ms2029_promote_selected_opportunity_persistence_nomination.py`.

Classification:
`MS2039_FOCUSED_HARNESS_TEST_PATH_MISMATCH__NO_SCIENTIFIC_VERDICT`.

The production nomination implementation and MS2039 tests had not yet received a scientific verdict at this point. Per research lineage policy this state is preserved before repairing the launcher path.
