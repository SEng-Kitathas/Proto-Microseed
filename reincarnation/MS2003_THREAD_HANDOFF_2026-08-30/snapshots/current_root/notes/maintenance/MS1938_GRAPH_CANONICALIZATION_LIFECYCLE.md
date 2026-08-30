# MS1938 — Graph Canonicalization / Certificate Lifecycle

Status: NON-NOVELTY TRACE-MANIFEST LIFECYCLE EXPERIMENT.
Date: 2026-08-29 ET.
No organism source mutation. No canonical promotion.
Sealed organism head during run: MS1924 `6b0f012980a625143ea7137be848d6f13b57325b`.

## Question
Can dependency graphs be hashed as semantically unordered edge sets so harmless serialization reorderings do not create false manifest drift, while bitmap inventory ordering remains strictly semantic and real topology changes still reject?

Can the compact-certificate size advantage survive a longer multi-version manifest lifecycle?

## Harness / receipt
Harness:
`tools/run_ms1938_graph_canonicalization_lifecycle.py`
SHA-256:
`3697bc2cccf0de381dc888ad1cefc41b445ab825cf2809dc1bc9513ba06c30fc`.

Receipt:
`reports/ms1938_graph_canonicalization_lifecycle/receipt.json`
SHA-256:
`84b54da71e4e82f0b1a90b87fa0e227d6b5921e21ec1e38e774ec3ad85d5efa3`.

Durable job:
`job-cd40a1a9c017`.
Exit 0.
Checks: 13/13 PASS.
Organism worktree clean.

## Canonicalization contract tested
### Dependency graph
- each edge must contain exactly two non-empty endpoints;
- self-edges are rejected in this fixture;
- duplicate edges are rejected rather than silently deduplicated;
- endpoints normalize to strings;
- normalized edge tuples are lexicographically sorted before hashing.

Graph edge order is therefore treated as serialization detail, not semantic identity.

### Inventory
DO NOT sort.

The capability/coordination/counterparty lists are position-bearing manifests used to decode certificate bitmaps. Their order is semantic for that representation and remains strictly hash-bound.

### Certificate v2
- `g` binds the canonical edge-set graph hash;
- `i` remains the exact ordered inventory hash.

## Base edge-order pressure
Raw graph hashes differed under harmless list reordering:
- raw base: `f7f75c219e46f1a8282506066aff0b676e0fc1ae098884154e7a2b291186890f`;
- raw reversed: `fc61b2d6c19b47f1c2783ff6c973c4a87c89ea5a9c0a691694615679c7cea77d`;
- raw shuffled: `15b7da17b79e9a4e7dd42c1cfa9263af79b073db65d6e100b02cd6bb84c87c91`.

After edge-set canonicalization all three produced:
`129d3067c8b2423df3406bebe109e62803f5ba4a266291aa7a301e48804008c3`.

A real topology change (`R3 -> B3-0` replaced with `R3 -> B4-0`) produced canonical hash:
`d9dfd93dc9abe48da73c41eca87b00e670b650cffe6ed12b6b55a54632ea2f07`.

Thus harmless edge order disappears while real topology drift remains visible.

A duplicated edge was rejected with:
`DUPLICATE_EDGE_NOT_ALLOWED`.

## Ordered inventory pressure
Base ordered inventory SHA:
`5353c14c72624c9a054699010972640f373dfa4e7a109baf27ed3a18760e5328`.

Reversed capability/coordination ordering SHA:
`16a0d58859bd8e62d67fb077ec59a674a861d23d69d9aec76127aa8b170ab928`.

The difference is intentionally preserved because bitmap positions depend on that order.

Earned scar:
`CANONICALIZE_ONLY_SEMANTICALLY_UNORDERED_STRUCTURE_NOT_POSITION_BEARING_INVENTORIES`.

## Multi-version lifecycle pressure
Built 12 semantic topology versions from 8 through 19 branches.
Each branch carries one coordination relation and three transitive capabilities.

For every semantic version:
- generated 6 independently shuffled graph-list serializations;
- every raw ordering produced a distinct raw serialized graph hash;
- all 6 canonicalized to one semantic graph hash;
- ran one narrow coordination fault and one broad shared-counterparty fault through the actual Microseed fixture;
- generated compact certificate v2 for both faults.

Totals:
- semantic graph versions: 12;
- observed graph serializations: 72;
- raw distinct graph hashes: 72;
- canonical distinct graph hashes: 12.

Raw list-order hashing would therefore create 6x graph-manifest identity churn under this observation pattern.

## Lifecycle storage measurements
Raw-order-churn graph archive:
59,310 bytes.

Canonical graph archive:
9,885 bytes.

Ordered inventory archive across all 12 versions:
5,124 bytes.

Raw graph + inventory archive:
64,434 bytes.

Canonical graph + inventory archive:
15,009 bytes.

Raw-order graph churn / canonical graph archive ratio:
6.0x.

## Certificate lifecycle across 24 actual fault runs
12 versions × 2 actual Microseed faults/version = 24 runs.

Full rich diagnostic projection bytes:
117,927.

Compact certificate bytes:
8,694.

All 12 version manifests (canonical graphs + ordered inventories):
15,009 bytes.

Certificates + every version manifest:
23,703 bytes.

Bytes saved versus full projections even after charging all manifests:
94,224 bytes.

Compression ratio:
4.9752x.

Every individual narrow and broad fault certificate remained smaller than its corresponding rich projection.

## Earned engineering statements
`CANONICAL_EDGE_SET_HASH_REMOVES_SERIALIZATION_ORDER_CHURN_WHILE_PRESERVING_REAL_TOPOLOGY_DRIFT_DETECTION`.

`BITMAP_INVENTORY_ORDER_REMAINS_SEMANTIC_AND_MUST_STAY_STRICTLY_BOUND`.

`COMPACT_CERTIFICATE_ADVANTAGE_SURVIVES_MULTI_VERSION_MANIFEST_COST_UNDER_THIS_HISTORY`.

## Interpretation
The certificate/manifests now survive the major synthetic pressures identified by MS1936/MS1937:
- compact root/closure projection;
- full-trace hash binding;
- ordered-inventory binding;
- topology binding;
- archived historical decode;
- current-manifest mismatch rejection;
- harmless graph serialization reorder;
- real topology drift;
- multi-version manifest/archive cost.

This is enough to treat the compact-certificate concept as an earned **project-control/readback design candidate**, but not as an organism feature and not as a replacement for canonical event history.

Any implementation outside the experiment should preserve:
- full event/history authority;
- content-addressed archived manifests;
- fail-closed manifest lookup;
- canonicalization only where semantics are genuinely unordered;
- explicit certificate schema/version binding.

## Campaign stop
MS1933–MS1938 now cover the selected architecture-factor questions with named baselines and fairness controls:
- invalidation blast radius;
- diagnostic precision;
- evaluator fault coupling;
- compact causal readback;
- dynamic manifest safety;
- graph canonicalization/lifecycle overhead.

Additional synthetic variants are now likely diminishing-return without a concrete implementation target.

Recommended next action:
checkpoint these engineering findings and select either:
1. a project-control implementation of compact certificate/readback surfaces (NOT organism code), if thread-life/operational efficiency is the objective;
2. an explicit EQUIPPED/FEDERATED experiment-warrant build objective;
3. a new blind external technical challenge.
