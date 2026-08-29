# MS1980 — Three-Coordinate Owned Projection Support Growth

Date: 2026-08-29 ET
Status: process-backed composition result; no Microseed-core mutation after MS1978
Parent: MS1979 sealed at `29485101abc8105a971545c9be1ccfc0c7460384`

## Question
Does the MS1978 owned raw-observation bridge compose with the existing bounded projection grammar beyond the two-coordinate XOR case?

## World
Separate process:
`research/substrate_shadow/raw_coordinate_parity3_world_server.py`.

The external observation contains one opaque 3-token vector drawn from all eight binary triples.
Visible control state remains `ALIAS`.

Action `B` produces:
- `EVEN` when the three-bit parity is even;
- `ODD` when parity is odd.

By construction, every one-coordinate and every two-coordinate subset is insufficient. The full three-coordinate conjunction is predictive.

## Owned acquisition
Scratch:
`scratch/ms1980_three_coordinate_owned_projection.py`.

64 actual process-backed trials were acquired under the existing explicitly EQUIPPED first-probe action boundary.

For each trial:
1. current opaque control state was established;
2. the current three-token observation was persisted through `record_bounded_raw_observation_coordinates(...)` with exact frame/capability/control-state ancestry;
3. action `B` executed through ordinary action closure;
4. actual process outcome was authenticated;
5. `derive_admitted_projection_samples_from_owned_raw_observations()` rejoined the durable raw receipt and action outcome into an ephemeral existing `ProjectionSample`.

Owned sample count: 64.
All eight opaque raw patterns were represented.

## Discriminator
Using the same entity-derived samples:

### `max_subset = 2`
Projection discovery returned zero candidates.

### `max_subset = 3`
Projection discovery selected exactly input positions:
`(0,1,2)`.

Observed:
- validation accuracy 1.0;
- lift 0.5416666666666667;
- 16/16 separate-process external holdouts correct before qualification.

External qualification/admission remained unchanged.

## Execution
Durable job:
`job-dcd4a738fcd6` PASS / rc=0.

Earned:
`OWNED_BOUNDED_RAW_OBSERVATION_BRIDGE_AND_EXISTING_PROJECTION_SEARCH_COMPOSE_TO_THREE_COORDINATE_SUPPORT_WHEN_ALL_LOWER_ARITY_SUBSETS_ARE_INSUFFICIENT`.

## Interpretation
MS1980 rejects the hypothesis that MS1978 merely special-cased a two-coordinate XOR.

Existing bounded projection discovery can grow support arity when supplied/current search ceiling permits it; the newly embodied owned raw ingress supplies the data without caller-provided feature slices.

No new projection search mechanism, feature ontology, or coordinate registry was added.

## Authority ceiling
- raw coordinate content: owned bounded observation evidence;
- coordinate semantics: NONE;
- support/search ceiling: supplied bounded grammar;
- projection proposal authority: NONE;
- qualification: external only;
- truth authority: NONE;
- language authority: NONE.

Preserve:
- `SUPPORTED_ARITY3_GROWTH != OPEN_ENDED_FEATURE_GRAMMAR`;
- `COORDINATE_POSITION != SEMANTIC_FEATURE_IDENTITY`;
- `MULTI_COORDINATE_PREDICTION != CATEGORY_MEANING`.

## Next high-information discriminator
Pressure **temporal raw-coordinate composition**.

Construct a process world where:
- the current raw observation alone is insufficient;
- visible-state history alone is insufficient;
- a bounded relation between previous and current owned raw observations predicts the outcome.

First test the existing constructor using supplied raw-history slices. If it succeeds, localize whether the only missing owner is an authenticated raw-observation predecessor-chain -> existing ConstructorProjectionSample bridge. Do not add a temporal feature learner unless existing constructor growth fails.