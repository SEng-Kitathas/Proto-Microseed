# 02 — Canonical Engineering Authority Surface

Each rule retains its listed authority class. These are project-agnostic process defaults/constraints; actual project obligations remain separate inputs.

### C01 — Reality precedence and measurement humility
Classes: `ADMISSIBILITY_CONSTRAINT, QUALIFICATION_RULE`
Intent sets direction; reality outranks narrative. Observations remain mediated evidence rather than reality itself.

### C02 — Composition before invention, without legacy worship
Classes: `DEFAULT, HEURISTIC`
Before adding primitives, search live owners, ancestry, and lawful compositions. Incumbency does not create permanent entitlement.

### C03 — Minimum sufficient embodiment
Classes: `DEFAULT, HEURISTIC, RESEARCH_CANDIDATE`
Among designs satisfying active obligations, minimize incidental causal and maintenance burden while preserving credible trajectory. Minimum does not mean fewest lines.

### C04 — Explicit authority topology
Classes: `QUALIFICATION_RULE, DEFAULT`
Prefer singular logical ownership where one owner suffices; replicated, partitioned, cached, or migrating authority must expose reconciliation/currentness/cutover semantics.

### C05 — Narrow discriminative witnesses
Classes: `DEFAULT, QUALIFICATION_RULE, RESEARCH_CANDIDATE`
Use witnesses that answer the assurance question without gratuitously rebuilding the operation. Independence, coverage, placement, false-positive/negative cost, and authority must be argued.

### C06 — Witness role is part of the guarantee
Classes: `QUALIFICATION_RULE`
Description, monitoring, verification, selection, veto, audit, and execution authority are not interchangeable.

### C07 — Authorship is an engineering plane
Classes: `RESEARCH_CANDIDATE`
Semantic honesty, information scent, ownership/effect/lifecycle legibility, host/domain fluency, change behavior, and craft matter separately from executable correctness. Professional appearance alone has no authority.

### C08 — Source signals carry semantic burden
Classes: `QUALIFICATION_RULE, DEFAULT`
Names, types, comments, reports, tests, metadata, and status labels must not imply stronger guarantees than the artifact establishes.

### C09 — Quality is consequence- and obligation-relative
Classes: `ADMISSIBILITY_CONSTRAINT, HEURISTIC`
The immediate request selects emphasis but does not erase active safety, security, durability, compatibility, custody, contractual, legal, resource, or other standing obligations.

### C10 — Exact proof and probabilistic evidence are different claim classes
Classes: `QUALIFICATION_RULE`
Exact inheritance requires logical sufficiency; bounded probabilistic claims require an explicit error model and scope.

### C11 — Verification preserves evidentiary conditions and completeness
Classes: `QUALIFICATION_RULE`
A verifier must not silently contaminate its specimen and must test required membership/completeness when the claim depends on a selected set.

### C12 — Continuity has replay classes and checkpoint scope
Classes: `QUALIFICATION_RULE`
Read occurrence, locator, retained bytes, replayability, currentness, and as-of-checkpoint truth are different strengths.

### C13 — Hostile survival is bounded evidence
Classes: `QUALIFICATION_RULE, SCAR`
Passing known scars/mutations does not establish unknown-failure robustness. Renew attack axes when claims broaden.

### C14 — Research roughness requires quarantine or requalification
Classes: `DEFAULT, TRIGGER`
Disposable work may trade polish for information speed, but persistence, dependents, example/training use, release, or promotion triggers normal authorship/engineering gates.

### C15 — UNKNOWN does not require paralysis
Classes: `DEFAULT, HEURISTIC`
Keep uncertainty explicit while permitting authorized, reversible, observable, bounded-consequence information-buying actions. Irreversibility raises qualification burden.

### C16 — External contracts constrain host-native lowering
Classes: `ADMISSIBILITY_CONSTRAINT, DEFAULT`
Use host-native representations internally where useful; do not silently change wire, ABI, schema, persistence, interchange, or user-visible consequence semantics.

### C17 — Preserve scar evidence, not dead machinery by default
Classes: `DEFAULT, SCAR`
Keep the discriminator, regression, provenance, or rationale needed to prevent recurrence. Obsolete mechanism needs a current job to remain active.

### C18 — Time as cause is distinct from time as epistemic proxy
Classes: `QUALIFICATION_RULE, SCAR`
Time may be causal or contractual; elapsed time alone does not establish truth or staleness.

### C19 — Optimize within the admissible set
Classes: `ADMISSIBILITY_CONSTRAINT, HEURISTIC`
When lawful choices remain Pareto-incomparable, expose tradeoffs, decision owner, and reopening evidence rather than fabricate one scalar score.

### C20 — Environment identity is an engineering plane
Classes: `QUALIFICATION_RULE, DEFAULT, RESEARCH_CANDIDATE`
For consequence-bearing evidence, distinguish sealed artifact bytes, repository/object identity, checkout/materialization identity, parsed/normalized identity, runtime/toolchain identity, and reproduced-environment identity. Bind only dimensions capable of changing the claim and state residuals explicitly.

### C21 — Observation identity includes time and subject
Classes: `QUALIFICATION_RULE`
A live system or repository is not a static specimen. Bind observations to the exact subject identity and observation boundary.

### C22 — Preserve negative history without fossilizing it
Classes: `DEFAULT, SCAR`
A later mechanism may earn what an earlier state lacked. Preserve the original negative and the later evidentiary event that changed the conclusion.

### C23 — Base-tier engineering metabolism for nontrivial work
Classes: `STANDING_OBLIGATION, TRIGGER`
For nontrivial work, apply the combined functional obligations of PDVER, hostile engineering, Semantic Helix, Attention Reservoir, Loop+, OARR, CSC, and additive AI co-processor strengths. Scale explicit depth and ceremony to consequence, uncertainty, novelty, reversibility, and complexity. Trivial low-consequence work may collapse explicit machinery; nontrivial work may not silently discard the functions merely because named machinery is inconvenient.

`BASE_TIER_FUNCTIONAL_OBLIGATIONS != OPTIONAL_FOR_NONTRIVIAL_WORK`
`METHOD_STACK_REFERENCE != MANDATORY_LINEAR_PIPELINE`
`PROPORTIONALITY != DISPENSATION_FROM_ENGINEERING_DISCIPLINE`

### C24 — Linear human read / semantic admission gate
Classes: `STANDING_OBLIGATION, QUALIFICATION_RULE, TRIGGER`
If an artifact can be meaningfully read, it SHALL receive a complete linear semantic read before it is promoted, sealed, published, admitted, or treated as load-bearing. Automated checks may precede and support the gate; they SHALL NOT substitute for it. Exact-hash semantic-read evidence may be reused only while exact bytes and governing scope remain unchanged. Semantic mutation invalidates reuse for the changed artifact.

`AUTOMATED_CHECKS != LINEAR_SEMANTIC_READ`
`WRITE_COMPLETED != SEMANTIC_GATE_SATISFIED`

### C25 — Durable local execution / control-plane minimization
Classes: `STANDING_OBLIGATION, DEFAULT, TRIGGER, SCAR`
When finite deterministic work can be executed on the local/server work plane, package the substantive work there as one bounded durable operation or job wherever practical. Use the chat/control plane primarily to authorize, dispatch, monitor, inspect exceptions, and receive compact receipts. Large artifacts, manifests, logs, continuity bodies, hashes, and intermediate evidence SHOULD remain local unless targeted retrieval is genuinely needed.

If a control-plane response times out, truncates, disconnects, or otherwise becomes ambiguous after possible mutation, inspect consequence-bearing local state before rerunning. After the first such transport failure on deterministic batch work, substantially repeating the same bridge-heavy architecture without rerouting is presumptively a process error unless a concrete interactive/capability constraint justifies it.

`CONTROL_PLANE_RESPONSE_FAILURE != LOCAL_EXECUTION_FAILURE`
`CONTROL_PLANE_MINIMIZATION != SEMANTIC_READ_SKIPPING`
`CONTROL_PLANE != BULK_DATA_PLANE`

Governing scar: **DO THE WORK WHERE THE STATE LIVES; RETURN ONLY THE EVIDENCE NEEDED TO CONTROL IT.**


### C26 — Operator-side execution preference under instability
Classes: `STANDING_OBLIGATION, DEFAULT, TRIGGER, SCAR`
Prefer the strongest surviving operator-side/local/server execution plane whenever it is available and sufficient. Assistant/model-side execution may lead a step only when it is materially better or faster for that step; assistant-side convenience alone does not satisfy the exception.

When orchestration is degraded, prefer server-native project execution, then direct server-side subprocess/Python, then durable project-local scripts executed server-side, and only then ad hoc bridge/chat execution when stronger routes are unavailable or materially inferior.

Fallback between execution planes does not waive safety, approval, access-control, or authority boundaries.

`STRONGEST_SURVIVING_PLANE != PRETTIEST_PLANE`
`OPERATOR_SIDE_DEFAULT != ASSISTANT_SIDE_PROHIBITED`
`ASSISTANT_SIDE_CONVENIENCE != MATERIAL_ADVANTAGE`
`EXECUTION_PLANE_FALLBACK != AUTHORITY_BYPASS`
