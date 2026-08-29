# MS1986 — Owned Learned-Bucket Composition With Source-Projection Lineage

Date: 2026-08-29 ET
Status: VERIFIED / ready for local seal and publication
Parent: MS1985 `9ef6ea3f33f27ef6cdf8aea1093f7ba688be2c85`

## Question
Can current exact admitted raw projections automatically supply an opaque bucket vector over owned action history to the existing projection learner, and can a resulting second-stage projection remain correctly bounded by the currentness of its source projections?

Prewrites:
- `OPAQUE_DERIVED_BUCKET != SEMANTIC_SYMBOL`;
- `REPRESENTATION_COMPOSITION != SEMANTIC_COMPOSITION`;
- `DERIVED_BUCKET_COORDINATE != FEATURE_ONTOLOGY`;
- `SOURCE_PROJECTION_CURRENTNESS != DEPENDENT_PROJECTION_CURRENTNESS_UNLESS_LINEAGE_IS_BOUND`;
- `SECOND_STAGE_PROJECTION != LANGUAGE`.

## MS1985 boundary inherited
MS1985 proved that the existing projection search already composes two independently learned opaque buckets when their pair predicts an outcome and either bucket alone is insufficient.

Therefore MS1986 does not add a new projection learner.

## Minimum ownership bridge
Added:
`derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=...)`.

The bridge:
1. starts only from the existing owned raw-receipt/action-outcome `ProjectionSample` join;
2. automatically scans current admitted raw projections;
3. requires exact nominated candidate content by digest;
4. requires current source-projection dependency ancestry and exact current frame ancestry;
5. requires each compatible source projection to project every owned base row rather than silently dropping unsupported rows;
6. orders source coordinates deterministically by lexicographic projection id;
7. refuses with `COMPATIBLE_SOURCE_PROJECTION_COUNT_EXCEEDS_BOUND` if compatible source count exceeds the supplied explicit ceiling rather than truncating or choosing;
8. emits ordinary existing `ProjectionSample` rows whose raw tokens are only the opaque derived bucket ids;
9. persists no derived sample and grants no qualification, semantic-symbol, semantic-composition or truth authority.

Caller supplies only a bounded maximum source-projection count. Caller does not supply per-sample bucket values or semantic labels.

## Process-backed embodiment
Separate process:
`research/substrate_shadow/owned_bucket_composition_world_server.py`.

Raw world is the same four-bit parity-composition structure as MS1985, but only action `Z` is exposed to the owned-history runtime:
- source projection A is independently learned/admitted for raw positions `(0,1)`;
- source projection B is independently learned/admitted for raw positions `(2,3)`;
- 64 actual process-backed Z trials enter the Microseed-owned raw/action/outcome history;
- Z outcome is SAME vs DIFF according to whether the two source parities agree.

Bridge result:
- source projections discovered automatically: `P-MS1986-A`, `P-MS1986-B`;
- source count: 2;
- owned second-stage samples: 64;
- coordinate order: `LEXICOGRAPHIC_PROJECTION_ID`;
- max subset 1 -> zero candidates;
- max subset 2 -> exact positions `(0,1)`;
- validation accuracy 1.0;
- lift 0.6875;
- external holdouts 16/16;
- admitted second-stage projection: `P-MS1986-SECOND`.

Earned positive behavior:
`CURRENT_EXACT_ADMITTED_RAW_PROJECTIONS_CAN_AUTOMATICALLY_SUPPLY_AN_OPAQUE_BUCKET_VECTOR_OVER_OWNED_ACTION_HISTORY_TO_FEED_EXISTING_SECOND_STAGE_PROJECTION_GROWTH`.

## Lineage footgun found before seal
The first positive MS1986 run showed that the second-stage candidate could be admitted without structurally recording its dependency on source projections A and B.

That would allow a source projection to change/stale while the dependent second-stage projection remained superficially current.

This was treated as a real currentness defect, not a documentation issue.

## Minimum lineage repair
Added optional exact source-projection ancestry:
`(projection_id, epoch, signature_sha256)`
through the existing chain:

`ProjectionSample -> EpistemicProjectionCandidate -> EpistemicProjectionRecord`.

Rules:
- empty lineage is omitted from serialized/signature payloads, preserving legacy candidate IDs/digests;
- non-empty lineage is sorted and duplicate projection ids are rejected;
- candidate fitting requires one exact source-projection lineage across training + validation rows;
- candidate id/digest becomes content-bound to non-empty source lineage;
- projection admission carries candidate source lineage into the admitted record;
- registration requires all exact source projections to be dependency-current with matching epoch/signature;
- projection currentness recursively requires all source projections to remain current at the exact bound epoch/signature;
- changing or invalidating a source projection transitively invalidates dependent projections;
- dependent reactivation/change refuses if exact source ancestry is not current.

This is dependency lineage, not a concept/symbol graph.

## Hostile verification
Focused tranche:
`tests/embodiment/test_ms1985_two_learned_bucket_composition_boundary.py`
`tests/embodiment/test_ms1986_owned_learned_bucket_composition.py`

Durable focused job:
`job-46230c752dac` -> **7/7 PASS in 14.24s**.

Covered:
1. positive owned second-stage composition + exact source lineage;
2. source A change transitively stales `P-MS1986-SECOND`;
3. stale dependent cannot reactivate against old source epoch;
4. 3 compatible sources with ceiling 2 refuses instead of truncating;
5. missing nominated source projection content produces no composed sample;
6. projection discovery rejects mixed source-lineage rows;
7. legacy empty-lineage MS1985 source projection digests remain byte-for-byte unchanged.

Legacy digest readback was verified against a detached sealed-MS1985 worktree and current candidate tree:
- source A: `4bde8127577b857952341dcd4da4c7ef18df9a9c46eefeebf777b520aca55d25` on both;
- source B: `88e4d5d1b31d751c2deb379d9e1663318eb347df7104777100b81b546a37aa2e` on both.

## Final verification
- focused MS1985–86: `job-46230c752dac` -> **7/7 PASS in 14.24s**;
- whole cleanup-neutral exact candidate tree: `job-fd198cea1c3b` -> **774/774 PASS in 346.54s**;
- stderr: empty;
- Microseed self-test: **81/81 PASS**;
- compileall over microseed/research/scratch/tests: PASS.

## Authority ceiling
- source selection authority: compatible current set + supplied count ceiling only;
- derived bucket semantics: NONE;
- semantic symbol authority: NONE;
- semantic composition authority: NONE;
- truth authority: NONE;
- qualification authority for generated samples: NONE;
- language authority: NONE.

## Interpretation
MS1986 is stronger than simple representation reuse: one learned opaque representation can serve as bounded operational input to another learned opaque representation step without becoming a semantic symbol.

But this remains finite, assisted and opaque. It does NOT establish:
- recursive open-ended representation grammar;
- autonomous source-projection selection policy beyond compatibility + bounded ceiling;
- semantic feature identity;
- semantic composition;
- conceptual reasoning;
- language.

## Next pressure after seal/publication
The highest-information next discriminator is **depth-3 representation composition** with lineage propagation:
- source projections A/B -> second-stage projection C;
- C plus an independent projection D -> third-stage projection E;
- each immediate source alone insufficient;
- source A invalidation must transitively stale C and E.

This would test whether the same lineage/composition mechanism recursively closes at one additional depth without a new representation manager.
