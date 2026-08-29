# MS1959–MS1961 — Affordance-Relative Proto-Reference and Symmetry Ceiling

Date: 2026-08-29 ET
Status: research result embodied minimally in existing Microseed referent owner
Parent: MS1958 within-session boundary coherence

## Scientific question
Can a prelingual operational referent be re-associated across changing sensor layouts and intervention order without supplied object labels, while refusing numerical identity when the observable/action structure is symmetry-equivalent?

## MS1959 — content re-association across sensor permutation
Scratch:
`scratch/ms1959_cross_session_operational_referent_signature.py`
Job `job-d6beded9db36` PASS.

The within-session channel groups changed when sensor channels were permuted, but the content of each group's change-boundary pattern produced the same two SHA-256 signatures across sessions.

Evaluator-only latent-source alignment showed that each shared signature corresponded to the same latent source across those sessions. The latent mapping was used only for scoring, never to compute the signature.

Earned:
`NOMINATED_BOUNDARY_GROUP_CONTENT_CAN_REASSOCIATE_OPERATIONAL_REFERENT_PARTITIONS_ACROSS_SENSOR_PERMUTATION_WITHOUT_CHANNEL_IDENTITY`.

Limit:
that signature depended on the exact intervention schedule. Therefore it was protocol-relative, not a general referent identity.

## MS1960 — affordance-relative signature across protocol-order change
Scratch:
`scratch/ms1960_affordance_relative_proto_referent.py`
Initial composition job `job-04d7738f5e64` PASS.
Integrated-owner rerun `job-a39f1fd19f98` PASS.

Two sessions used:
- different sensor-channel mapping;
- different intervention ordering;
- same opaque effect handles `FX-A`, `FX-B`, `FX-G`.

Raw temporal boundary hashes changed under the different protocol order, as expected.

For each already boundary-coherent group, the derivation instead recorded the boolean response pattern for each opaque action handle. The resulting action-response signatures remained exactly stable across both sensor permutation and intervention-order change.

Evaluator-only alignment again showed the same two signatures tracked the same two latent causal sources under those conditions.

Earned:
`OPAQUE_ACTION_RESPONSE_STRUCTURE_CAN_REASSOCIATE_PROTO_REFERENT_PARTITIONS_ACROSS_SENSOR_AND_PROTOCOL_ORDER_CHANGES`.

## Minimum organism embodiment
The successful scratch derivation was moved into the existing owner:
`microseed/cognition/referents.py`.

Added:
- `OperationalReferentSignature`;
- `derive_affordance_relative_referent_signature(...)`.

The function is pure/read-only. It consumes:
- channel boundary signatures;
- one already-nominated group;
- an opaque action sequence.

It returns:
- status;
- content SHA-256;
- opaque action-response rows;
- explicit reason;
- authority NONE;
- identity authority NONE;
- semantic-reference authority NONE.

It does not register objects, persist identity, execute actions, infer action meaning, or create language tokens.

This is the first Microseed-core cognition change since published MS1947. It was admitted because the research result demonstrated a reusable representation/binding that could no longer remain solely in the evaluator if the organism was to own the proto-referential distinction.

## MS1961 — joint sensor+actuator alias symmetry
Scratch:
`scratch/ms1961_joint_sensor_actuator_symmetry.py`
Initial job `job-972f2a506ba5` PASS.
Integrated-owner rerun `job-f246e4c23c70` PASS.

Hostile:
- session B permutes sensor channels;
- session B also swaps the opaque names attached to the two selective effect handles;
- local action-response graph remains structurally identical.

Result:
the exact same local operational signatures align to opposite evaluator-only latent sources across the two sessions.

Thus no local algorithm can lawfully infer which physical source is numerically the same from that symmetry-equivalent local graph alone.

Earned:
`JOINT_SENSOR_AND_ACTUATOR_ALIAS_SYMMETRY_MAKES_CROSS_SESSION_NUMERICAL_REFERENT_IDENTITY_UNIDENTIFIABLE_FROM_LOCAL_AFFORDANCE_STRUCTURE_ALONE`.

Required breaker:
`ADDITIONAL_CONTINUITY_OR_ASYMMETRIC_EVIDENCE_REQUIRED`.

## Authority ceiling
Preserve all of the following:
- `AFFORDANCE_RELATIVE_OPERATIONAL_REFERENT != NUMERICAL_OBJECT_IDENTITY`;
- `CONTENT_SIGNATURE != SEMANTIC_NAME`;
- `REFERENT_REASSOCIATION != LANGUAGE_REFERENCE`;
- `OPAQUE_ACTION_HANDLE != ACTION_MEANING`;
- `LOCAL_GRAPH_ISOMORPHISM != PHYSICAL_IDENTITY`;
- `IDENTITY_AUTHORITY = NONE`;
- `SEMANTIC_REFERENCE_AUTHORITY = NONE`.

## Language-gate consequence
This campaign materially narrows the prelingual reference gap.

Microseed can now own a bounded, content-addressed proto-referential carrier based on operational affordance structure rather than sensor index. It can survive changing appearance/channel layout and protocol ordering when the opaque effect handles remain stable/current.

What remains is not simply 'invent a referent registry'. The next hard problem is how developmental continuity or independent asymmetric evidence can lawfully break joint alias symmetries when operational labels themselves change.

Language must not be used to supply that identity relation in advance.
