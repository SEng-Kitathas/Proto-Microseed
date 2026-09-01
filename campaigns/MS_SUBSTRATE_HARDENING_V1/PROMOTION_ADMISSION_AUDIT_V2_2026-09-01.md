# MS Substrate Hardening V1 — Promotion Admission Audit V2

Status: **ADMISSION AUDIT PASS / CONTROLLED PROMOTION REVIEW ADMISSIBLE / DIGEST SCHEMA REPAIRED / CANONICAL PROMOTION NOT PERFORMED**

## Why V2 exists
Opus independently verified the promotion-admission audit and found one real regression: the V1 audit artifact digests I reported were Windows working-tree CRLF hashes, not committed Git blob hashes. This repeats the MS2065 class: `FIX_APPLIED_AT_SITE != FIX_APPLIED_TO_PATTERN`.

## Digest rule repaired
Receipt artifact digests in this lineage must state and use this normalization form:

`sha256(git committed blob bytes read as REF:path)`

not local working-tree checkout bytes. A helper was added:

`tools/receipt_blob_digest.py`

## Corrected V1 artifact digests
| Artifact | Correct Git blob SHA-256 | Previous CRLF working-tree SHA-256 |
|---|---:|---:|
| `PROMOTION_ADMISSION_AUDIT_V1_2026-09-01.json` | `69e29755daf232119e7083215f0d19871444085f5a8a555a86cd688c730fca53` | `897d3066f5af36a22f25cb7b22cb3a959fa8caf6f8b1cef19d8c7fccbf49be19` |
| `PROMOTION_ADMISSION_AUDIT_V1_2026-09-01.md` | `e362727ecf59d071ba6081ae365b0b4e7f3328ebe773b4cc57090a0774ed4684` | `68a73437036f3ed67ed3d5af0831ad610edb58c40321119b31518fbf6a192a59` |

## What the 24-line production delta does
Changed production file: `microseed/runtime/entity.py`.

Owner: `Microseed.change_epistemic_projection`.

Semantic claim: when a source epistemic projection changes, Microseed now records currently dependent derived projections before advancing the source epoch, then stales capability specializations, contrast bindings, and epistemic deficits bound to those dependent projection epochs. This prevents projection-derived request atoms from remaining current after their source projection ancestry drifts.

Mechanism: transitive dependent-projection collection over current `EpistemicProjectionRecord.dependency_projection_epochs` or `source_projection_epochs`, followed by dependent stale propagation and explicit packet readback through `stale_projection_ids`.

## Earned properties
1. Dependent derived projections are discovered before the source projection epoch advances.
2. The old source epoch/signature remains available for dependency matching.
3. The collection is transitive over current dependent projections.
4. Direct source-bound capabilities still stale through the existing owner.
5. Derived-projection-bound capabilities now stale on source drift.
6. Dependent projection contrast bindings now invalidate.
7. Dependent projection premise deficits now stale with dependency-qualified reasons.
8. The repair composes with existing projection dependency fields and adds no new representation/currentness manager.

## Ceilings
1. No semantic projection authority.
2. No raw projection discovery authority.
3. No truth authority.
4. No execution authority.
5. No language/reference authority.
6. No durable vocabulary registry authority.
7. No arbitrary desired-state authority.
8. No selfhood/numerical identity/exclusive successor authority.
9. No canonical promotion or substrate-freeze declaration.

## Promotion decision
The V1 admission decision remains: `ADMISSIBLE_TO_CONTROLLED_PROMOTION_REVIEW`.

The promotion decision remains: `CANONICAL_PROMOTION_NOT_PERFORMED`.
