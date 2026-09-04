# Frontier F VALUE Replay on R4.2 / B-C Canon — 2026-09-04

Status: **REPLAY VERIFIED / RESEARCH ONLY / NO CANON CHANGE / NO PRODUCTION DELTA**

## Base / source
- Current public base: `809318630f656e712cde612e9ec3378af8872329`.
- Replay branch: `research/frontier-f-value-replayed-on-r42-bc-canon-v1`.
- Source: `research/frontier-f-value-v1` -> `45e0e45f915990318824f0dd588728ce56fc27e0`.
- Replayed only F-specific campaign artifacts, methodology, and embodiment test. Shared Wave1 recovery/controller files were intentionally excluded.

## Claim under replay
`CURRENT_FULL_FRAME_CROSS_VALUE_SELECTION_USES_STRICT_PARETO_DOMINANCE_AND_DOES_NOT_REQUIRE_OR_REVEAL_A_HIDDEN_WEIGHTED_SUM_ARBITER_IN_THE_TESTED_PATH`

Ceiling remains exactly bounded by the source research result. No promotion authority is created by replay.

## Verification
- Initial single-lane run exceeded the 150s control bound after 16 passing dots and was killed. This is incomplete evidence, not a failure verdict.
- Bounded batch 1: **12/12 PASS** in 45.18s.
- Bounded batch 2: **10/10 PASS** in 32.59s.
- Bounded batch 3: **8/8 PASS** in 20.18s.
- Aggregate re-earned surface: **30/30 PASS**.
- Frontier test committed Git-blob SHA-256: `490cfec475c878405482a454d39c6ac3d64db7fba2fd1d50e9191e7e676965c4`.
- Worktree SHA-256: `620c3af3b7970dffa5c271f2d0d2036af0fc56583236b6a2fce9686789f2c720` (non-authoritative normalization variant).
- Identity rule: `WORKTREE_HASH != GIT_BLOB_EVIDENCE_IDENTITY`; source and staged replay Git blobs match exactly.
- `microseed/` production delta: **none**.

## Exploratory selection context
A live Qwen3.5-35B-A3B speculative-decoding coprocessor ranked F_VALUE over E_IDENTITY at 0.78 confidence because F is less redundant with admitted B_DRIFT and offers a sharper falsifier. This is **provisional research-plane advice only** and carries no promotion authority.

## Decision
`KEEP_AS_REPLAYED_RESEARCH_EVIDENCE__DO_NOT_MOVE_MAIN`
