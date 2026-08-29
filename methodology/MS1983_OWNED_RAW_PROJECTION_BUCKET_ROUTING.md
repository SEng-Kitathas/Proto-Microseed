# MS1983 — Owned Raw-Projection Bucket Derivation and Existing Relation Routing

Date: 2026-08-29 ET
Status: core-changing composition candidate
Parent: MS1982 `dfcd4017b0d0b18bad88d5093ae61188cf6a8db1`

## Question
Can a current admitted raw-coordinate projection be reused consequentially without allowing a caller to choose its projection bucket?

Prewrites:
- `ADMITTED_PROJECTION != CALLER_BUCKET_AUTHORITY`;
- `OPAQUE_BUCKET_DERIVATION != SEMANTIC_CLASSIFICATION`;
- `PROJECTION_BUCKET_SELECTION != TRUTH_AUTHORITY`;
- `REPRESENTATION_REUSE != LANGUAGE`.

## Existing owner audit
The historical projection-conditioned predictive-relation routing owner already provides:
- projection id/epoch/signature binding;
- independently qualified existing action-outcome relations;
- externally qualified bucket->relation routing;
- route currentness checks;
- no truth, semantic-regime, model-switch or execution authority.

Its generic resolver intentionally accepts `projection_bucket_id` from the caller.

MS1865 previously removed this caller-bucket requirement only for one-step visible-history refinement by deriving the bucket from the exact admitted predecessor transition.

## Missing ownership seam
For MS1978+ raw-coordinate projections, no equivalent current-evidence bucket resolver existed.

The projection itself already owns a pure opaque `project(raw_tokens)` mapping, and MS1978 already owns bounded current raw-observation receipts.

Therefore no new routing learner, feature ontology, or semantic classifier is required.

## Minimum embodiment
Added:
`resolve_current_raw_projection_conditioned_relation(...)`.

The method:
1. requires an existing current externally qualified projection-conditioned routing binding;
2. requires the exact current EpistemicProjectionRecord bound by that routing;
3. exact-matches one still-present nominated raw projection candidate by digest;
4. checks all candidate frame ancestry is current;
5. requires a current opaque control-state witness;
6. finds exactly one bounded raw-observation receipt attached to that exact current control-state evidence;
7. rechecks receipt capability epoch/signature, frame epoch/signature/binding, control-state id, and candidate frame membership;
8. invokes the candidate's existing opaque `project(raw_tokens)` to derive the bucket;
9. delegates bucket->relation selection to the existing qualified routing resolver;
10. persists nothing and grants no bucket-selection, semantic-coordinate, semantic-projection, truth, model-switch or execution authority.

If the exact nominated candidate content is absent (for example after a restart that restores only projection records), the method abstains rather than treating record-local currentness as content recoverability.

## Process-backed discriminator
Scratch:
`scratch/ms1983_owned_raw_projection_routing.py`.

The MS1978 XOR process world is reused to earn a current two-coordinate opaque projection.

Two independently qualified action-outcome relations are installed:
- EVEN relation;
- ODD relation.

The existing projection-conditioned routing owner is externally qualified across both opaque buckets.

For current raw pair `(0,0)`:
- admitted projection maps to the opaque EVEN bucket;
- the legacy generic resolver is deliberately called with the *other* qualified bucket and returns the ODD relation;
- the new owned resolver accepts no bucket argument and returns the EVEN relation from current raw evidence.

This demonstrates that caller bucket choice was a real ownership boundary, not merely API cosmetics.

## Execution
Initial async job `job-bb28381ab475` produced complete PASS stdout but execution supervision was lost (`SUPERVISION_LOST`, null exit code). It is not used as the final execution witness.

Exact synchronous replay:
- rc=0;
- stdout `status=PASS`;
- candidate input positions `(0,1)`;
- legacy wrong caller bucket -> `R-MS1983-ODD`;
- owned current-evidence route -> `R-MS1983-EVEN`;
- derivation basis `CURRENT_BOUNDED_RAW_OBSERVATION_PLUS_EXACT_ADMITTED_PROJECTION`.

Earned:
`CURRENT_OWNED_RAW_OBSERVATION_CAN_BE_PROJECTED_THROUGH_THE_EXACT_ADMITTED_OPAQUE_PROJECTION_AND_REUSED_BY_EXISTING_EXTERNALLY_QUALIFIED_RELATION_ROUTING_WITHOUT_CALLER_BUCKET_AUTHORITY`.

## Authority ceiling
- projection bucket selection authority: NONE;
- coordinate semantics: NONE;
- semantic projection/category authority: NONE;
- truth authority: NONE;
- model-switch authority: NONE;
- execution authority: NONE;
- language authority: NONE.

## Next discriminator
Pressure the same lawful reuse pattern for **externally qualified temporal constructor projections** derived from owned temporal raw history.

Question:
Can current owned temporal raw receipts reconstitute the constructor's raw-history input, compute its opaque bucket internally, and feed existing projection-conditioned relation routing without caller history/bucket authority?

Do not add a semantic relation graph or concept-composition manager unless existing constructor projection + owned temporal-history bridge fails to compose.