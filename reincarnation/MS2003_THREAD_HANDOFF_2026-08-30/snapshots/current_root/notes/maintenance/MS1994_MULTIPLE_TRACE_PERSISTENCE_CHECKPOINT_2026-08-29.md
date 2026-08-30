# MS1994 Multiple-Trace Persistence Checkpoint — 2026-08-29

## Seal / publication
- Technical milestone: **MS1994**.
- Commit: `cd60c48a0fd8a4e0fea0995ca8550af2f8c394d3`.
- Tree: `6558b12e11198c336138516209a4aa7275581529`.
- Source/test snapshot: `fe2d67a8bf412fa522c089b757793a0c1ca2b429541523ae07b2311db5cb168a` / 318 Python files.
- Worktree clean at seal.
- GitHub `refs/heads/research/ms1888-replay`: remote readback exactly matched the seal.
- `origin/main`: unchanged at `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`.
- Canonical Main-Dev remains MS1527.

## Boundary
MS1993 showed one intervention-bound causal trace can strengthen operational persistence across a gap without proving numerical identity.

MS1994 tests two independent target traces plus unrelated nuisance under six hidden variants:
- persistent target with both traces;
- unmarked replacement;
- partial-copy replacement retaining A1 but losing A2;
- perfect-copy replacement retaining both;
- replacement with target traces lost plus nuisance change elsewhere;
- persistent target retaining both traces plus nuisance change elsewhere.

## Result
Existing referent functions are reused unchanged. A1/A2 trace deltas form a finite exact basis and post-gap evidence is represented as exact retained-trace topology, not a scalar vote.

Observed topology:
- persistent -> `{A1,A2}` / `SUPPORTED_BY_ALL_OBSERVED_TRACES`;
- unmarked replacement -> `{}` / `REFUTED_FOR_ALL_OBSERVED_TRACES`;
- partial copy -> `{A1}` / `MIXED_TRACE_EVIDENCE`;
- perfect copy -> `{A1,A2}` despite evaluator replacement;
- nuisance replacement -> target `{}` while unrelated group changes;
- persistent+nuisance -> target `{A1,A2}` while unrelated group changes.

Therefore:
`MULTIPLE_INDEPENDENT_INTERVENTION_TRACES_CAN_PRESERVE_EXACT_OPERATIONAL_PERSISTENCE_EVIDENCE_TOPOLOGY_ACROSS_A_GAP_WITHOUT_PROMOTING_NUMERICAL_IDENTITY`.

Authority ceiling:
- operational persistence: `TRACE_TOPOLOGY_RELATIVE_ONLY`;
- mixed conflict: preserve exact per-trace status, no majority collapse;
- numerical identity: NONE;
- semantic reference: NONE;
- language: NONE.

Perfect-copy replacement retaining all traces remains operationally indistinguishable from persistence.

## Mechanism verdict
No new referent-core mechanism was required. Do not add persistent object IDs, identity confidence voting, genealogy managers, or semantic object authority at this level.

## Verification
- focused referent regression `job-6ca5c8f0c398`: **16/16 PASS in 2.30s**;
- whole cleanup-neutral embodiment suite `job-72006a068385`: **791/791 PASS in 700.65s**;
- whole stderr empty;
- self-test 81/81 PASS;
- compileall PASS;
- diff-check PASS.

Executable/test candidate hashes matched exactly before and after whole verification.

## Concurrency scar
A concurrent writer briefly created an incompatible second untracked MS1994 scratch draft and then removed it while rewriting the same four intended MS1994 artifacts into a reconciled candidate. Verification began only after the four candidate files were stable. The final witnesses apply to the reconciled frozen tree.

## Remaining-work projection
Best-informed planning estimate after MS1994: **~7–14 further earned hostile campaigns** to the stronger robust self-sufficient prelingual threshold, moderate confidence.

Major remaining families:
1. hostile multi-referent crossing/occlusion/appearance change;
2. endogenous intervention/probe candidate construction from learned structure;
3. rich-world long-horizon online robustness;
4. separate constitutional choice for NAKED first-probe execution authority;
5. richer self/body operational continuity after external persistence.

Immediate next: multi-referent crossing/occlusion persistence under changing appearance, preserving trace currentness and identity refusal.