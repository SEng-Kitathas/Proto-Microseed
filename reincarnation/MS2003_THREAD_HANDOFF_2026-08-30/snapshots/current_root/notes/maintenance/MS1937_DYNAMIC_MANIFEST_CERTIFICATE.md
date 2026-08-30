# MS1937 — Dynamic Manifest Safety for Compact Causal Certificates

Status: NON-NOVELTY TRACE-PORTABILITY EXPERIMENT.
Date: 2026-08-29 ET.
No organism source mutation. No canonical promotion.
Sealed organism head during run: MS1924 `6b0f012980a625143ea7137be848d6f13b57325b`.

## Question
Can the MS1936 bitmap-based causal certificate remain safe across inventory/topology evolution, or can an old certificate silently decode against the wrong current ordering/graph?

## Harness / receipt
Harness:
`tools/run_ms1937_dynamic_manifest_certificate.py`
SHA-256:
`c798a8dba531c7b9c1cfb3be70f9165bd6124529054e4046bfeccb3fffd76bde`.

Receipt:
`reports/ms1937_dynamic_manifest_certificate/receipt.json`
SHA-256:
`1d7fc4236e6b31b96cd698dedbed3fc20b81f524de175415c1f9fbc0ec428447`.

Durable job:
`job-02ec0c8291fe`.
Exit 0.
Checks: 10/10 PASS.
Organism worktree clean.

## V1 certificate manifests
Ordered inventory SHA-256:
`5353c14c72624c9a054699010972640f373dfa4e7a109baf27ed3a18760e5328`.

Dependency graph SHA-256:
`f7f75c219e46f1a8282506066aff0b676e0fc1ae098884154e7a2b291186890f`.

Combined inventory+graph manifest size: 765 bytes.

## V2 append-only growth pressure
Added:
- coordination `R8`;
- capabilities `B8-0`, `B8-1`, `B8-2`;
- corresponding dependency edges.

V2 inventory SHA:
`6908acd781525e42e2d94c36f201351105f46edb53fd414b294e84c454cf0ad5`.

V2 graph SHA:
`39084b6c5f11d5d3534385930175f3ebb66907ea05af1808e9ca7094f2e77342`.

Every V1 certificate was REJECTED against the V2 current manifest because the bound inventory digest did not match.

Important observation:
for all four scenarios, naïvely decoding the old bitmap under the append-only V2 ordering happened to produce the same stale closure because old bit positions were preserved.

This is precisely why apparent decode plausibility is insufficient.

Earned scar:
`APPEND_ONLY_INVENTORY_GROWTH_CAN_PRESERVE_OLD_BITMAP_POSITIONS_AND_LOOK_PLAUSIBLE_BUT_MUST_STILL_FAIL_CURRENT_MANIFEST_BINDING`.

## Inventory reordering pressure
The V1 inventory was reversed without changing object identities.
Reordered inventory SHA:
`16a0d58859bd8e62d67fb077ec59a674a861d23d69d9aec76127aa8b170ab928`.

All certificates REJECTED with `INVENTORY_MANIFEST_BINDING_MISMATCH`.

This is required because inventory order is semantic for bitmap decoding.

## Topology-only drift pressure
One dependency edge was changed while retaining the same object inventory.
Topology-drift graph SHA:
`56fe82ee371795ff8155b88b26142594e9f4a4954277966aa189be26699da89e`.

All certificates REJECTED with `DEPENDENCY_GRAPH_BINDING_MISMATCH`.

Thus a matching object inventory is not enough; certificate interpretation is also bound to the exact dependency topology.

## Archive/recovery pressure
Simulated a runtime that had advanced to V2 and retained only current V2 manifests.

Every V1 certificate ABSTAINED with:
`REFERENCED_INVENTORY_MANIFEST_NOT_AVAILABLE`.

When content-addressed V1 inventory/graph manifests were preserved in an archive registry, every old V1 certificate verified and decoded exactly after V2 became current.

Earned recovery statement:
`OLD_CERTIFICATE_DECODE_REQUIRES_EXACT_REFERENCED_ARCHIVED_MANIFEST`.

## Amortized size including manifest cost
Across the four MS1936 scenarios:
- full rich diagnostic projections: 7633 bytes;
- compact certificates: 1428 bytes;
- one shared V1 inventory+graph manifest: 765 bytes;
- certificates + shared manifest: 2193 bytes;
- bytes saved vs full projections: 5440 bytes;
- full / (certificates + manifest) ratio: 3.4806x.

Thus the compression advantage survives even when the one required shared decoding manifest is counted.

## Earned engineering statement
`CONTENT_ADDRESSED_MANIFEST_BINDING_PREVENTS_SILENT_CERTIFICATE_MISDECODE_ACROSS_INVENTORY_OR_TOPOLOGY_DRIFT_UNDER_THIS_FIXTURE`.

Companion laws:
- `CURRENT_MANIFEST != REFERENCED_MANIFEST` => REJECT;
- `REFERENCED_MANIFEST_UNAVAILABLE` => ABSTAIN;
- `ARCHIVED_EXACT_MANIFEST + CERTIFICATE` => lawful historical decode;
- `PLAUSIBLE_BITMAP_DECODE != MANIFEST_VERIFIED_DECODE`.

## What this does NOT prove
- It does not make the compact certificate a replacement for the canonical event stream.
- It does not establish a general serialization standard.
- It does not prove graph-list order should itself be semantically meaningful.
- It does not measure long-horizon manifest-registry growth or garbage-collection policy.
- It does not establish novelty.

## Next Pareto-useful pressure
The graph is semantically an edge set, but MS1936/MS1937 currently hash its serialized list order. This can cause safe-but-unnecessary rejection if only edge ordering changes.

Next question:

> can dependency graphs be canonicalized as semantically unordered edge sets while inventory ordering remains strictly bound, such that harmless graph serialization reorderings verify, real topology changes still reject, and longer dynamic manifest histories retain the compact-certificate size advantage?
