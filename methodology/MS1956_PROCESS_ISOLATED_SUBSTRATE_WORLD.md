# MS1956 — Process-Isolated Substrate World

Date: 2026-08-29 ET
Status: research ↔ reality process-boundary embodiment
Parent: MS1955 `b2f54b6e225e88fd8811a197aeb662e9dff8e194`

## Question
Does the experimental substrate still work when the external world is not an in-memory Python object sharing state with the test process, but a separately running process accessed only through a serialized protocol?

Prewrite:
- `EXTERNAL_WORLD_OBJECT != EXTERNAL_PROCESS_REALITY`;
- `SERIALIZED_INTERFACE_SUCCESS != SHARED_MEMORY_SUCCESS`;
- `SEPARATE_PROCESS != QUALIFICATION_INDEPENDENCE_PROVED`.

## Embodiment
World process server:
`research/substrate_shadow/process_world_server.py`

Protocol:
newline-delimited JSON over stdin/stdout.
Operations:
- `reset`;
- `apply`;
- `observe`;
- `observe_outcome`;
- `close`.

Live world client:
`ProcessChargeWorld` in `scratch/ms1956_process_isolated_environment.py`.

The live process owns its internal level state. The adapter can interact with it only through serialized requests/responses.

Qualification role:
`ProcessQualificationSource` starts a separate process for each holdout sample. These sample processes do not share the live world's state or PID.

## Adapter lifecycle hardening
To support process-owning worlds, generic shadow-adapter fork paths were tightened:
- temporary equipped probes are closed if they expose `close()`;
- temporary forked qualification worlds are closed after sampling.

This is an external resource lifecycle requirement, not a Microseed cognition change.

## Result
Scratch:
`scratch/ms1956_process_isolated_environment.py`

Job `job-5e584fbb15fc` PASS.

Observed:
- live external world PID = 16144;
- 16 qualification samples came from 16 distinct other PIDs;
- learned relation = `ACTION-LAW-ef9f22950c81a8b968ce`;
- predicted final state = `PROC-LEVEL-2`;
- actual final state = `PROC-LEVEL-2`;
- no shared Python world-object state.

Earned statement:
`SHADOW_SUBSTRATE_OPERATES_ACROSS_SERIALIZED_PROCESS_BOUNDARY_WITH_SEPARATE_QUALIFICATION_PROCESSES`.

## Nonclaims
This does not establish:
- physical-world validity;
- network/distributed fault tolerance;
- qualification independence merely because processes differ;
- safe process-crash recovery;
- general environment protocol completeness.

Those remain reality-pressure frontiers.

No Microseed-core mutation was required.