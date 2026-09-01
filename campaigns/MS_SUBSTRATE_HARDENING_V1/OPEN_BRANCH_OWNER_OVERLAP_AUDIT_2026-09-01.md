# Open Branch Owner-Overlap Audit - 2026-09-01

Status: AUDIT COMPLETE / NO MUTATION / NO CANONICAL PROMOTION

Scope: remote branches origin/research/frontier-a..k and origin/research/hardening-* as visible after V2 audit branch push.
Origin main: `3ec008b9f1f44c3871c28aee19d823ff68680cc7`.
Branches audited: 22 (11 frontier, 11 hardening).

Finding: `INDEPENDENT_PRODUCTION_OWNER_OVERLAP_PRESENT__BC_REPAIR_AND_RELEASE_GATE_FINISH_BOTH_TOUCH_MICROSEED_RUNTIME_ENTITY_PY__SERIALIZE_OR_REBASE_BEFORE_PROMOTION`.

## Exact production file overlaps
- `microseed/runtime/entity.py` raw touched by: `research/hardening-bc-nested-currentness-v1`, `research/hardening-release-gate-admission-audit-v1`, `research/hardening-release-gate-admission-audit-v2`, `research/hardening-release-gate-finish-v1`

## Independent production file overlap pairs
- `microseed/runtime/entity.py` independent pairs: `research/hardening-bc-nested-currentness-v1` <> `research/hardening-release-gate-admission-audit-v1`; `research/hardening-bc-nested-currentness-v1` <> `research/hardening-release-gate-admission-audit-v2`; `research/hardening-bc-nested-currentness-v1` <> `research/hardening-release-gate-finish-v1`

## Lineage-carry production file overlap pairs
- `microseed/runtime/entity.py` lineage pairs: `research/hardening-release-gate-admission-audit-v1` -> `research/hardening-release-gate-admission-audit-v2`; `research/hardening-release-gate-admission-audit-v1` -> `research/hardening-release-gate-finish-v1`; `research/hardening-release-gate-admission-audit-v2` -> `research/hardening-release-gate-finish-v1`

## Branch production deltas
- `research/frontier-a-target-v1` @ `38779470`: production files 0; none
- `research/frontier-b-drift-v1` @ `c9c6f047`: production files 0; none
- `research/frontier-c-scale-v1` @ `e6a313fc`: production files 0; none
- `research/frontier-d-cfe-v1` @ `0b59687d`: production files 0; none
- `research/frontier-e-identity-v1` @ `edc0f27a`: production files 0; none
- `research/frontier-f-value-v1` @ `45e0e45f`: production files 0; none
- `research/frontier-g-naked-v1` @ `e41287c0`: production files 0; none
- `research/frontier-h-language-v1` @ `b453df21`: production files 0; none
- `research/frontier-i-growth-v1` @ `56ed04a8`: production files 0; none
- `research/frontier-j-convergence-v1` @ `8f246a5f`: production files 0; none
- `research/frontier-k-red-team-v1` @ `48f6ff17`: production files 0; none
- `research/hardening-a-target-vocabulary-v1` @ `cdee37b8`: production files 0; none
- `research/hardening-bc-nested-currentness-baseline-repro` @ `f944b0b9`: production files 0; none
- `research/hardening-bc-nested-currentness-v1` @ `4188e40d`: production files 2; `microseed/development/rehearsal.py`, `microseed/runtime/entity.py`
- `research/hardening-d-terrain-provenance-v1` @ `adeb08e4`: production files 0; none
- `research/hardening-h-coreference-query-local-candidate-v1` @ `d2a68f42`: production files 0; none
- `research/hardening-h-coreference-v1` @ `d542d78f`: production files 0; none
- `research/hardening-i-operational-equivalence-v1` @ `2db5d7ec`: production files 0; none
- `research/hardening-release-gate-admission-audit-v1` @ `6d1a57de`: production files 1; `microseed/runtime/entity.py`
- `research/hardening-release-gate-admission-audit-v2` @ `361d1075`: production files 1; `microseed/runtime/entity.py`
- `research/hardening-release-gate-finish-v1` @ `1c42da8e`: production files 1; `microseed/runtime/entity.py`
- `research/hardening-sh6-vocabulary-wip-archive-2026-09-01` @ `03adc395`: production files 0; none

## Interpretation
The frontier-a..k branches have no production-file deltas in this audit. The relevant independent production-owner collision is between the quarantined B/C nested-currentness repair branch and the hardening release-gate finish/admission line on `microseed/runtime/entity.py`. Promotion should serialize or rebase that owner before merging/promoting either line.

## Caveat
Diffs are branch-local from each branch merge-base with origin/main. Lineage-carry overlaps are separated from independent overlaps, but semantic merge safety still requires exact owner inspection.
