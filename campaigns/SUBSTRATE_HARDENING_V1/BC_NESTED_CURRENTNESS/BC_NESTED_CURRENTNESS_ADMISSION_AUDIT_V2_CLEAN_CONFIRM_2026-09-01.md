# B/C Nested Currentness Admission Audit V2 — Clean Confirmation — 2026-09-01

Status: **ADMISSION AUDIT PASS / CLEAN CAPTURED WHOLE-SUITE CONFIRMATION / CONTROLLED PROMOTION REVIEW ADMISSIBLE / NOT CANON / NOT PROMOTED**

## Why V2 exists
V1 had a whole-suite evidence caveat: stdout was green, but the execution wrapper ended `FAILED/SUPERVISION_LOST`. V2 reruns the whole suite through a captured-output cleanup-neutral harness so the test output is written to committed evidence files and validated by a compact follow-up verifier.

## Current canon baseline
- Canon: `PRELINGUAL_SUBSTRATE_V1_P1A_N1A_BOUNDED_HIERARCHY_V1_MS_SUBSTRATE_HARDENING_V1`
- Tag: `prelingual-substrate-v1-p1a-n1a-bounded-hierarchy-v1-ms-substrate-hardening-v1` -> `0f6cf0b3d660c8a4bb9561a65d7f1fd95e1b99f7`
- Canon Microseed subtree: `88f5a058cc5a4e92b1006c36d31b95cf727d197f`
- Public main: `28489c6feaa9d1d777b8bca0cca2ec3e35042144`

## Candidate
- Branch: `research/hardening-bc-admission-audit-v2`
- V1 audit head: `f205c2fc4fce1d56d870b8ec05c575f2cd63a891`
- Candidate Microseed subtree: `4c8051563279d20f2ea555d21d7b3305b039e771`
- Production delta from current canon: `microseed/development/rehearsal.py`, `microseed/runtime/entity.py`
- Shortstat: `2 files changed, 151 insertions(+), 3 deletions(-)`

## Clean rerun
Whole-suite cleanup-neutral captured rerun:
- Result: **1015 passed, 1 deselected**
- Pytest return code: `0`
- Elapsed: `1215.519` seconds
- Stderr bytes: `0`
- Stdout SHA-256: `79f42242cbd9696da223d66f9d7d54a509d09109f76c09a9cd1ee4cc2dd29276`
- Stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The original long tool call timed out at the tool surface, but the server-side process continued to completion and wrote a complete summary. A separate compact validator returned PASS with issues empty, verifying return code, hashes, empty stderr, and the expected green pytest summary. This supersedes the V1 `SUPERVISION_LOST` caveat while preserving the new transport note as `TIMEOUT_ERROR_AT_TOOL_CALL_SURFACE__SERVER_PROCESS_CONTINUED_TO_COMPLETION`.

## Additional confirmation
- Compileall: PASS for `microseed` and `tests/embodiment`.
- Public verifier: PASS, issues empty.
- Current-canon identity guard: expected failure remains explicit because candidate subtree `4c8051563279d20f2ea555d21d7b3305b039e771` differs from canon `88f5a058cc5a4e92b1006c36d31b95cf727d197f`.

## Decision
`ADMISSIBLE_TO_CONTROLLED_PROMOTION_REVIEW_WITH_CLEAN_CAPTURED_WHOLE_SUITE_CONFIRMATION`.

## Non-decision
`NOT_CANON` and `NOT_PROMOTED`.

## Ceilings
- No semantic/reference/language/truth/execution/selfhood authority.
- No durable global currentness manager.
- No automatic admission from cherry-pick auto-merge.
- Current-canon guard failure is not laundered.
