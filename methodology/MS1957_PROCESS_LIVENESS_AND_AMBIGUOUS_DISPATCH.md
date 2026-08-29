# MS1957 — External Process Liveness / Ambiguous Dispatch Boundary

Date: 2026-08-29 ET
Status: pre-repair reality violation reproduced; adapter-level repair verified
Parent local research head: MS1956 `7c8327f5d8b6c398a788fe3ed32ce7b7e4c7439c`
Process doctrine: RAHL R3.1 project-local shadow use

## Question
Once process-backed learned competence, rehearsal and intent are current, what happens if the external endpoint disappears before physical execution or disappears after a request may have crossed the transport boundary?

Prewrite:
- `PROCESS_INTERFACE_ATTACHED != PROCESS_STILL_ALIVE`;
- `CURRENT_CAPABILITY_CONTRACT != CURRENT_EXTERNAL_ENDPOINT`;
- `PREDICTIVE_RELATION_CURRENTNESS != ENDPOINT_LIVENESS`;
- `INTENT_AUTHORIZED_BEFORE_CRASH != EXECUTION_AUTHORIZED_AFTER_CRASH`;
- `TRANSPORT_FAILURE != WORLD_OUTCOME`;
- `DISPATCH_ATTEMPT != KNOWN_EFFECT_COMPLETION`.

## Pre-repair hostile
Scratch:
`scratch/ms1957_process_liveness_hostile.py`

Job `job-f3187026c73f` reproduced the defect.

After the external process was killed:
- `PROC-CHARGE` remained `SHADOW_QUALIFIED`;
- learned relation remained `CURRENT_PREDICTIVE_RELATION`;
- rehearsal proposal remained `CURRENT_REHEARSAL_PROPOSAL`;
- direct Microseed execution reached the handler and raised `RuntimeError:PROCESS_WORLD_NOT_RUNNING:1`.

Good invariant retained even pre-repair:
- execution count did not increase;
- outcome count did not increase.

Thus Microseed did not fabricate a completed effect, but the shadow substrate lacked a pre-effect endpoint-liveness owner.

Earned violation:
`CURRENT_INTERNAL_PREMISES != CURRENT_EXTERNAL_ENDPOINT_LIVENESS`.

## Minimum repair location
No Microseed-core world/liveness manager was added.

The external adapter/world contract now owns endpoint liveness:
- `ExternalWorld.is_available()`;
- `ShadowEnvironmentAdapter.refresh_endpoint_liveness(...)`;
- `ShadowEnvironmentAdapter.execute_intent(...)` as the shadow-substrate effect boundary.

When endpoint liveness is known false, the adapter invalidates current world-bound action/observation premises through the existing `CapabilityRegistry.invalidate(...)` owner. Transitive dependency/currentness propagation then stales the environment-binding premise, learned relation and rehearsal proposal through already-earned Microseed mechanisms.

## Transport consequence classes
Added external exceptions:
- `ExternalEndpointUnavailable`: endpoint known unavailable before dispatch;
- `ExternalEndpointAmbiguous`: request may have crossed the transport boundary but completion is unknown.

`ProcessChargeWorld` now maps:
- dead process before request -> unavailable;
- broken/empty transport after request dispatch -> ambiguous.

The process server gained one hostile-only `apply_and_exit` operation that applies the external state transition and exits before writing a reply. This produces a real ambiguous-dispatch condition rather than a mocked exception.

## Post-repair result
Job `job-a945f0183be8` PASS.

### Known-dead before dispatch
After process kill, `adapter.execute_intent(...)` returns:
- status `NO_EXECUTION`;
- reason `EXTERNAL_ENDPOINT_NOT_CURRENT`;
- authority NONE.

Staled capability set:
- `PROC-CHARGE`;
- `SUBSTRATE-OBSERVE`;
- `SUBSTRATE-OBS-BASIS`;
- `SUBSTRATE-ENV-BINDING`.

Consequences:
- execution count unchanged;
- outcome count unchanged;
- learned relation -> `STALE_PREDICTIVE_RELATION / STRUCTURAL_PREMISE_NOT_CURRENT`;
- proposal -> `UNKNOWN_INCOMPLETE / REHEARSAL_CAPABILITY_NOT_CURRENT:PROC-CHARGE`.

A fresh compatible process/adapter attached in a fresh Microseed runtime makes the exact historical relation/proposal current again; fresh intent/execution/outcome succeeds at `PROC-LEVEL-2`.

Earned:
`KNOWN_DEAD_EXTERNAL_ENDPOINT_INVALIDATES_SHADOW_SUBSTRATE_AUTHORITY_BEFORE_EFFECT_AND_COMPATIBLE_REATTACHMENT_RESTORES_HISTORICAL_COMPETENCE`.

### Ambiguous dispatch
The real external process applies `PROC-CHARGE` then exits before response.

Adapter returns:
- status `UNKNOWN_EXECUTION`;
- reason `EXTERNAL_ENDPOINT_DISPATCH_AMBIGUOUS`;
- authority NONE;
- transport error `PROCESS_WORLD_EMPTY_RESPONSE_AFTER_DISPATCH`.

Microseed records neither an execution nor an outcome because no handler result was obtained.
Current world-bound premises are invalidated; relation becomes STALE and proposal UNKNOWN.

Earned:
`AMBIGUOUS_EXTERNAL_DISPATCH_REMAINS_UNKNOWN_AND_INVALIDATES_CURRENT_REALITY_PREMISES_WITHOUT_FABRICATING_OUTCOME`.

## Authority / nonclaims
- adapter liveness is external operational currentness, not semantic world knowledge;
- liveness does not prove action safety or world truth;
- known-dead and ambiguous-dispatch are distinct consequence classes;
- an ambiguous dispatch may have physically changed the world; absence of a Microseed execution record means only that effect completion was not authenticated;
- do not blindly retry an UNKNOWN dispatch;
- direct calls that bypass the shadow adapter are outside the shadow-substrate execution contract and do not inherit its liveness guarantee.

## R3.1 relevance
MS1957 is the first fresh real-project campaign run under R3.1 shadow use. R3.1 E04 directly sharpened the repair: ambiguous process state remained UNKNOWN rather than being compressed into failure/success. R3.1 C02/C03 kept ownership at the external adapter instead of introducing a Microseed liveness manager.
