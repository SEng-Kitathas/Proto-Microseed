# V1-SOAK-001 Serialized on B/C Canon V1 — 2026-09-01

Status: **SERIALIZED ON CURRENT B/C CANON / NO PRODUCTION DELTA / EVIDENCE AND HARNESS ONLY / NOT NEW CANON**

## Current canon
- Label: `PRELINGUAL_SUBSTRATE_V1_P1A_N1A_BOUNDED_HIERARCHY_V1_MS_SUBSTRATE_HARDENING_V1_BC_NESTED_CURRENTNESS_V1`
- Tag: `prelingual-substrate-v1-p1a-n1a-bounded-hierarchy-v1-ms-substrate-hardening-v1-bc-nested-currentness-v1` -> `9e5df16ac60c0edaf8833b54e42d8e38d724fc4c`
- Microseed subtree: `4c8051563279d20f2ea555d21d7b3305b039e771`
- Base public main: `6c9c9a54de8269902438916ea00a81caed5e8913`

## Source branch
- Source: `origin/research/v1-developmental-soak-001` -> `3e95bb520307b5b2a0dc4d292655f0d9c3a76014`
- Merge-base with current main: `0fa41f1ed4cf2fbd341b5f0b63adbc0034d4ac39`
- Status: stale lineage; do not merge directly.

## Key correction
The old soak branch is **not** a missing production patch. Current main already contains the V1-SOAK-001 stale learned-relation rehearsal repair through MS2054 P1A:

- `c036ab5 MS2054 P1A: promote stale rehearsal currentness repair candidate`

This serialization imports the missing long-horizon methodology, 1200-episode result, artifact pointers, readiness JSON, long-horizon scratch harness, and smoke test onto current B/C canon.

## Imported files
- `methodology/V1_SOAK_001_NOVEL_WORLD_LONG_HORIZON_DEVELOPMENTAL_SOAK.md`
- `research_results/V1_SOAK_001_1200_EPISODE_RESULT.json`
- `research_results/V1_SOAK_001_ARTIFACT_POINTERS.md`
- `research_results/V1_SOAK_001_REPAIR_PROMOTION_READINESS.json`
- `scratch/v1_soak_001_novel_world_long_horizon.py`
- `tests/embodiment/test_v1_soak_001_smoke.py`

## Production delta
None. `microseed/` remains at `4c8051563279d20f2ea555d21d7b3305b039e771`.

## Verification
- Focused cleanup-neutral lane: **19/19 PASS**.
- Public verifier: **PASS**, issues empty.
- B/C promotion guard: **2/2 PASS**.
- Compileall: **PASS**.
- Direct unpatched precheck: 8 passed and 11 Windows SQLite tempdir cleanup failures; cleanup-neutral rerun passed 19/19.

## Decision
`SERIALIZATION_ONLY__NO_CANON_CHANGE__NO_PRODUCTION_CHANGE`.

## Next
Do not merge `origin/research/v1-developmental-soak-001` directly. Either run a bounded admission audit over this serialized long-horizon evidence, or select another frontier.
