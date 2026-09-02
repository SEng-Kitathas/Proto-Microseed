# B/C Nested Currentness Admission Audit V1 — 2026-09-01

Status: **ADMISSION AUDIT PASS WITH SUPERVISION-LOST CAVEAT / CONTROLLED PROMOTION REVIEW ADMISSIBLE / NOT CANON / NOT PROMOTED**

## Candidate
- Branch: `research/hardening-bc-admission-audit-v1`
- Serialized base branch: `research/hardening-bc-nested-currentness-rebased-on-hardening-canon-v1`
- Serialized base head: `2df02b159edde474e4d21f8ca9748e3e0058a96d`
- Audit base head before this artifact commit: `2df02b159edde474e4d21f8ca9748e3e0058a96d`
- Candidate Microseed subtree: `4c8051563279d20f2ea555d21d7b3305b039e771`

## Current canon baseline
- Canon: `PRELINGUAL_SUBSTRATE_V1_P1A_N1A_BOUNDED_HIERARCHY_V1_MS_SUBSTRATE_HARDENING_V1`
- Tag: `prelingual-substrate-v1-p1a-n1a-bounded-hierarchy-v1-ms-substrate-hardening-v1` -> `0f6cf0b3d660c8a4bb9561a65d7f1fd95e1b99f7`
- Canon Microseed subtree: `88f5a058cc5a4e92b1006c36d31b95cf727d197f`
- Public main: `28489c6feaa9d1d777b8bca0cca2ec3e35042144`

## Production delta from current canon
- `microseed/development/rehearsal.py`
- `microseed/runtime/entity.py`

Shortstat: `2 files changed, 151 insertions(+), 3 deletions(-)`

## Verification
- Adjacent cleanup-neutral lane: **76/76 PASS** in 532.35s, `PYTEST_RC=0`.
- Full functional whole-suite cleanup-neutral lane with current-canon identity guard deselected: stdout reports **1015 passed, 1 deselected** in 1207.66s and `PYTEST_RC=0`.
- Whole-suite wrapper caveat: server execution status is `FAILED` with `failure_kind=SUPERVISION_LOST` and no stderr, despite complete green pytest stdout. This is preserved as a supervision/transport caveat, not hidden.
- Compileall: PASS for `microseed` and `tests/embodiment`.
- Public verifier: PASS, issues empty; continuity check only.
- Current-canon identity guard: **1 failed, 1 passed as expected** because B/C `HEAD:microseed = 4c8051563279d20f2ea555d21d7b3305b039e771` differs from current canon `88f5a058cc5a4e92b1006c36d31b95cf727d197f`.

## Interaction audit
Hardening V1 owner: `Microseed.change_epistemic_projection` stales projection-bound artifacts across transitive dependent projection ancestry when a source projection changes.

B/C owner: routed rehearsal and projection-conditioned binding currentness over exact `projection_routing_id`, `projection_bucket_id`, routed relation, and post-binding outcome evidence.

Composition claim: B/C preserves exact route/bucket ancestry at rehearsal proposal creation and revalidates routed descendants at use time; hardening V1 separately stales projection-bound artifacts when source projection ancestry drifts. These mechanisms compose at the tested surfaces without granting a global currentness manager.

## Decision
`ADMISSIBLE_TO_CONTROLLED_PROMOTION_REVIEW_WITH_SUPERVISION_LOST_CAVEAT`.

## Non-decision
`NOT_CANON` and `NOT_PROMOTED`.

## Ceilings
- Full-suite evidence carries explicit `SUPERVISION_LOST` wrapper caveat.
- No semantic/reference/language/truth/execution/selfhood authority.
- No durable global currentness manager.
- No automatic admission from cherry-pick auto-merge.
- No current-canon guard laundering.
