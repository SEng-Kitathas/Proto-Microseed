# 06A — Server Execution Methodology for Unreliable Planes

## Purpose
This document defines the project-agnostic operating method when server planes, bridge paths, queue surfaces, or orchestration routes are flaky, rate-limited, degraded, or otherwise unreliable.

The objective is execution reliability: preserve consequence-bearing work even when the aesthetically preferred route is not the route that actually lands.

## Core rule
**Use the strongest surviving plane, not the prettiest plane.**

If a bridge, queue, or interactive orchestration path fails repeatedly, do not keep retrying the same fragile route. Move the work onto the server-native/operator-side path that actually lands.

## Operator-side default rule
Default to the operator-owned/local/server side for as much as possible.

If the operator-side environment can save, store, edit, execute, mutate, materialize, or read back the consequence-bearing state, that path SHOULD be the default. Assistant/model-side execution SHOULD take the lead only when it is materially better or faster for the specific step.

The execution preference is therefore:

1. strongest surviving operator-side plane first;
2. assistant/model-side execution only when it has a material capability or speed advantage for that step.

The burden is on the assistant/model to justify leaving an available and sufficient operator-side path. Assistant-side convenience alone is not sufficient justification.

## Plane order of preference under instability
When the environment is partially degraded, prefer:

1. server-native project execution routes;
2. direct local subprocess or Python execution from the server/operator side;
3. durable project-local script files, then execute them from the server/operator side;
4. chat-side or bridge-side ad hoc execution only when the stronger local routes are unavailable or materially inferior for the specific step.

Guiding principles:
- keep work close to the machine/state that will actually perform or persist it;
- prefer the operator side when available and sufficient;
- reduce moving parts;
- do not repeat known-failing paths without a causal reason.

## Practical operating method
### 1. Inspect first
Before mutation or execution:
- verify the target root;
- verify the runtime/interpreter path;
- verify the artifacts the run depends on;
- verify where outputs should land;
- verify the consequence-bearing readback surface.

Do not assume a path works merely because it worked once in another plane.

### 2. Materialize scripts; do not over-orchestrate inline
If a run matters, prefer a durable project-local runner script:
- the script owns the bounded operation;
- the operator/server environment executes it by default;
- logs and artifacts are written server-side;
- reruns and recovery remain inspectable.

### 3. Bypass unstable orchestration, not safety/authority
When a queue or bridge is unreliable, move execution to a stronger server-native/local route when authorized. This is execution-plane selection, not permission to bypass safety, approval, access-control, or authority boundaries.

Do not keep feeding a known-brittle queue and expecting transport behavior to improve without evidence.

### 4. Make writes incremental and resumable
Long operations SHOULD:
- write progress incrementally;
- flush at meaningful checkpoints or per item where practical;
- support resume;
- capture per-item failures without needlessly discarding successful work;
- preserve a clear completion marker and partial-state semantics.

A long run should degrade into inspectable partial progress rather than total information loss wherever the operation permits it.

### 5. Separate execution truth from chat truth
A run is real when the machine proves it through consequence-bearing evidence such as:
- job/execution ID;
- PID where applicable;
- stdout/stderr paths;
- durable output artifacts;
- summary JSON or equivalent structured receipt;
- repository/remote state;
- exact hashes or other task-appropriate identities.

Conversational memory or a successful-looking response does not outrank machine state.

## Stable execution pattern
For high-value work, prefer:

1. write a project-local runner script;
2. execute it through the strongest available operator-side/server-native route;
3. keep stdout/stderr server-side;
4. emit structured result files into a known output directory;
5. inspect those artifacts directly before making claims;
6. return only the compact consequence-bearing receipt and targeted exceptions through the control plane.

This becomes the default as soon as a workflow shows meaningful bridge or queue fragility.

## Model / inference workloads
For inference, benchmark, or evaluator runs:
- prefer an already-provisioned heavy runtime that contains the required libraries;
- explicitly bind interpreter/runtime, model, input packet, and output paths;
- persist prediction/result files;
- score from durable files rather than ephemeral stdout alone;
- keep prompt/contracts explicit and parser-friendly;
- move the whole execution loop into the server-side runner when chat/queue orchestration becomes the weak link.

## File mutation and tool import
When moving SOPs, review machinery, or tooling across environments:
- inspect source surfaces separately;
- copy only load-bearing docs/tools rather than unrelated debris;
- preserve provenance by naming the import source clearly;
- record why the import occurred;
- keep imports under an explicit import/provenance root until deliberately integrated.

Import does not self-promote into authority.

## Anti-patterns
Do not:
- keep retrying a bridge route that has already shown repeated failure;
- rely on a known-unstable queue for long-running work when a stronger local path exists;
- depend on a giant inline command when a durable script would materially improve recoverability;
- claim success before reading back consequence-bearing output;
- confuse submitted with started, started with completed, completed with persisted, or persisted with published;
- move work assistant-side merely because it is convenient.

## Default under degraded conditions
When in doubt:
- write the script;
- run it operator/server-side;
- keep outputs on disk;
- inspect artifacts directly;
- begin with a bounded smoke run where uncertainty warrants it;
- widen only after the execution path proves stable.

## Assistant-side exception clause
Assistant/model-side execution is allowed when it is materially better or faster for the specific step, for example:
- a bounded transformation where assistant-side execution has a substantial speed advantage;
- a required tool surface exists only on the assistant side;
- operator-side setup cost would dominate a genuinely one-off bounded step.

The exception SHALL remain explicit. Assistant-side convenience alone is not enough.

## Governing non-equivalences
`STRONGEST_SURVIVING_PLANE != PRETTIEST_PLANE`
`OPERATOR_SIDE_DEFAULT != ASSISTANT_SIDE_PROHIBITED`
`ASSISTANT_SIDE_CONVENIENCE != MATERIAL_ADVANTAGE`
`EXECUTION_PLANE_FALLBACK != AUTHORITY_BYPASS`
`CONTROL_PLANE_RESPONSE_FAILURE != LOCAL_EXECUTION_FAILURE`
`STARTED != COMPLETED`
`COMPLETED != PERSISTED`
`PERSISTED != PUBLISHED`

Canonical scar:

**DO THE WORK WHERE THE STATE LIVES; RETURN ONLY THE EVIDENCE NEEDED TO CONTROL IT.**
