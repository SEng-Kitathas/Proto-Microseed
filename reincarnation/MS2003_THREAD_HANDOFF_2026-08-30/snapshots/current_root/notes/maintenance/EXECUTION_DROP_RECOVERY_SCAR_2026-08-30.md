# Execution Drop / Hangup Recovery Scar — 2026-08-30

## Why this exists
Repeated conversation/tool turns dropped, stalled, or returned incompletely while the local project continued to advance. Treating each interruption as a simple retry hazard is incorrect because concurrent server/local work may complete between visible chat turns.

## Verified failure classes
1. **Tool-turn delivery loss / incomplete return surface**
   - A tool invocation may not return a visible result to chat even when the control plane remains healthy.
   - Absence of visible return is `UNKNOWN`, not failure and not success.

2. **Supervision / terminal-surface loss**
   - A job may produce passing stdout yet end with supervision loss or missing terminal status.
   - Printed PASS is not a seal witness unless terminal completion/readback is independently clean.

3. **Long-job buffering / synchronization fragility**
   - Whole-suite runs can outlive conversational tool-turn stability.
   - Long synchronous waits are a poor control surface for seal-critical verification.

4. **Concurrent advancement / tree movement during dropped turns**
   - Another executor or surviving server-side process may commit/push while chat appears stalled.
   - Recovery that blindly resumes an old plan can overwrite or duplicate legitimate progress.
   - Observed here: stale plan expected unsealed MS1998, but recovery snapshot showed HEAD and remote already at published MS1998 while an MS1999 worktree had begun.

5. **Concurrent writer / dirty-tree race**
   - Verification evidence is invalid if executable/test hashes move during the witness window.
   - A dirty tree must be snapshotted before and after verification.

6. **Continuity drift after interruption**
   - Chat memory can retain the last intended step while local persisted state has advanced.
   - Persisted project state outranks remembered plan after a drop.

## Recovery law
`MISSING_CHAT_RETURN != TASK_FAILURE`

`MISSING_CHAT_RETURN != TASK_SUCCESS`

`RECOVERY_INTENT != CURRENT_PROJECT_STATE`

`LOCAL_OR_REMOTE_ADVANCEMENT_AFTER_DROP != SAFE_TO_REPLAY_OLD_PLAN`

`PRINTED_PASS != TERMINAL_VERIFICATION`

## Required recovery sequence after any dropped/hung substantive turn
1. **Do not mutate immediately.**
2. Check control-plane health/project existence.
3. Read current persisted state / Live Shadow.
4. Snapshot branch, HEAD, dirty status, and remote research ref.
5. Compare snapshot to the pre-drop intended baseline.
6. If HEAD/tree/remote moved, invalidate the stale plan and re-ground on the new state.
7. Only then decide whether to resume, replay, or skip the interrupted action.
8. For long verification, prefer submitted server jobs with journaling/checkpoints/result paths over long synchronous conversational waits.
9. Read terminal job status separately from stdout.
10. Before seal, rehash executable/test surfaces and confirm tree stability.
11. After seal/push, independently `git ls-remote` the research ref.

## Execution-shape change
Default execution is now:
- one bounded mutation/inspection unit at a time;
- short synchronous commands for snapshots only;
- expensive tests submitted as server jobs;
- journaling/checkpoint/result paths enabled when available;
- no blind retries after a missing response;
- idempotency keys for persistent mutations;
- explicit post-drop local/remote reconciliation before resuming.

## Current incident resolution
Recovery found:
- control plane healthy;
- project/manifest/ledger present;
- research HEAD `66052ff913fc481336d96d866200e95e2dd96cd2`;
- independent remote readback matched exactly;
- Current State confirms MS1998 focused 26/26, whole 797/797, self-test 81/81, compile/diff PASS, frozen hashes stable, local seal/push/readback exact;
- active dirty frontier has already advanced to MS1999 hundred-capability scale/dependency work.

Therefore: do **not** rerun or rewrite MS1998. Re-ground on the MS1999 dirty tree and verify its provenance before continuing.
