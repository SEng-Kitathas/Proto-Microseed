# Current Continuity / External Audit Entry Point

## Governing process authority

Before continuity re-entry, read [`GOVERNING_ENGINEERING_SOP.md`](GOVERNING_ENGINEERING_SOP.md). Rahl Engineering Canonical SOP R4.2 is adopted as project engineering/research process authority; continuity pointers remain navigation rather than current-state proof.

## Read this before using any branch named `continuity/*`

The branch `continuity/reincarnation-2026-08-30` inside this repository is a **historical MS2003-era continuity package**. It is intentionally preserved for lineage and is **not the current continuity authority**.

Current operator/recovery continuity is maintained in a separate repository:

`SEng-Kitathas/Proto-Microseed-RD-Continuity`

That repository may not be publicly reachable to every external auditor. Therefore this public repository carries a compact, independently checkable promotion-continuity receipt at:

`evidence/PRELINGUAL_SUBSTRATE_V1_PUBLIC_CONTINUITY_POINTER.json`

The original promotion continuity receipt is mirrored byte-for-content at:

`evidence/PRELINGUAL_SUBSTRATE_V1_PROMOTION_CONTINUITY_RECEIPT.json`

and the exact 911-test stdout is mirrored at:

`evidence/PRELINGUAL_SUBSTRATE_V1_EXACT_SUITE_STDOUT.log`

and a local verifier at:

`tools/verify_public_v1_continuity.py`

Run:

```text
python tools/verify_public_v1_continuity.py
```

The verifier uses only this public Git checkout. It checks:
- canonical V1 commit and tree identity;
- `prelingual-substrate-v1` peeled tag identity;
- NAKED and grounded-language genesis tags and their direct-parent relation to V1;
- current checkout ancestry from V1;
- byte identity of the current `microseed/` subtree to the V1 checkpoint, so later documentation-only maintenance does not silently alter the organism;
- the public receipt's exact promotion claims.

## Exact canonical checkpoint

- canonical label: `PRELINGUAL_SUBSTRATE_V1`
- promotion commit: `0fa41f1ed4cf2fbd341b5f0b63adbc0034d4ac39`
- promotion tree: `88a4014db5838848b1e36b904b96e55b2a5f670e`
- annotated tag: `prelingual-substrate-v1` -> `0fa41f1ed4cf2fbd341b5f0b63adbc0034d4ac39`
- NAKED genesis: `06a3cbd409262b2b948fb8d1c3b96ad78f2b6c91` (direct child of V1)
- grounded-language genesis: `e4e4c961654794d5d2b26eaeadeded2c0075a5df` (direct child of V1)

## External-verification ceiling

The public receipt proves only what can be checked from this repository plus the exact copied receipt fields it exposes. It does **not** make a private/unreachable continuity repository externally inspectable.

Use these distinctions:

`INSPECTED_SURFACE != AUTHORITATIVE_SURFACE`

`OPERATOR_VERIFIED_PRIVATE_CONTINUITY != EXTERNALLY_REACHABLE_CONTINUITY`

`PUBLIC_PROMOTION_RECEIPT != FULL_CONTINUITY_REPOSITORY`

A public auditor may therefore verify the promotion checkpoint, branch genesis, current production-byte identity, and the published promotion verification summary here, while treating deeper private continuity claims as reported unless separately supplied.

## Active post-V1 canonical substrate

Historical `PRELINGUAL_SUBSTRATE_V1` remains immutable at `0fa41f1...`. P1A remains sealed at `prelingual-substrate-v1-p1a-repair`. The active repaired/extended canon is `PRELINGUAL_SUBSTRATE_V1_P1A_N1A`, sealed by `prelingual-substrate-v1-p1a-n1a`.

P1A receipt: `evidence/MS2054_P1A_CANONICAL_REPAIR_PROMOTION_RECEIPT.json`

N1A promotion receipt: `evidence/MS2056_N1A_CANONICAL_PROMOTION_RECEIPT.json`

N1A whole regression: `evidence/MS2056_N1A_WHOLE_SUITE_STDOUT.log`

Promotion remote/fresh-clone readback: `evidence/MS2056_N1A_CANONICAL_PROMOTION_READBACK_RECEIPT.json`

N1A grants only one exact bounded first-unmodeled EFFECT exposure after current qualification, scope, state, complete current value-frame, known-consequence exclusion, and unique-eligibility gates. `UNKNOWN != SAFE`; the warrant is durably consumed before EFFECT and does not create generic exploration authority.

## Active bounded-hierarchy canonical extension

The active repaired/extended canonical substrate is `PRELINGUAL_SUBSTRATE_V1_P1A_N1A_BOUNDED_HIERARCHY_V1`, sealed by annotated tag `prelingual-substrate-v1-p1a-n1a-bounded-hierarchy-v1` after the dedicated MS2065 promotion gate.

Canonical parent before this extension: `0312459457223feb79bb2d0d71ab8387fbc28b1c` (`PRELINGUAL_SUBSTRATE_V1_P1A_N1A` public docs/evidence head).

Exact production delta:
- `microseed/development/epistemic.py`;
- `microseed/runtime/entity.py`.

Promotion receipt: `evidence/MS2065_BOUNDED_HIERARCHY_CANONICAL_PROMOTION_RECEIPT.json`

Promotion whole regression: `evidence/MS2065_BOUNDED_HIERARCHY_PROMOTION_WHOLE_SUITE_STDOUT.log`

The extension promotes only the bounded two-level learned opaque request-target specialization/currentness path. It does not grant recursive hierarchy, semantic Parent/Child authority, arbitrary desired-state construction, generic planning, CFE transfer, or generic exploration authority.

### MS2065 remote/fresh-clone readback
Canonical tag `prelingual-substrate-v1-p1a-n1a-bounded-hierarchy-v1` peels to `ed2cde491962105b0d853b7fd82d8e8b3d81bd8a` and fresh-clone verification passed public continuity verification, the 18-test promotion gate, and `git fsck`. Exact promotion whole-suite evidence blob is 1168 bytes with SHA-256 `282ed8993e301a639cd0acbc13e606a37ff6e7178c9895a1e9ece756f42369bb`. Post-promotion docs/evidence may advance `main` beyond the immutable canonical tag while the Microseed subtree remains `9d63915e9e0396f39d255df474d8c2849a153e3f`.
