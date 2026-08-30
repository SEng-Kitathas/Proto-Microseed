# MS1967–MS1970 / RAHL R3.1 Reference-Boundary Checkpoint — 2026-08-29

## Authority / lineage
- Canonical Main-Dev remains MS1527.
- Research baseline remains MS1887.
- Published GitHub research remains MS1947 `673db9978f48151ef862954a177f519683e900f2`.
- GitHub main remains MS1939 `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`.
- Current sealed LOCAL research: MS1970 `ac2a215c23e055f0f3ac6b4a5bbec0af50c4d32e`.
- Tree: `393910e23e66d40df451c9bd00c00f2d1f84fb9a`.
- Source/test snapshot: `affb9ba180537125bf8dab3f2cf4a3a609da9fa328bdb9bdc7286d4d384d6055` across 299 Python files.
- Worktree clean.
- No `microseed/` delta from MS1961 `c92d2eae21823ff695457d0ca7205c5db431f5aa` through MS1970.
- MS1948–MS1970 unpublished.
- Novelty remains `UNKNOWN / NOT_ENTITLED_TO_CLAIM`.

## RAHL R3.1 adoption status
Source ZIP SHA-256:
`4d205becc2413889bdb37c6b6ff7513d6f759a7dff1d9f9b8fddaddd8235a278`.

R3.1 remains ACTIVE PROJECT-LOCAL SHADOW USE / NOT UNIVERSAL REPLACEMENT.
Source nonclaims retained:
- replacement_ready=false;
- foundation promotion false;
- compression inherits no new authority;
- assurance ceiling `STRUCTURE_SOURCE_CLASS_BODY_COVERAGE_AND_INTEGRITY_ONLY`.

Existing fresh-project adjudication at MS1957 remains valid:
`R3_1_PRESERVES_R6_LAWFUL_DECISION_ON_MS1957_WITH_LOWER_AUTHORITY_LOOKUP_AND_RECOVERY_BURDEN`.

### New Windows verifier scar
Original Windows verifier falsely reported package membership drift because host-native `str(relative_path)` backslashes were compared with canonical `/` manifest/member ids.

A first partial portability replay also showed that hostile 19/19 nonzero exits could be vacuous when hostile resealing used the same noncanonical Windows member strings.

The result was NOT counted as semantic hostile coverage.

Controlled temporary replay canonicalized both verifier and hostile reseal paths using `.as_posix()`, recomputed only the temporary specimen manifest, then reran:
- base verifier: PASS / rc=0;
- hostile mutations: 19/19 rejected through meaningful target guards including source-class drift, live-section drift, source-body drift, frozen semantic binding, scar drift, ancestry drift, membership drift, and authority-effect drift.

Maintenance evidence:
`notes/maintenance/RAHL_R3_1_WINDOWS_VERIFIER_PORTABILITY_AND_HOSTILE_REPLAY_2026-08-29.md`
SHA `d9cb4fe4589fd9fbad8dd7918432f5825568e208e321a168772f1efc504f4680`.

New scars:
- `HOST_NATIVE_PATH_STRING != CANONICAL_PACKAGE_MEMBER_IDENTITY`;
- `NONZERO_EXIT != EXPECTED_MUTATION_DETECTION`;
- `HOSTILE_REJECTION_AT_UNRELATED_GATE != TARGET_GUARD_EXERCISED`;
- `CANONICAL_PACKAGE_MEMBER_IDENTITY_REQUIRES_PLATFORM_NEUTRAL_PATH_NORMALIZATION`.

Original ZIP remained untouched.

## MS1967 — calibrated observation-frame currentness
Existing `OperationalFrameRegistry` proved sufficient for calibration lifecycle/currentness.

Low-noise passive calibration:
- observed bound 3.0;
- current frame recovers `(0,1),(2,3)`.

Sensor-regime subject drift:
- old frame is staled before referent nomination;
- old attempt returns UNKNOWN / `CALIBRATION_FRAME_NOT_CURRENT_FOR_SENSOR_REGIME`;
- epoch increments and qualification/currentness become STALE.

Fresh high-noise qualification:
- new content-bound frame artifact;
- observed bound 15.0;
- frame current but referent partition fragments `(0),(1),(2,3)`.

Earned:
`EXISTING_OPERATIONAL_FRAME_CURRENTNESS_CAN_OWN_BOUNDED_CALIBRATION_LIFECYCLE_WHEN_EXTERNAL_SENSOR_REGIME_COMPATIBILITY_IS_EXPLICIT`.

Important new boundary:
`CURRENT_CALIBRATION != SUFFICIENT_ROBUST_OBSERVATION_FRAME`.

Durable job `job-d60e3498790a`: PASS.
Seal `cc32c0064b708a2d5a1f474b13e4bc154a38cdb7`.

## MS1968 — noisy calibrated sensor handoff
OLD, OVERLAP and NEW sensor layouts each received their own passive calibration/current OperationalFrame.

At handoff:
- CAL-OLD staled before overlap;
- CAL-OVERLAP staled before new;
- CAL-NEW current at end.

Despite distinct frame identities/currentness windows, the same two affordance-relative signatures bridge old -> overlap -> new under bounded jitter.

Earned:
`SEPARATELY_CURRENT_CALIBRATED_SENSOR_FRAMES_CAN_SUPPORT_OPERATIONAL_PROTO_REFERENT_CONTINUITY_ACROSS_NOISY_LAYOUT_HANDOFF_WITHOUT_SHARED_FRAME_IDENTITY`.

Continuity ceiling: `OPERATIONAL_REFERENT_CONTINUITY_ONLY`.
No numerical/semantic/language authority.

Durable job `job-0187bf09a79b`: PASS.
Seal `42fc1bfc5f81687262a4cce3481b365e617d1bc1`.

## MS1969 — disappearance/reappearance
Adversarial twin worlds:
1. evaluator individuals persist through an unobserved gap;
2. evaluator individuals are silently replaced by same-affordance successors during the gap.

Operational pre/post observations, partitions and affordance signatures are exactly identical in both worlds.

Earned:
`AFFORDANCE_SIGNATURE_REAPPEARANCE_SUPPORTS_OPERATIONAL_REASSOCIATION_BUT_CANNOT_ESTABLISH_INDIVIDUAL_PERSISTENCE_ACROSS_UNOBSERVED_SUBSTITUTION`.

Ceiling:
- reassociation `AFFORDANCE_RELATIVE_ONLY`;
- individual persistence NONE;
- numerical identity NONE;
- semantic reference NONE;
- language NONE.

Durable job `job-4a1472ccef91`: `BOUNDARY_CONFIRMED`.
Seal `02d9e88fdea3ad47882e2369c6d72c28bbfe587f`.

## MS1970 — one-to-many decomposition vs genealogy
Initial parent-only world was a valid nonresult because global synchrony returned UNKNOWN rather than inventing a single referent.
World was strengthened with an unrelated background referent so the target parent was genuinely distinguishable.
A second harness nonresult from repeated action positions was corrected without changing the scientific discriminator.

Final parent target responds to FX-L and FX-R. Two current descendants separately respond to FX-L vs FX-R. Their per-action response-tuple OR exactly reconstructs the parent response.

Adversarial twin variants:
1. evaluator genuine parent split;
2. hidden replacement by two new same-affordance descendants.

All operational parent/child groups, signatures, response rows, and decomposition are identical across variants.

Earned:
`PARENT_AFFORDANCE_CAN_DECOMPOSE_INTO_MULTIPLE_CURRENT_CHILD_AFFORDANCES_WITHOUT_ESTABLISHING_GENEALOGICAL_SPLIT_OR_IDENTITY_INHERITANCE`.

Ceiling:
- affordance decomposition `OPERATIONAL_RELATION_ONLY`;
- genealogy NONE;
- numerical identity inheritance NONE;
- semantic reference NONE;
- language NONE.

Final durable job `job-0a31d88e8608`: `BOUNDARY_CONFIRMED`.
Seal `ac2a215c23e055f0f3ac6b4a5bbec0af50c4d32e`.

## Verification discipline
A combined async runner printed `7 passed` but returned wrapper `status=FAILED` / `return_code=null`. Under R3.1 that receipt was treated as UNKNOWN/non-evidence.

The exact same MS1964–1970 subject was rerun synchronously:
- rc=0;
- status COMPLETED;
- **7/7 PASS in 1.23s**.

Compileall over the active MS1967–1970 research/substrate/tests: PASS.

Because Microseed core bytes are unchanged since the MS1961 whole-organism witness, the prior **732/732** cleanup-neutral whole-organism result remains the current core-byte compatibility witness; MS1962–1970 research/test additions have focused current verification. No ceremonial full rerun is claimed as newly necessary merely because test/methodology artifacts were added.

## Language-gate effect
Proto-reference now supports bounded operational claims across:
- sensor permutation;
- noisy current calibration;
- separate calibrated frames;
- overlap handoff;
- no-overlap re-association;
- one-to-many affordance decomposition.

And explicitly abstains from:
- hidden-substitution persistence;
- genealogy;
- numerical identity inheritance;
- semantic object identity.

This materially reduces the proto-reference blocker but does not open lexical language by itself.

## Next dual-arm frontier
Scientific P0: **representation-growth adequacy under reality pressure**.
Ask whether Microseed can enlarge an inadequate prelingual operational representation using existing constructor/projection/discovery owners without supplied semantic categories.

Reality arm should supply an environment where the current representation provably aliases behaviorally distinct operational situations, then test whether existing discovery machinery can construct a discriminating representation and requalify it.

Prewrite:
- `REPRESENTATION_INADEQUACY != NEED_FOR_LANGUAGE`;
- `NEW_OPERATIONAL_DISCRIMINATOR != SEMANTIC_CATEGORY`;
- `REPRESENTATION_GROWTH != SELF_QUALIFICATION`;
- `CONSTRUCTOR_DISCOVERY != ONTOLOGY_TRUTH`.

Secondary identity seam remains open: what additional continuity evidence, if any, can strengthen operational re-association toward individual persistence without semantic injection.