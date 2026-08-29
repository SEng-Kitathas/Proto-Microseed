# MS1933–MS1938 Architecture-Factor Checkpoint

Status: **non-novelty architecture science**
Organism-code baseline during experiments: **MS1924** (`6b0f012980a625143ea7137be848d6f13b57325b`)
Scope: reproducible synthetic fixtures and named baselines only.

These six experiments pressure concrete engineering properties without modifying organism source. Their purpose is to separate properties of **information structure and semantic factorization** from claims about physical distribution, generic architectural superiority, or novelty.

## Reproduction

Run from repository root:

```powershell
python tools/architecture_factor/run_ms1933_invalidation_blast_radius.py
python tools/architecture_factor/run_ms1934_fault_localization.py
python tools/architecture_factor/run_ms1935_authority_coupling.py
python tools/architecture_factor/run_ms1936_causal_trace_certificate.py
python tools/architecture_factor/run_ms1937_dynamic_manifest_certificate.py
python tools/architecture_factor/run_ms1938_graph_canonicalization_lifecycle.py
```

Final public-repo rerun:

| Experiment | Checks | Result |
|---|---:|---|
| MS1933 invalidation blast radius | 10/10 | PASS |
| MS1934 fault localization | 12/12 | PASS |
| MS1935 authority coupling | 10/10 | PASS |
| MS1936 causal trace certificate | 7/7 | PASS |
| MS1937 dynamic manifest safety | 10/10 | PASS |
| MS1938 graph canonicalization/lifecycle | 13/13 | PASS |

The first publication-adaptation run was `INVALID_RUN`, not negative science: the old project-local source-cleanliness guard examined the whole Git worktree and therefore treated newly added publication harnesses as organism dirtiness. The public harness adaptation narrows that guard to `microseed/` and `tests/`, preserving the intended source-integrity check while allowing evidence/tool files to be newly staged.

Final machine-readable receipts are under `evidence/architecture_factor/`.

## MS1933 — dependency-local invalidation blast radius

Named baseline: `GLOBAL_AUTHORIZATION_EPOCH_BASELINE`.

Fixture: 8 independent coordination branches, 3 transitive capabilities per branch, 24 capabilities total, and one shared upstream counterparty.

Measured recheck/stale sets:

- coordination-specific drift: **3/24** local vs **24/24** global-epoch baseline — 8× smaller;
- branch-root capability drift: **3/24** vs **24/24** — 8× smaller;
- leaf capability drift: **1/24** vs **24/24** — 24× smaller;
- shared upstream drift: **24/24** vs **24/24** — no locality advantage when the dependency is actually shared.

Earned under the fixture and named baseline:

`DECLARED_DEPENDENCY_LOCALITY -> BOUNDED_INVALIDATION_BLAST_RADIUS`

Not earned: superiority over every centralized design.

## MS1934 — diagnostic precision follows typed trace information

Compared:

1. `GLOBAL_DECISION_REASON_VECTOR_BASELINE`: final CURRENT/STALE vector plus generic changed-premise type, no ancestry graph;
2. `CENTRALIZED_TYPED_DEPENDENCY_TRACE_BASELINE`: centralized owner receives equivalent typed origin/reason lineage and the same dependency graph.

Microseed uniquely localized every injected root. The flat vector remained ambiguous for a coordination fault (**8 candidate roots**) and a branch-root capability fault (**3 candidates**).

The centralized typed-trace fairness baseline matched Microseed **exactly in all scenarios**.

Earned:

`DIAGNOSTIC_PRECISION_FOLLOWS_EXPLICIT_TYPED_TRACE_INFORMATION_UNDER_THIS_FIXTURE`

`EQUIVALENT_TYPED_TRACE -> EQUIVALENT_FAULT_LOCALIZATION`

Rejected overclaim:

`PHYSICAL_DISTRIBUTION_OF_AUTHORITY_OWNERS_CAUSES_UNIQUE_DIAGNOSTIC_PRECISION`

## MS1935 — unsafe evaluator-fault containment follows premise factorization

Grounding uses actual `conjoin_required_commitments` semantics:

- evaluable NO vetoes;
- YES requires every required premise to license YES;
- otherwise UNKNOWN.

The 45-context matrix covers five program-step premise axes: `NEED`, `PRIORITY`, `INFORMATION`, `FEASIBILITY`, `ROUTE`.

Under an equal one-site stuck-YES mutation budget:

- one independently addressable typed premise fault: **6/45 false authorizations**;
- centralized manager with the same typed submodules: **the same 6/45**, same cases;
- one evaluator shared across all premise types: **40/45 false authorizations**.

Earned:

`INDEPENDENT_PREMISE_FACTORIZATION_BOUNDS_SINGLE_EVALUATOR_UNSAFE_AUTHORITY_FAULT_BLAST_RADIUS_UNDER_THIS_MATRIX`

Rejected overclaim: physical distribution is required. The centralized typed-submodule fairness control matches the local factorization.

## MS1936 — compact hash-bound causal certificate

A read-only certificate binds:

- schema version;
- dependency graph digest;
- ordered inventory digest;
- full relevant event-trace digest;
- opaque reason digest;
- exact origin premise/epoch;
- capability/coordination/counterparty stale-closure bitmaps;
- event count.

It preserved exact origin, final closure, event count, graph/inventory identity, reason binding, full-trace binding, and deterministic bytes in all scenarios.

Payload reduction versus rich diagnostic projection:

- relation fault: **979 → 355 bytes** (2.76×);
- root capability: **764 → 358** (2.13×);
- leaf capability: **740 → 358** (2.07×);
- shared upstream: **5150 → 357** (14.43×).

Aggregate: **7633 → 1428 bytes**.

Earned:

`HASH_BOUND_CAUSAL_CERTIFICATE_CAN_PRESERVE_ROOT_AND_FINAL_CLOSURE_WITH_LOWER_DIAGNOSTIC_PAYLOAD_UNDER_THIS_FIXTURE`

Authority boundary:

`COMPACT_CERTIFICATE != FULL_EVENT_STREAM_FOR_AUDIT_OR_RECOVERY`

The canonical event stream remains audit/recovery authority.

## MS1937 — dynamic manifest safety

An old certificate verifies only against its exact content-addressed inventory and graph manifests.

- exact referenced V1 manifests: VERIFIED;
- append-grown V2 current manifests: REJECTED;
- reordered inventory: REJECTED;
- topology-only drift: REJECTED;
- referenced historical manifest absent: ABSTAIN;
- archived exact V1 manifests after V2 becomes current: VERIFIED.

Important scar: append-only growth can preserve old bitmap positions and make a naïve decode look correct. That is still rejected if the bound manifest is wrong.

Earned:

`CONTENT_ADDRESSED_MANIFEST_BINDING_PREVENTS_SILENT_CERTIFICATE_MISDECODE_ACROSS_INVENTORY_OR_TOPOLOGY_DRIFT_UNDER_THIS_FIXTURE`

`PLAUSIBLE_BITMAP_DECODE != MANIFEST_VERIFIED_DECODE`

Including the one shared decoding manifest, the four certificates used **2193 bytes** versus **7633 bytes** for rich projections — 3.48× smaller.

## MS1938 — canonical graph identity and lifecycle cost

Dependency edges are semantically an unordered set in this fixture; bitmap inventories are semantically ordered.

Graph canonicalization tested:

- exactly two non-empty endpoints;
- reject self/duplicate edges in this fixture;
- normalize endpoints to strings;
- lexicographically sort normalized edges before hashing.

Inventory ordering is **not** normalized because bitmap positions depend on it.

Base/reversed/shuffled raw graph serializations produced different raw hashes but the same canonical graph hash. A real topology change produced a different canonical hash. Duplicate edges were rejected.

Across 12 semantic topology versions × 6 shuffled serializations:

- raw graph identities: **72**;
- canonical graph identities: **12**.

Across 24 actual fault runs:

- rich projections: **117,927 bytes**;
- compact certificates: **8,694 bytes**;
- all 12 canonical graph + ordered inventory manifests: **15,009 bytes**;
- certificates + all manifests: **23,703 bytes**;
- full / compact+manifests ratio: **4.9752×**.

Earned:

`CANONICAL_EDGE_SET_HASH_REMOVES_SERIALIZATION_ORDER_CHURN_WHILE_PRESERVING_REAL_TOPOLOGY_DRIFT_DETECTION`

`BITMAP_INVENTORY_ORDER_REMAINS_SEMANTIC_AND_MUST_STAY_STRICTLY_BOUND`

`COMPACT_CERTIFICATE_ADVANTAGE_SURVIVES_MULTI_VERSION_MANIFEST_COST_UNDER_THIS_HISTORY`

## Combined interpretation

The surviving engineering story is about **explicit information structure and semantic factorization**, not novelty and not physical module placement:

- dependency locality can bound invalidation work;
- typed causal traces can improve diagnostics;
- equivalent centralized typed traces can match those diagnostics;
- independent premise vetoes can contain one evaluator failure;
- equivalent centralized typed submodules can match that containment;
- compact content-addressed causal projections can reduce readback cost without replacing full evidence;
- manifest identity must be exact where ordering/topology is semantic;
- canonicalization should remove only genuinely non-semantic serialization churn.

Novelty posture remains:

`UNKNOWN / NOT_ENTITLED_TO_CLAIM`

These results are engineering measurements under named fixtures/baselines. They do not promote a universal architecture claim.


## Publication-descendant rerun guard

The original experiments were earned on organism-code baseline MS1924 (`6b0f012980a625143ea7137be848d6f13b57325b`). The public repository now also contains the MS1939 proposal/action-indication clarification, so a reproduction harness cannot require every future research descendant to have Git HEAD exactly equal to MS1924 or require `microseed/` and `tests/` to be globally clean before the run. That would make the documented `python tools/architecture_factor/...` reproduction commands fail on a legitimate descendant even when the experiment itself is stable.

The six public harnesses therefore retain the historical ancestry check (`MS1924` must be an ancestor) and now bind a SHA-256 snapshot of all `microseed/**/*.py` and `tests/**/*.py` files immediately before and after each experiment. A run is admissible only when that source/test snapshot is unchanged across the experiment. The receipt records:

- current repository HEAD at run start;
- original experiment head MS1924;
- source snapshot before and after;
- `source_stable_during_run`;
- the experiment-specific scientific checks.

This changes the **run-integrity guard**, not the original experimental baseline or the measured claims.

A final publication-descendant rerun against local MS1939 commit `1dcdbd62e80bde4c41f40cbf79c64a1d35f34502` produced:

| Experiment | Result | Source stable |
|---|---:|---:|
| MS1933 | 10/10 PASS | yes |
| MS1934 | 12/12 PASS | yes |
| MS1935 | 10/10 PASS | yes |
| MS1936 | 7/7 PASS | yes |
| MS1937 | 10/10 PASS | yes |
| MS1938 | 13/13 PASS | yes |

The durable aggregate launcher journal ended with `PUBLIC_ARCHITECTURE_FACTOR_RERUN=PASS`. Its execution supervisor missed the terminal transition and later reported the job as unsupervised; the child process was no longer present and each per-experiment `reports/.../receipt.json` independently reported `all_pass: true` with `source_stable_during_run: true`. The scientific result therefore rests on the per-experiment receipts and durable stdout, not the stale supervisor status.
