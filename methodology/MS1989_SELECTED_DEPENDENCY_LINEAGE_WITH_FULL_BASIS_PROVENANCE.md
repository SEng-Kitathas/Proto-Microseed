# MS1989 — Selected Dependency Lineage with Full-Basis Provenance

Date: 2026-08-29 ET
Status: VERIFIED / ready for local seal and research-branch publication
Parent: published MS1988 `c734c366fa22a313f7eb4c07eac83a17e513bcfc`

## Question
MS1988 proved bounded recursive projection composition one level deeper, but every composed projection still carried the entire source vector as its currentness dependency.

If C is discovered from an A/B/D/F bucket vector but its learned candidate uses only positions A+B, should later change to unused F make C stale?

Prewrites:
- `FULL_EVALUATION_BASIS != SELECTED_DEPENDENCY_SET`;
- `FALSE_STALENESS != FALSE_CURRENTNESS`;
- removing false staleness must not weaken fail-closed currentness for actually selected sources;
- full discovery basis provenance must remain exact and inspectable.

## Sealed-MS1988 boundary
A detached worktree at exact sealed MS1988 `c734c366fa22a313f7eb4c07eac83a17e513bcfc` reproduced the currentness behavior directly in `EpistemicProjectionRegistry`.

C was registered with full basis:
`A, B, D, F`.

Before changing F:
- C current flag: `True`;
- `is_current(C)`: `True`.

After changing F:
- C current flag: `False`;
- `is_current(C)`: `False`.

For the MS1988/MS1989 process, C's selected `input_positions` are `(0,1)`, meaning A+B. D/F are search/evaluation basis coordinates but are not used by C's predictive partition.

Therefore the sealed behavior demonstrates a real **false-staleness** cost: an unselected source definition can invalidate a projection that does not operationally depend on it.

This is safe but overly conservative. It does not create false currentness, but it widens invalidation unnecessarily as recursive source vectors grow.

## Smallest lawful split
MS1989 keeps two distinct lineage surfaces.

### Full basis provenance
`source_projection_epochs`

This remains the exact ordered current source vector used to produce the generated projection samples and discover the candidate.

It remains required and checked at admission time. Every full-basis source must be exact and current when the projection is admitted.

### Selected operational dependencies
`dependency_projection_epochs`

This is derived from:
- the already bound full source basis; and
- the candidate's already bound `input_positions`.

The caller does not nominate this set independently.

For C over A/B/D/F with positions `(0,1)`:
- full basis = A/B/D/F;
- selected dependency set = A/B.

After admission, projection currentness, transitive invalidation, recursive currentness checks, and recursive projection evaluation follow selected dependencies when present.

Legacy records with no selected dependency lineage continue to use the full source basis conservatively.

## Why dependency lineage is derived rather than separately trusted
The selected dependency set is a deterministic consequence of two fields already included in candidate identity:
- `source_projection_epochs`;
- `input_positions`.

MS1989 therefore does not add selected dependency lineage as a second independent candidate identity input.

`EpistemicProjectionCandidate.__post_init__` derives it from basis+positions. If serialized input explicitly supplies a dependency set, it must exactly match the derived set or construction fails.

This preserves old source-based candidate identity.

### Exact identity compatibility witness
A deterministic synthetic source-basis candidate was run under:
1. sealed MS1988 in a detached worktree; and
2. the MS1989 candidate tree.

Both produced exactly:
- candidate ID: `proj-cand-659ab3b00df7224f5100`;
- candidate digest: `6c19bb59464942b716d607e65d4c1f838076056519de9407521f756338632d21`.

MS1988 has no selected dependency field; MS1989 derives A+B. Candidate identity remains unchanged because the dependency set is already implied by signed basis+positions.

## Process embodiment
Scratch:
`scratch/ms1989_selected_dependency_lineage_boundary.py`

Uses the MS1988 eight-bit process world and learns C from an automatically generated A/B/D/F source vector.

Observed candidate:
- full basis: `P-MS1989-A`, `P-MS1989-B`, `P-MS1989-D`, `P-MS1989-F`;
- input positions: `(0,1)`;
- selected dependencies: `P-MS1989-A`, `P-MS1989-B`.

### Unused-source hostile
Change F after C admission.

Required:
- C stays current;
- recursive evaluation can still evaluate C from selected A+B;
- stale/missing old F candidate content must not be needed to evaluate C.

Observed: PASS.

### Selected-source hostile
Change A after C admission.

Required:
- C becomes stale;
- `is_current(C)` fails closed.

Observed: PASS.

## Admission safety
Full basis still controls admission validity.

A test explicitly makes an unselected basis source stale before registering C. Registration fails with:
`EPISTEMIC_SOURCE_PROJECTION_NOT_CURRENT`.

This preserves the distinction:
- **formation provenance** requires the full basis to have been valid when the candidate was earned;
- **future operational currentness** depends only on the inputs the admitted candidate actually uses.

## Legacy behavior
For projection records with:
- nonempty `source_projection_epochs`; and
- empty `dependency_projection_epochs`;

currentness continues to follow the full source basis.

No existing sealed record is silently reinterpreted as having narrower dependencies.

## Core changes
### `microseed/development/projection_discovery.py`
- candidate carries derived `dependency_projection_epochs`;
- selected dependencies are determined only by source-basis positions selected by the learned candidate;
- explicitly supplied dependency lineage must match that derivation;
- candidate ID/digest remains legacy-compatible because dependency is not a second identity input;
- candidate deserialization re-derives dependency when older packets omit it.

### `microseed/development/epistemic.py`
- admitted projection record can persist selected dependency lineage separately from full basis provenance;
- registration still validates full basis;
- currentness/invalidation/change/reactivation follow selected dependencies when present;
- legacy empty dependency lineage falls back to full-basis currentness.

### `microseed/runtime/entity.py`
- admission copies candidate selected dependency lineage into the projection record;
- recursive composed-projection evaluation verifies exact full-basis provenance but recursively evaluates only selected dependencies when the selected lineage exists;
- legacy composed projections retain old full-basis evaluation behavior.

## Earned candidate statement
`SELECTED_SOURCE_DEPENDENCY_LINEAGE_CAN_GOVERN_CURRENTNESS_AND_RECURSIVE_EVALUATION_WHILE_FULL_SOURCE_BASIS_REMAINS_EXACT_PROVENANCE`

## What this does not earn
- semantic feature identity;
- semantic dependency identity;
- causal ontology;
- autonomous source-family selection;
- truth authority;
- language authority.

The selected dependencies are operational coordinates selected by predictive search. They are not semantic causes.

## Verification so far
Initial cleanup-neutral focused MS1986–MS1989 regression:
- job `job-7457922cdee6`;
- **15/15 PASS in 199.67s**;
- stderr empty.

The tightened cleanup-neutral focused MS1986–MS1989 regression, including exact candidate-identity compatibility:
- job `job-65a991fc8b11`;
- **16/16 PASS in 188.78s**;
- stderr empty.

Additional gates:
- self-test: **81/81 PASS**;
- compileall: PASS.

## Final verification
- sealed-MS1988 false-staleness boundary: PASS; changing unused F makes C stale under MS1988;
- exact source-based candidate identity compatibility with MS1988: PASS;
- cleanup-neutral focused MS1986–MS1989: `job-65a991fc8b11` -> **16/16 PASS in 188.78s**;
- whole cleanup-neutral embodiment suite: `job-e0d362e00fab` -> **784/784 PASS in 501.40s**;
- whole-suite stderr: empty;
- Microseed self-test: **81/81 PASS**;
- compileall: PASS;
- `git diff --check`: required once more after this documentation-only finalization.

## Seal/publication gate
The mechanism/test tree passed all behavioral gates. This final edit only records those results. After one final diff/readback check, the pass is eligible for:
1. exact local Git seal;
2. push to `origin/research/ms1888-replay`;
3. independent remote ref readback matching the sealed SHA.
