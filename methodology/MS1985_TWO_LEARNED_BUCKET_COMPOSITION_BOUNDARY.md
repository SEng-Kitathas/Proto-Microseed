# MS1985 — Two Learned Opaque Buckets as Second-Stage Projection Coordinates

Date: 2026-08-29 ET
Status: boundary localization; no Microseed-core mutation
Parent: MS1984 `7f99c49764776ed70ee61e03d9c4b77cb1946953`

## Question
Can two independently learned opaque projection buckets act as bounded inputs to another existing projection learner when neither source bucket alone predicts the new outcome?

Prewrites:
- `OPAQUE_DERIVED_BUCKET != SEMANTIC_SYMBOL`;
- `REPRESENTATION_COMPOSITION != SEMANTIC_COMPOSITION`;
- `DERIVED_BUCKET_COORDINATE != FEATURE_ONTOLOGY`;
- `SECOND_STAGE_PROJECTION != LANGUAGE`.

## Process world
Separate process:
`research/substrate_shadow/learned_bucket_composition_world_server.py`.

Raw state is a four-bit opaque vector `(a,b,c,d)` over all 16 combinations.

Actions:
- `A` outcome depends only on parity `(a,b)`;
- `B` outcome depends only on parity `(c,d)`;
- `Z` outcome is `SAME` when those two parities agree and `DIFF` otherwise.

## Independent source projections
Using separate process samples:
- admitted `P-MS1985-A` learns exact raw positions `(0,1)` for action A;
- admitted `P-MS1985-B` learns exact raw positions `(2,3)` for action B.

Both are ordinary externally qualified opaque `EpistemicProjectionRecord`s. Their bucket IDs remain hash-derived operational labels with no semantic authority.

## Second-stage boundary
For each actual Z process outcome, the harness applies the two exact admitted source candidate mappings to the same raw vector and constructs an existing `ProjectionSample` whose two raw tokens are:
`(bucket_A, bucket_B)`.

This step is deliberately harness-side in MS1985. It measures whether the existing projection search can consume learned opaque buckets before any entity-owned composition bridge is added.

64 second-stage samples were generated.

Using the same rows:
- max subset 1 -> zero candidates;
- max subset 2 -> exact `(0,1)` second-stage projection;
- validation accuracy 1.0;
- lift 0.5;
- 16/16 separate-process holdouts correct.

Synchronous execution: rc=0 / `BOUNDARY_CONFIRMED`.

Earned:
`EXISTING_PROJECTION_SEARCH_CAN_COMPOSE_TWO_INDEPENDENTLY_LEARNED_OPAQUE_BUCKETS_INTO_A_SECOND_STAGE_PREDICTIVE_PARTITION_WHEN_EACH_BUCKET_ALONE_IS_INSUFFICIENT`.

## Missing owner
`ENTITY_OWNED_CURRENT_PROJECTION_BUCKET_VECTOR_TO_PROJECTION_SAMPLE`.

No new projection search mechanism is required.

## Assistance / authority ceiling
- source projection learning: bounded supplied search grammar + external qualification;
- source bucket vector in MS1985: harness-derived from exact admitted source projection content;
- semantic symbol authority: NONE;
- semantic composition authority: NONE;
- truth authority: NONE;
- language authority: NONE.

## Next discriminator — MS1986
Add the narrowest ephemeral entity-owned bridge that:
1. starts from ordinary owned raw projection samples / authenticated action outcomes;
2. discovers compatible current admitted raw projections by exact record/candidate digest and current frame ancestry;
3. requires each selected source projection to project every base sample rather than silently dropping rows;
4. orders source projections opaquely and deterministically;
5. emits existing `ProjectionSample` values whose raw tokens are only the derived opaque buckets;
6. persists no sample and grants no semantic/symbol/truth/qualification authority;
7. refuses rather than arbitrarily truncating if compatible source count exceeds its bounded ceiling.

Do not add a concept graph, symbol registry, or recursive representation manager unless this composition fails.