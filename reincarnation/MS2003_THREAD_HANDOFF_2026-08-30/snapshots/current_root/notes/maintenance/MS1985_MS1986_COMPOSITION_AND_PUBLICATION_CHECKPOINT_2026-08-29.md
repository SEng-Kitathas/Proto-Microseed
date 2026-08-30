# MS1985–MS1986 Composition + Publication Checkpoint — 2026-08-29

## Authority / lineage
- Canonical Main-Dev remains MS1527.
- Research baseline remains MS1887.
- `origin/main` remains MS1939 `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`.
- Current sealed LOCAL research: **MS1986 `383196060c0bb88980a2e22b972972a4e09f58a5`**.
- Tree: `82bcf09060977aae16239ec8ac1dafabf6f60bd0`.
- Source/test snapshot: `242d743d38cb3ac48814cdd57e348689e856ad0fefca56f1e984d200b3096317` / 311 Python files.
- Worktree clean.
- Novelty remains `UNKNOWN / NOT_ENTITLED_TO_CLAIM`.

## MS1985 boundary
Sealed commit: `9ef6ea3f33f27ef6cdf8aea1093f7ba688be2c85`.

Process world learned two independent opaque source projections:
- A -> raw positions `(0,1)`;
- B -> raw positions `(2,3)`.

Second-stage harness-supplied source bucket pair:
- one bucket alone -> zero candidates;
- pair -> exact `(0,1)`;
- validation 1.0;
- lift 0.5;
- external holdouts 16/16.

Earned:
`EXISTING_PROJECTION_SEARCH_CAN_COMPOSE_TWO_INDEPENDENTLY_LEARNED_OPAQUE_BUCKETS_INTO_A_SECOND_STAGE_PREDICTIVE_PARTITION_WHEN_EACH_BUCKET_ALONE_IS_INSUFFICIENT`.

Missing owner localized to entity-owned current projection-bucket vector -> existing ProjectionSample.

## MS1986 embodiment
Added `derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=...)`.

Positive result:
- source projections automatically selected from exact compatible current admitted projections: `P-MS1986-A`, `P-MS1986-B`;
- owned second-stage sample count 64;
- one source bucket alone -> zero candidates;
- pair -> exact `(0,1)`;
- validation 1.0;
- lift 0.6875;
- external holdouts 16/16;
- second-stage admitted as `P-MS1986-SECOND`;
- no new projection-search mechanism.

Earned:
`CURRENT_EXACT_ADMITTED_RAW_PROJECTIONS_CAN_AUTOMATICALLY_SUPPLY_AN_OPAQUE_BUCKET_VECTOR_OVER_OWNED_ACTION_HISTORY_TO_FEED_EXISTING_SECOND_STAGE_PROJECTION_GROWTH`.

## Lineage footgun and repair
Before seal, hostile review found that a second-stage projection could otherwise be admitted without explicit source-projection currentness ancestry.

Repair added optional exact ancestry:
`(source_projection_id, epoch, signature_sha256)`
through:
`ProjectionSample -> EpistemicProjectionCandidate -> EpistemicProjectionRecord`.

Properties:
- empty lineage omitted, preserving legacy IDs/digests;
- non-empty lineage content-binds second-stage candidate id/digest;
- registration requires dependency-current exact sources;
- currentness recursively checks source projection ancestry;
- source change/invalidation transitively stales dependent projection(s);
- dependent change/reactivation refuses stale source ancestry;
- mixed-lineage training/validation rows reject rather than silently merge regimes.

## Verification
Focused MS1985–86:
- `job-46230c752dac` -> **7/7 PASS in 14.24s**.

Whole exact MS1986 candidate:
- `job-fd198cea1c3b` -> **774/774 PASS in 346.54s**;
- stderr empty;
- self-test 81/81 PASS;
- compileall PASS.

Legacy digest compatibility was cross-checked against a detached sealed-MS1985 worktree:
- source A `4bde8127577b857952341dcd4da4c7ef18df9a9c46eefeebf777b520aca55d25` unchanged;
- source B `88e4d5d1b31d751c2deb379d9e1663318eb347df7104777100b81b546a37aa2e` unchanged.

## Local seal
Commit:
`383196060c0bb88980a2e22b972972a4e09f58a5`

Tree:
`82bcf09060977aae16239ec8ac1dafabf6f60bd0`

## GitHub publication
Operator standing directive now requires every publication-eligible substantive pass to end:
`VERIFY -> SEAL -> PUSH -> REMOTE READBACK`.

Push transport used explicit Git Credential Manager because global config still reports `helper-selector`:
`git -c credential.helper= -c credential.helper=manager push origin refs/heads/research/ms1888-replay:refs/heads/research/ms1888-replay`.

Push transport returned success:
`673db99..3831960 research/ms1888-replay -> research/ms1888-replay`.

Independent remote readback:
`git ls-remote origin refs/heads/research/ms1888-replay`
returned exactly:
`383196060c0bb88980a2e22b972972a4e09f58a5`.

Therefore publication status is:
**GITHUB_PUBLISHED / REMOTE_READBACK_VERIFIED**.

`origin/main` remains unchanged at MS1939.

## Authority ceiling
- derived bucket semantic authority: NONE;
- semantic symbol authority: NONE;
- semantic composition authority: NONE;
- truth authority: NONE;
- language authority: NONE;
- publication != main promotion != canonical promotion.

## Next frontier
MS1987 depth-3 composition pressure:
A/B -> second-stage C; C + independent D -> third-stage E; source A invalidation must transitively stale C and E.

Prewrite:
`RECURSIVE_OPAQUE_REPRESENTATION_COMPOSITION != SEMANTIC_RECURSION`.
