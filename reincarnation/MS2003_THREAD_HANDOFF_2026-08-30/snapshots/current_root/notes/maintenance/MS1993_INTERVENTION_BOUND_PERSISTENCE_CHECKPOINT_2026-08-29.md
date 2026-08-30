# MS1993 Intervention-Bound Persistence Checkpoint — 2026-08-29

## Seal / publication
- Technical milestone: **MS1993**.
- Commit: `76db4aa62c802fb744aca4d6a66ad4fb78d3cbd6`.
- Tree: `320fbcd6cf052566bc6728a27e0e5414d1bcec1f`.
- Source/test snapshot: `d0ee7d63bced63e64a703ea09ad87b5b5f34c119d3adda3486bd927460689f7f` / 317 Python files.
- Worktree clean at seal.
- GitHub research ref remote readback exactly matched the seal.
- `origin/main` unchanged at `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`.
- Canonical Main-Dev remains MS1527.

## Boundary
Existing referent work could re-associate affordance-relative proto-referents after a gap but could not distinguish persistence from hidden same-affordance substitution.

MS1993 added a separate process world where an already represented intervention `FX-MARK-A` leaves a persistent additive trace on exactly one nominated referent group.

Three evaluator worlds:
1. persistent source + retained trace;
2. unmarked replacement + trace loss;
3. perfect-copy replacement + retained trace.

The organism route receives only channel observations and existing action interfaces. Evaluator generation counters are used only as hidden falsification truth.

## Result
The existing referent composition was sufficient:
- boundary coherence nominated the same target group;
- affordance-relative signature re-associated that group after the gap;
- the intervention trace remained content-bound to exact before/after values, delta, group, and action ID.

Persistent world:
- trace retained;
- evaluator persistence true;
- operational persistence support `SUPPORTED`.

Unmarked replacement:
- same affordance signature/group;
- trace lost;
- evaluator persistence false;
- operational persistence support `REFUTED_FOR_THIS_TRACE`.

Perfect-copy replacement:
- same affordance signature/group;
- trace retained;
- evaluator persistence false;
- organism-visible evidence indistinguishable from persistent world.

Earned:
`INTERVENTION_BOUND_CAUSAL_TRACE_CAN_SUPPORT_OPERATIONAL_PERSISTENCE_ACROSS_AN_OBSERVATION_GAP_WITHOUT_ESTABLISHING_NUMERICAL_IDENTITY`.

No new referent-core mechanism was required.

Authority ceiling:
- operational persistence: TRACE_RELATIVE_ONLY;
- numerical identity: NONE;
- semantic reference: NONE;
- language: NONE.

## Verification
- focused MS1958–MS1970 + MS1993: `job-7e970e912589` -> **11/11 PASS in 1.71s**;
- whole cleanup-neutral embodiment suite: `job-65c8c2e1d49f` -> **790/790 PASS in 494.89s**;
- whole stderr empty;
- self-test 81/81 PASS;
- compileall PASS;
- diff-check PASS.

## Interpretation
MS1993 strengthens external operational persistence without creating an object-ID registry or metaphysical identity claim. It is another composition result where the behavior was reachable from already-earned mechanisms.

## Projection consequence
After MS1993, best internal engineering assessment is that the research descendant has crossed the threshold of an **early recognizable prelingual substrate prototype**. Remaining work to a robust/self-sufficient prelingual substrate is dominated by richer persistence, endogenous experiment construction/selection, lawful first-probe authority, and combined rich-world lifetime pressure.

See:
`notes/maintenance/PRELINGUAL_SUBSTRATE_REMAINING_WORK_PROJECTION_2026-08-29.md`.