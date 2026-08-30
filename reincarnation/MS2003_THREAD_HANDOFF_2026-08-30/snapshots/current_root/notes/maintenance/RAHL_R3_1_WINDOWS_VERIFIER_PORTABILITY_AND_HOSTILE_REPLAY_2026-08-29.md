# RAHL R3.1 Windows Verifier Portability + Hostile Replay — 2026-08-29

## Subject
Original server-side archive:
`C:\Users\ancal\Downloads\RAHL_ENGINEERING_IN_HOUSE_SOP_SPLIT_CANDIDATE_R3_1_2026-08-29.zip`

Original ZIP SHA-256:
`4d205becc2413889bdb37c6b6ff7513d6f759a7dff1d9f9b8fddaddd8235a278`

Original archive was not mutated.

## Original verifier result on Windows
Running the package's original `VERIFY_CANDIDATE.py` after clean extraction returned rc=1 with package-membership drift.

Root cause:
`verify_membership_integrity()` formed actual relative paths with:
`str(path.relative_to(R))`
while `EXPECTED_FILES` and manifest keys use canonical `/` separators.

On Windows, actual paths therefore used backslashes and could not equal the canonical manifest/member identifiers.

Scar:
`HOST_NATIVE_PATH_STRING != CANONICAL_PACKAGE_MEMBER_IDENTITY`.

This is a portability defect in the verifier, not evidence of package-member absence.

## First portability replay warning
A temporary extracted verifier was changed only from:
`str(path.relative_to(R))`
to:
`path.relative_to(R).as_posix()`.

The base specimen then correctly rejected itself at `manifest hash drift: VERIFY_CANDIDATE.py` because the verifier byte identity had changed without resealing. This is expected integrity behavior.

Running the existing hostile harness against that partially patched specimen misleadingly produced 19/19 nonzero exits, but most cases failed at `manifest membership drift` because the hostile harness `reseal()` itself used Windows-native `str(p.relative_to(root))` keys.

That result was explicitly NOT counted as semantic hostile coverage.

Scars:
- `NONZERO_EXIT != EXPECTED_MUTATION_DETECTION`;
- `HOSTILE_REJECTION_AT_UNRELATED_GATE != TARGET_GUARD_EXERCISED`;
- `VERIFIER_PORTABILITY_FIX != HOSTILE_RESEAL_PORTABILITY_FIX`.

## Controlled temporary portability repair
A fresh temporary extraction was modified only for Windows-canonical package identities:
1. verifier actual member ids: `path.relative_to(R).as_posix()`;
2. hostile reseal member ids: `p.relative_to(root).as_posix()`;
3. temporary specimen manifest recomputed to bind the two temporary portability edits.

Temporary verifier SHA-256:
`91b5cd75b9e2ed1f049384eafee67d20711220f9bb8d7f0ffe435ec45d1fb77e`

Temporary hostile harness SHA-256:
`baa5c39ffcec599b9033a2018386a99c043b6c4be6f5b8728a1b1ba9016d4ee7`

Temporary manifest SHA-256:
`e74cbb53a6d5bac0c3060c1a128c0cc72b7b8d47bb25311890ae69ffea75fb04`

These hashes identify a transient verification specimen only; they do not replace the source archive.

## Replayed base verification
Temporary portability-corrected specimen:
- rc=0;
- exact membership PASS;
- pinned ancestry PASS;
- source class+body binding PASS;
- exact live human-section binding PASS;
- governance boundary PASS;
- active scar binding PASS;
- execution/release recovery PASS;
- coverage blockers PASS;
- dormant substrate schema PASS.

Assurance ceiling remains:
`STRUCTURE_SOURCE_CLASS_BODY_COVERAGE_AND_INTEGRITY_ONLY`.

## Replayed hostile verification
19/19 mutations rejected, now after canonical resealing rather than path-format failure.

Observed target guard classes included:
- `engineering source class drift: C09`;
- `human engineering section drift: C16`;
- relocated expected C16 text still rejected at the live C16 section;
- `engineering source body drift: C16`;
- frozen `candidate semantic binding drift` for governance/project/substrate/cold-start/authority/execution/machinery surfaces;
- `active scar set drift`;
- `pinned ancestry drift`;
- undeclared member rejected by exact package-membership check;
- `human engineering section drift: C01`;
- `engineering authority effect drift: C01`.

Therefore the earlier Windows-local 19/19 nonzero result was vacuous, but the canonicalized/resealed replay does support that the declared hostile mutations reach meaningful integrity/semantic binding guards.

## Authority / adoption consequence
R3.1 remains:
- ACTIVE project-local shadow-use doctrine;
- universal replacement unclaimed;
- `replacement_ready=false` in the source candidate;
- foundation promotion false;
- compression inherits no new authority.

The new project-local verifier scar is:
`CANONICAL_PACKAGE_MEMBER_IDENTITY_REQUIRES_PLATFORM_NEUTRAL_PATH_NORMALIZATION`.

If a future R3.2/R4 package is produced, both verifier member enumeration and hostile resealing should canonicalize package member identities explicitly and hostile cases should preserve/read back the expected rejection reason, not merely assert nonzero exit.