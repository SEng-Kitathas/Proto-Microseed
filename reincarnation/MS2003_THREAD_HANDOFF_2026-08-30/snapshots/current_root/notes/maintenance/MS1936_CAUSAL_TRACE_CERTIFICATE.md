# MS1936 — Compact Causal Invalidation Certificate

Status: NON-NOVELTY TRACE-EFFICIENCY EXPERIMENT.
Date: 2026-08-29 ET.
No organism source mutation. No canonical promotion.
Sealed organism head during run: MS1924 `6b0f012980a625143ea7137be848d6f13b57325b`.

## Question
Can Microseed's rich invalidation event trace be projected into a compact, deterministic, hash-bound certificate that preserves exact root localization and final stale closure while materially reducing diagnostic payload?

The certificate is explicitly a read-only projection. It does NOT replace the canonical event stream for audit/recovery.

## Harness / receipt
Harness:
`tools/run_ms1936_causal_trace_certificate.py`
SHA-256:
`c2f3db89d32c0872fef222f26251691b92655d2df778aff9de516ca071fd1f5a`.

Receipt:
`reports/ms1936_causal_trace_certificate/receipt.json`
SHA-256:
`e8b1370772db9ac8124614d44756b3c54130d3589aed2894a901b06ade97e660`.

Durable job:
`job-c8423378f1a3`.
Exit 0.
Checks: 7/7 PASS.
Organism worktree clean.

## Static fixture bindings
Reused the 8-branch / 24-capability MS1933 fixture.

Inventory SHA-256:
`5353c14c72624c9a054699010972640f373dfa4e7a109baf27ed3a18760e5328`.

Dependency graph SHA-256:
`f7f75c219e46f1a8282506066aff0b676e0fc1ae098884154e7a2b291186890f`.

## Certificate v1 fields
Compact canonical JSON fields:
- `v`: certificate version;
- `g`: dependency graph SHA-256;
- `i`: inventory/order manifest SHA-256;
- `t`: SHA-256 of the full relevant invalidation-event trace;
- `r`: SHA-256 of the opaque originating reason;
- `o`: `[origin premise type, origin ID, origin epoch-or-null]`;
- `c`: hex bitmap over ordered capability inventory;
- `q`: hex bitmap over ordered coordination inventory;
- `p`: hex bitmap over ordered counterparty inventory;
- `n`: relevant invalidation-event count.

The bitmaps make the closure compact; the inventory digest binds their ordering.
The trace digest binds the compact projection back to the full canonical event evidence.

## Verification requirements
Every scenario required all of:
- exact originating premise reconstruction;
- exact stale capability closure;
- exact stale coordination closure;
- exact stale counterparty closure;
- exact event count;
- graph digest binding;
- inventory digest binding;
- full trace digest binding;
- reason digest binding;
- deterministic certificate bytes;
- certificate smaller than rich full diagnostic projection.

All checks passed for all four scenarios.

## Measured results

### Coordination-specific fault
Full diagnostic projection: 979 bytes.
Certificate: 355 bytes.
Compression: 2.7577x.
Saved: 624 bytes.

### Branch-root capability fault
Full: 764 bytes.
Certificate: 358 bytes.
Compression: 2.1341x.
Saved: 406 bytes.

### Leaf capability fault
Full: 740 bytes.
Certificate: 358 bytes.
Compression: 2.0670x.
Saved: 382 bytes.

### Shared counterparty fault
Full: 5150 bytes.
Certificate: 357 bytes.
Compression: 14.4258x.
Saved: 4793 bytes.

### Aggregate
Total full projection: 7633 bytes.
Total certificates: 1428 bytes.
Total saved: 6205 bytes.
Mean per-scenario compression ratio: 5.3461x.

Broad shared drift produced the largest absolute saving because the canonical trace intentionally records the complete causal fan-out.

## Earned engineering statement
`HASH_BOUND_CAUSAL_CERTIFICATE_CAN_PRESERVE_ROOT_AND_FINAL_CLOSURE_WITH_LOWER_DIAGNOSTIC_PAYLOAD_UNDER_THIS_FIXTURE`.

Non-replacement law:
`COMPACT_CERTIFICATE != FULL_EVENT_STREAM_FOR_AUDIT_OR_RECOVERY`.

## Interpretation
MS1936 demonstrates that the operator/model does not need to repeatedly materialize the full causal event stream merely to answer bounded questions such as:
- what root premise changed?
- which capabilities/relations are stale now?
- which graph/inventory version was this result bound to?
- which full trace must be consulted for audit?

The certificate can act as a compact control/readback surface while the event stream remains canonical authority.

This directly supports the PCMMAD thread-life/local-first doctrine: preserve full evidence server-side, return compact bound summaries when full detail is unnecessary.

## Limitation / next discriminator
Certificate v1 depends on an externally known ordered inventory manifest for bitmap decoding.
The inventory digest detects ordering drift, but a consumer must fail closed rather than decoding the bitmap against whatever current inventory happens to exist.

Next question:

> can the certificate remain safe and useful across dynamic inventory/topology evolution by binding to content-addressed archived manifests, rejecting mismatched current manifests, and decoding successfully only with the exact referenced manifest?

No production adoption is earned until that dynamic-manifest pressure passes.
