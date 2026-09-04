# 13 — Package, Archive, and Provenance Discipline

## Canonical package rules
- one unique package identity SHALL map to one exact payload tree;
- a changed payload requires a new identity/version or an explicit append-only overlay/supersession relation;
- `FINAL` in a filename is not evidence;
- logical member identities use `/` canonical separators independent of host OS;
- manifest membership and member hashes are separately checked;
- package verifier SHALL avoid writing into the specimen tree;
- release receipt states an assurance ceiling and nonclaims;
- active universal surfaces are scanned for accidental project/person/runtime current-state contamination.

## Ancestry
Historical/parent artifacts MAY be carried under `ancestry/` for provenance. Their presence does not make their historical status/currentness active doctrine.

## Evidence
Qualification artifacts MAY be carried under `evidence/`. Evidence preserves provenance and supports claims; it does not self-promote into process authority.

## Transport splitting
Transport-specific part-size ceilings are configuration, not universal law. Verify canonical archive first; split after verification; hash/order parts; provide deterministic reassembly and post-reassembly hash verification.

`SAME_LOGICAL_ID != SAME_ARTIFACT_IF_BYTES_DIFFER`
`ANCESTRY_PRESENT != ANCESTRY_CURRENT`
`EVIDENCE_PRESENT != EVIDENCE_PROMOTED`
`FINAL_LABEL != VERIFIED_RELEASE`

## Semantic sealing gate
A meaningfully readable release/package payload SHALL pass complete linear semantic reading before sealing or publication. Machine verification remains necessary where applicable but cannot substitute for the semantic gate. Exact-hash read receipts are reusable only while exact bytes and governing scope are unchanged.

## Package-construction execution plane
Deterministic package construction, hashing, manifest generation, archive assembly, and release verification SHOULD be performed as bounded local/server work with durable evidence and compact receipts. Do not stream package bodies or full manifests through a conversational control bridge when local paths/hashes can carry the evidence.


## Import provenance under cross-environment reuse
When moving SOPs, review machinery, or tooling across environments, inspect source surfaces separately, copy only load-bearing materials, name the import source, record the reason for import, and keep imported material under an explicit import/provenance root until deliberately integrated.

`IMPORTED_MATERIAL != PROMOTED_AUTHORITY`
