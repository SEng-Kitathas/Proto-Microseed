# RAHL R3.1 — Project-Local Verifier Portability Amendment

Date: 2026-08-29 ET
Status: ACTIVE PROJECT-LOCAL SCAR / DOES NOT PROMOTE R3.1 REPLACEMENT AUTHORITY

## Subject
RAHL R3.1 source candidate ZIP SHA-256:
`4d205becc2413889bdb37c6b6ff7513d6f759a7dff1d9f9b8fddaddd8235a278`.

R3.1 remains active project-local shadow-use doctrine only. Source candidate still says `replacement_ready=false`; foundation promotion remains false.

## New active scars
`HOST_NATIVE_PATH_STRING != CANONICAL_PACKAGE_MEMBER_IDENTITY`

`NONZERO_EXIT != EXPECTED_MUTATION_DETECTION`

`HOSTILE_REJECTION_AT_UNRELATED_GATE != TARGET_GUARD_EXERCISED`

`CANONICAL_PACKAGE_MEMBER_IDENTITY_REQUIRES_PLATFORM_NEUTRAL_PATH_NORMALIZATION`

## Operational rule
For package verifiers, manifests, ZIP entries, frozen bindings and hostile resealing:
- package member identity SHALL use one explicit platform-neutral canonical form;
- host filesystem display/path separators SHALL NOT be treated as package member identity;
- a verifier mutation that changes its own bytes requires a separately identified/resealed test specimen before integrity conclusions are drawn;
- hostile mutation success SHALL NOT be counted from nonzero exit alone when the intended guard is knowable;
- inspect and retain the actual rejection reason/gate;
- rejection at an earlier unrelated integrity gate is a nonresult for the deeper semantic guard under test.

## Evidence
Original Windows verifier falsely reported package membership drift due slash/backslash mismatch.
A partial verifier-only patch caused the hostile resealer to generate noncanonical manifest keys, making 19/19 exits vacuous at membership.
A fresh temporary specimen canonicalized both verifier enumeration and hostile resealing with `.as_posix()`, recomputed the temporary manifest, then produced:
- base verifier PASS / rc=0;
- 19/19 hostiles rejected through meaningful source-class/body, live-section, frozen semantic binding, scar, ancestry, membership and authority-effect guards.

Full evidence:
`notes/maintenance/RAHL_R3_1_WINDOWS_VERIFIER_PORTABILITY_AND_HOSTILE_REPLAY_2026-08-29.md`
SHA `d9cb4fe4589fd9fbad8dd7918432f5825568e208e321a168772f1efc504f4680`.

## Nonclaims
- Original ZIP was not repaired or resealed.
- This amendment does not make R3.1 universal replacement-ready.
- Temporary patched specimen hashes are verification evidence only, not a new RAHL release.
- 19/19 hostile rejection remains bounded to the declared mutation family and verifier assurance ceiling.