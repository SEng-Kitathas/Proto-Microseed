# 06 — Execution, Release, and Environment Discipline

### E01 — Name the discriminator
Before consequential execution, name what the run can distinguish. Tool work must advance the discriminator or preserve evidence.

### E02 — Durable run receipt
Consequential or durable runs SHOULD record, where applicable:
- working directory;
- interpreter/runtime/toolchain identity;
- consequence-bearing environment variables/configuration;
- start/end timestamps;
- process/job identity;
- stdout and stderr;
- exit code;
- completion marker/status;
- stable artifact paths;
- input/output hashes or identities where needed.

### E03 — Completion is not consequence
Inspect final artifact/state/effect. Tool completion is not task success.

### E04 — Ambiguity remains UNKNOWN
Timeout, disconnected foreground, partial output, submitted job, started job, completed process, and registered artifact are distinct states. Do not infer across missing readback.

### E05 — Mutation claims require readback
Do not claim saved, written, executed, committed, tested, verified, uploaded, extracted, registered, synchronized, or promoted without the corresponding evidence surface confirming it.

### E06 — Release/package qualification
Sealed/release artifacts require exact membership when claimed, manifest/hash identity, clean extraction/replay where relevant, explicit lineage, assurance ceiling, and exclusion of accidental runtime state.

### E07 — Verifier purity
Verification must not silently contaminate the specimen. Isolate generated state when needed.

### E08 — Membership vs identity
Completeness of the selected set and identity of present members are separate checks.

### E09 — Common-mode declarations
A verifier and specification sharing one mutable declaration is a common-mode trust boundary unless a distinct witness exists.

### E10 — Environment identity contract
For evidence where environment can change meaning, explicitly name:
1. subject identity;
2. authoritative representation (sealed bytes, repository object, checkout form, parsed object, runtime state, semantic replay, etc.);
3. admissible transformations;
4. consequence-bearing environment dimensions;
5. assurance class actually verified;
6. residual dimensions not sealed.

Repository normalization policy is artifact-class relative. A fresh clone/materialization gate exercises a different surface from an existing working tree.

### E11 — Portable evidence surfaces
Prefer machine-readable evidence protocols over parsing human-formatted error/traceback text when evidence is load-bearing.

### E12 — Archive transport
When an archive must cross transport size limits, verify the canonical unsplit archive first, then split below the smallest relevant limit. Record configured part size, part hashes/order, and a deterministic reassembly/verification method. No fixed transport limit is universal SOP law.

`LOCAL_EXECUTION_COMPLETE != ASSISTANT_READBACK_COMPLETE`
`ARTIFACT_REGISTERED != CHAT_RENDERED`
`SUBMITTED != STARTED`
`STARTED != COMPLETED`
`COMPLETED != REGISTERED`
`SEALED_ARTIFACT != SEALED_ENVIRONMENT`
`LOCKED_BYTES != CHECKED_OUT_BYTES`
`NORMALIZED_EQUIVALENCE != SEALED_BYTE_IDENTITY`
`PORTABLE_GATE != WEAKER_GATE`
`SEALED_ENVIRONMENT != REPRODUCED_ENVIRONMENT`
`IDENTITY_POLICY_IS_ARTIFACT_CLASS_RELATIVE`

### E13 — Linear semantic admission before authority transition
A meaningfully readable artifact SHALL receive a complete linear semantic read before promotion, sealing, publication, admission, or load-bearing use. Automated integrity, syntax, test, manifest, hostile-mutation, or other machine checks may support the gate but SHALL NOT replace it.

Exact-hash semantic-read evidence may be reused only when the artifact bytes and governing scope are unchanged. Any semantic mutation requires a new complete read before renewed authority transition.

### E14 — Durable local batch execution
For substantial finite deterministic work, prefer one bounded project-local script, launcher, or job that freezes intended inputs, executes the complete bounded operation, captures environment/timing/job identity/stdout/stderr/exit state locally, produces manifests/hashes/diffs/readback locally, preserves partial/failure state, and emits a compact receipt.

### E15 — Control plane is not the bulk data plane
Do not use chat/action transport as the default bus for large artifacts, long logs, complete manifests, large continuity documents, or intermediate evidence that can remain local and be addressed by path, hash, handle, or compact summary. Prefer:

`LOCAL WORK -> LOCAL EVIDENCE -> COMPACT RECEIPT -> TARGETED EXCEPTION RETRIEVAL`

over:

`LOCAL WORK -> LARGE CONTROL-PLANE STREAM -> RECONSTRUCTION IN CHAT`.

### E16 — Response-loss readback
`CONTROL_PLANE_RESPONSE_FAILURE != LOCAL_EXECUTION_FAILURE`.

If a mutation or batch may have completed locally but the control response is lost, timed out, truncated, disconnected, or ambiguous, inspect the local filesystem/repository/job/log/manifest/artifact state before rerunning. Never blindly repeat merely because the response was lost.

### E17 — Execution-architecture escalation
After the first transport-size, timeout, truncation, or response-loss failure on deterministic batch work, substantially repeating the same bridge-heavy execution pattern without changing architecture is presumptively a process error. Re-route to durable local execution with compact receipt unless the work is genuinely interactive, depends stepwise on newly observed external state, or the local plane lacks required capability.

### E18 — Long-lived process proportionality
Finite batch work SHOULD NOT be implemented as an open-ended service merely because a service mechanism exists. Long-lived processes are appropriate only when persistent service, interactive availability, streaming observation, or an intentionally durable execution environment is actually part of the task.

### E19 — Deterministic publication/release pattern
Where publication or release is deterministic, prefer one bounded local publisher/verifier that performs the consequence-bearing chain, such as:

`INSPECT -> VERIFY REQUIRED GATES -> COPY/GENERATE -> HASH -> ENFORCE EXCLUSIONS -> DIFF -> STAGE -> COMMIT -> PUSH/PUBLISH -> REMOTE READBACK -> WRITE RECEIPT`.

The stages vary by task; the law is execution architecture, not ritualized choreography. Publication is not complete until its task-specific remote or consequence-bearing readback succeeds.

`AUTOMATED_CHECKS != LINEAR_SEMANTIC_READ`
`CONTROL_PLANE_MINIMIZATION != SEMANTIC_READ_SKIPPING`
`CONTROL_PLANE != BULK_DATA_PLANE`


### E20 — Strongest surviving operator-side plane
Under instability, choose the strongest surviving operator-side/local/server plane rather than repeatedly favoring a prettier but fragile orchestration path. Default order is server-native project execution -> direct server-side subprocess/Python -> durable project-local script executed server-side -> ad hoc bridge/chat execution when the stronger routes are unavailable or materially inferior.

Assistant/model-side execution is allowed when materially better or faster for the specific step; the exception SHALL be explicit and convenience alone is insufficient.

### E21 — Incremental and resumable long operations
Where semantics permit, long operations SHOULD checkpoint incremental progress, flush durable state, preserve per-item failures, support resume, and expose clear partial/completion states. Prefer inspectable partial progress over total information loss.

### E22 — Machine execution truth
When machine evidence is available, execution truth is established by consequence-bearing state such as job/execution ID, PID where applicable, stdout/stderr paths, durable outputs, structured summary artifacts, repository/remote state, and task-appropriate hashes/identities. Conversational memory or a transport response does not outrank those surfaces.

`STRONGEST_SURVIVING_PLANE != PRETTIEST_PLANE`
`ASSISTANT_SIDE_CONVENIENCE != MATERIAL_ADVANTAGE`
`EXECUTION_PLANE_FALLBACK != AUTHORITY_BYPASS`
