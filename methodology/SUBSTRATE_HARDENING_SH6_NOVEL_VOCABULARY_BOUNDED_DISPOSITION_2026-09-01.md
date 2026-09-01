# Substrate Hardening V1 — SH6 Novel Opaque Vocabulary Bounded Disposition

Status: BOUNDED DISPOSITION CANDIDATE / RESEARCH BRANCH ONLY / NO CANONICAL PRODUCTION DELTA

## Question
Can existing representation-growth owners derive a new opaque operational vocabulary without caller-supplied target/partition identity, semantic desired-state authority, or a new vocabulary manager?

## Result
Yes, boundedly, with an additional currentness repair. The archived WIP seed already showed that a second-stage opaque bucket projection can be discovered from owned projection-bucket samples and externally qualified before request specialization. The first admissibility run exposed two stale WIP-test expectations and one real mechanism seam.

## Observed mechanism seam
After `P-MS1986-A` drifted, derived projection `P-SH6-NOVEL` became non-current, but bound request capabilities specialized against `P-SH6-NOVEL` remained current. That was currentness laundering through a derived projection.

## Repair
`Microseed.change_epistemic_projection` now records transitive dependent projection ids before advancing the source projection, then stales capabilities, contrasts and deficits bound to those dependent projection epochs. Projection evidence still grants no execution authority.

## Ceiling
This is opaque operational vocabulary only. It is not semantic vocabulary, language admission, desired-state authority, truth authority, local-means ownership, or canonical promotion.

## Tests
- `tests/embodiment/test_hardening_sh6_endogenous_opaque_vocabulary_growth.py`: 3/3 PASS, 206.11s.
- `tests/embodiment/test_hardening_sh6_projection_bound_request_currentness_cascade.py`: 1/1 PASS, 4.20s.

## Release-gate posture
SH6 has a bounded disposition candidate after focused repair. It still needs breadth/finish reconciliation before the formal substrate-release gate can be updated.
