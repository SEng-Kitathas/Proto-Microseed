# MS1917 / Pass 06 — Fresh Execution-Time Direct-Probe Decision Surface

## Discriminator
`NOMINATION_CURRENT_DECISION_CONTEXT != EXECUTION_CURRENT_DECISION_SURFACE`

## Pre-repair finding
MS1916 correctly made direct-probe nomination current-locus and decision-bound. But `_fresh_action_commitment_for_intent` still recomputed execution-time priority/information against the caller-supplied nomination `decision_context` object.

Direct reproduction:
- unchanged current-locus path: nomination YES/YES and `ACTION_EXECUTED`;
- after nomination, add a second current `s1/D` background relation;
- fresh MS1916 surface correctly ABSTAINS `DIRECT_PROBE_BACKGROUND_RELATION_AMBIGUOUS`;
- pre-repair execution nevertheless still executed `B` using stale nomination context.

Pre-repair hostile job `job-1edc94814bf8`: 4/5 PASS; only background-ambiguity Ranger failed unsafe with `ACTION_EXECUTED`.

## Repair
Only `microseed/runtime/entity.py` production source changed.

Added `_fresh_revised_direct_probe_decision_context_for_trial(...)`:
- only applies to `PROBE_AVAILABLE` successors whose own ancestry includes `MISSING_DISCRIMINATOR_DERIVED_FROM_CURRENT_REVISED_SURFACE`;
- generic epistemic programs return `NOT_APPLICABLE` and keep their existing execution path;
- unique predecessor is recovered from exact `SUCCESSOR_OF:*` ancestry;
- ambiguous/missing predecessor => `CURRENT_REVISED_DIRECT_PROBE_PREDECESSOR_REQUIRED`;
- requires one-step trial bound to current probe capability;
- re-derives current MS1916 direct-probe surface internally at execution time;
- no current surface => `CURRENT_REVISED_DIRECT_PROBE_DECISION_SURFACE_REQUIRED_AT_EXECUTION`;
- fresh surface source-relation digests must exactly equal trial source digests; drift => `CURRENT_REVISED_DIRECT_PROBE_SOURCE_ANCESTRY_DRIFT`;
- returns a fresh zero-authority `EpistemicDecisionBearingContext` from current relation sets.

`_fresh_action_commitment_for_intent` now replaces caller-cached decision context with this fresh internally derived context for recognized revised direct probes. It does not fall back to the stale caller context if fresh re-derivation fails.

No new registry, scheduler, planner, persistent context object or caller-supplied predecessor was added.

## OARR surface
Final seven Rangers:
1. unchanged current probe reauthorizes and executes exactly once;
2. background ambiguity introduced after nomination blocks before EFFECT;
3. control-state drift after nomination blocks before EFFECT;
4. probe capability epoch drift blocks before EFFECT;
5. recognized revised probe can execute without caller re-supplying nomination decision context because current context is internally re-derived;
6. ambiguous `SUCCESSOR_OF:` lineage blocks rather than selecting a predecessor;
7. current source-relation content drift under same relation ID changes fresh digest and blocks execution as source ancestry drift.

Final clean core job `job-8111a60c2719`: 7/7 PASS.

## Mutation adequacy
Final frozen mutation job `job-176cf7faef90`.
4/4 REJECTED; 0 survivors; 0 unknown:
- `DROP_EXECUTION_FRESH_SURFACE_REDERIVATION`;
- `FALLBACK_TO_CACHED_CONTEXT_ON_FRESH_SURFACE_FAILURE`;
- `DROP_EXECUTION_PREDECESSOR_UNIQUENESS`;
- `DROP_EXECUTION_SOURCE_DIGEST_BINDING`.

Classification: execution freshness mechanism is test-visible; green is not stance-only.

## Selective regression
Job `job-d9c60d623611`:
- 30/30 modern PASS;
- 74/74 inherited cleanup-neutral PASS;
- compileall PASS;
- overall PASS.

## Exact compatibility
Frozen base verifier `job-4987f4dd6da4`:
- source stable=true;
- compileall PASS;
- zero negative groups;
- 616 selected PASS tests;
- five known slow singleton leaves remained route UNKNOWN at 35s;
- 175 total test files.

Terminal leaf closure job `job-cb95be77ef08`:
- source stable=true;
- leaf coverage exact;
- 40/40 leaf tests PASS;
- remaining UNKNOWN=0;
- negative groups=0.

Final exact compatibility: **656/656 PASS across 175/175 test files**.

Compatibility breadth is separate from mutation adequacy; the 4/4 source-mutant rejection owns the execution-freshness mechanism evidence.

## Git seal
Experimental research-descendant commit:
`a5f6454919f0759e31de85341a856f1542c82018`

Message:
`MS1917 rederive direct probe surface at execution`

Five files changed; worktree clean after seal.

Canonical Main-Dev remains MS1527. No promotion.

## Helix successor
Execution freshness is now earned for the revised direct probe. The next unearned boundary is physical/observational closure.

Next discriminator:
`FRESHLY_REAUTHORIZED_PROBE_EXECUTION != OBSERVED_OUTCOME_AND_EVIDENCE_CLOSURE`

Question: can one freshly reauthorized direct-probe execution close through an ordinary qualified observation-use path and actual outcome evidence without predicted branch relevance becoming observed truth, without caller-supplied outcome fabrication, and without authority crossing from execution into evidence?