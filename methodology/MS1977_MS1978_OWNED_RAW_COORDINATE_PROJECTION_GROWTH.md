# MS1977–MS1978 — Owned Raw-Coordinate Projection Growth

Date: 2026-08-29 ET
Status: MS1977 boundary localized; MS1978 minimal core bridge + process-backed embodiment
Parent: MS1976 `c97fc43be92d31c3da36baedce74e58189d7efac`

## Question
Can Microseed grow an opaque predictive representation from multiple raw observation coordinates when no single coordinate is informative, without caller-supplied feature slices or semantic coordinate labels?

Prewrites:
- `RAW_OBSERVATION_AVAILABLE != OWNED_PROJECTION_SAMPLE`;
- `SUPPLIED_FEATURE_SLICE != ENDOGENOUS_SAMPLE_DERIVATION`;
- `MULTI_COORDINATE_SUPPORT != SEMANTIC_CATEGORY`;
- `CONSTRUCTOR_SUPPORT_GROWTH != ONTOLOGY_DISCOVERY`;
- `FRAME_OWNS_COORDINATE_BOUNDARY != MICROSEED_OWNS_SENSOR_SEMANTICS`.

## Process-backed XOR world
Server:
`research/substrate_shadow/raw_coordinate_alias_world_server.py`.

External state exposes one visible control state `ALIAS` plus two opaque raw tokens chosen from:
`00, 01, 10, 11`.

Action `B` produces:
- `EVEN` for `00` and `11`;
- `ODD` for `01` and `10`.

Therefore either raw coordinate alone is statistically useless; the two-coordinate conjunction is perfectly predictive.

## MS1977 — pre-repair boundary
Scratch:
`scratch/ms1977_raw_coordinate_projection_boundary.py`.

Initial harness issues before science:
- missing explicit episode ancestry in rehearsal seed rows;
- fixed by registering current `EP` and binding rows to `EP@0`.

Final pre-repair run:
`job-9c9514ccef8f` PASS / rc=0 as `BOUNDARY_CONFIRMED`.

Observed:
- max subset 1 -> zero projection candidates;
- max subset 2 -> exact input positions `(0,1)`;
- validation accuracy 1.0;
- 16/16 external process holdouts pass;
- ordinary action-outcome evidence does **not** preserve `raw_tokens`;
- harness had to manufacture `ProjectionSample(raw_tokens=pair, ...)`.

Earned:
`EXISTING_PROJECTION_SEARCH_CAN_DISCOVER_A_TWO_COORDINATE_XOR_DISCRIMINATOR_WHEN_RAW_COORDINATES_ARE_SUPPLIED`.

Missing owner:
`BOUNDED_DURABLE_OWNED_RAW_OBSERVATION_COORDINATE_INGRESS`.

No new projection search/feature learner was indicated.

## MS1978 — minimum owned ingress + sample bridge
Added two Microseed facade methods.

### `record_bounded_raw_observation_coordinates(...)`
- invokes an already-current `OBSERVATION_ONLY` capability;
- accepts only a bounded non-empty list/tuple of opaque scalar values returned under key `raw_tokens`;
- hard call bound 1..64 coordinates, caller-supplied per-use maximum;
- rejects nested structures and oversized/empty scalar strings;
- requires exactly one current operational frame bound to the observation capability;
- content-binds evidence to:
  - current control-state evidence id/state id;
  - raw token tuple;
  - coordinate count and bound;
  - observation capability id/epoch/signature;
  - operational scope;
  - frame id/epoch/signature;
- stores the bounded payload in the existing append-only EvidenceLedger and event store;
- grants only OBSERVATION_ONLY evidence authority;
- semantic-coordinate, projection and truth authority remain NONE.

### `derive_admitted_projection_samples_from_owned_raw_observations()`
- scans durable bounded raw receipts;
- rejects receipts whose observation capability/frame epoch/signature/binding is not current;
- re-derives authenticated ordinary transition samples from actual action/outcome history;
- joins exactly one current raw receipt to each execution through the action intent's exact `control_state_evidence_id`, operational scope and frame;
- emits existing `ProjectionSample` values ephemerally;
- persists no sample and grants no qualification/semantic/truth authority.

No raw-coordinate registry, feature ontology, coordinate naming mechanism or new projection search was added.

## MS1978 reality result
Scratch:
`scratch/ms1978_owned_raw_coordinate_projection.py`.

Job:
`job-7e4364f9ceed` PASS / rc=0.

48 actual process-backed trials were executed.
For each trial the entity:
1. established current opaque control state;
2. invoked `OBS` through the new bounded raw-ingress method;
3. persisted exact raw receipt tied to current control-state evidence;
4. executed actual `B` through ordinary action closure;
5. observed/authenticated actual outcome;
6. later re-derived ProjectionSample from owned evidence.

Bridge result:
- owned sample count 48;
- history basis `AUTHENTICATED_RAW_OBSERVATION_PLUS_ACTION_OUTCOME_JOIN`;
- raw patterns exactly all four opaque pairs;
- effect tokens exactly `EVEN`/`ODD`.

Projection search:
- max subset 1 -> zero candidates;
- max subset 2 -> exact `(0,1)`;
- validation accuracy 1.0;
- lift 0.625.

Separate external process holdouts: 16/16.
External qualification admitted `P-MS1978` with existing projection origin `ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED`.

Earned:
`BOUNDED_CURRENT_RAW_OBSERVATION_RECEIPTS_CAN_BE_JOINED_WITH_AUTHENTICATED_ACTION_OUTCOMES_TO_FEED_EXISTING_PROJECTION_SEARCH_AND_EARN_A_TWO_COORDINATE_OPERATIONAL_DISCRIMINATOR`.

## Authority ceiling
- coordinate boundary: supplied/current operational frame;
- coordinate maximum: supplied bounded assistance;
- raw values: owned observation evidence;
- subset grammar/search thresholds: supplied assistance;
- proposal authority NONE;
- qualification: external only;
- semantic coordinate authority NONE;
- semantic projection/category authority NONE;
- truth authority NONE;
- language authority NONE.

## Next pressure
Attack raw-receipt currentness and replay:
- coordinate-limit refusal;
- duplicate current raw receipts for one control state;
- frame/capability drift;
- restart without attachment;
- compatible reattachment.

Then pressure higher-arity support within the already-bounded projection grammar before considering any open-ended feature grammar.