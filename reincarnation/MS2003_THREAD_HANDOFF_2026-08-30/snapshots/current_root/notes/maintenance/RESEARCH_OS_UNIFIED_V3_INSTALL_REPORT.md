# Research OS Unified V3 — Intake / Verification Report

Date: 2026-08-27
Mode: MERGE
Role: R1 Conservative Auditor → R3 Evidence Synthesizer

## Source
Attachment: `RESEARCH_OS_COLD_START_UNIFIED_V3_2026-08-27.zip`
Exact attachment SHA-256: `83b1d4e302e2943d695e4010bfd7c309c573c1deee94a8aa09b05ed3f0cd4d87`
Size: 205,083 bytes
Files in ZIP excluding directories: 122 total; manifest covers 121 non-manifest members.
Manifest schema: `research-os.unified-cold-start.manifest.v3`
Scar rule count: 377.

The exact ZIP was not found in user-side `C:\Users\ancal\Downloads`. Ngrok server cannot directly read ChatGPT `/mnt/data`. Therefore package-byte inspection and runtime verification used the attachment side as a necessary file/context-plane bridge. Exact executable ZIP/runtime is not claimed server-copied.

## Authority
Machine profile authority: `process_only_no_project_state`.
`project_context_installed: false`.
No Microseed project state or canonical authority is supplied by the package.

## Package verification
Bounded report group `integrity`:
- `verify_manifest.py`: PASS, exit 0
- `package_hygiene.py`: PASS, exit 0

No package-integrity failure observed in these gates.

## Method-kernel bounded verification
- OARR neutral validator: PASS
- OARR hostile lab: PASS
- HSP method validator: PASS
- PDVER import: PASS
- mode/role contract: PASS
- CSC shipped unittest wrapper: UNKNOWN_INCOMPLETE under 10s on attachment host

The CSC wrapper produced one test progress dot and then stalled because its first test spawns a regular `sys.executable` child. This host injects an unrelated spreadsheet/artifact-tool Python startup hook. Direct site-disabled `run_csc_self_audit.py` subsequently PASSed, and the `enforcement_authority == NONE` contract PASSed.

## Composition/runtime bounded verification
Direct site-disabled constituents: 17/17 PASS:
1. CSC self-audit
2. CSC authority ceiling
3. Evidence Bus append 1
4. OARR neutral slice
5. Evidence Bus append 2
6. Semantic Helix
7. Evidence Bus append 3
8. Attention Reservoir add
9. Attention Reservoir select
10. Evidence Bus append 4
11. Evidence Bus verify
12. Isomorphic Predator
13. Distillation Engine
14. campaign pass gate
15. continuity append
16. continuity shadow
17. continuity pair verify

Shipped HSP orchestrator wrapper: UNKNOWN_INCOMPLETE under 10s on this host.
Shipped unified demo wrapper: UNKNOWN_INCOMPLETE under 10s on this host.
Reason localized: both wrappers spawn regular `sys.executable` children, re-entering the host site-startup hook. Their direct site-disabled constituents PASS. Do not call wrappers PASS from constituent status.

Monolithic `verify_all.py`: UNKNOWN_INCOMPLETE on attachment host. Per V3 verifier law, do not increase timeout until green without localization and do not launder constituent PASS into integrated PASS.

V3 package-provided `RELEASE_VERIFICATION.md` reports fresh-extraction integrated PASS in its release environment. Treat this as package-provided release evidence, not independent local integrated verification.

## Host-environment scar
Observed attachment-host Python startup interference from unrelated spreadsheet/artifact-tool warmup. This is a harness/environment portability issue for wrappers that recursively spawn bare `sys.executable`.

Classification:
- package manifest/hygiene: VERIFIED within local attachment scope
- direct runtime constituents: VERIFIED within bounded site-disabled attachment scope
- shipped integrated wrappers on this host: UNKNOWN_INCOMPLETE / ENVIRONMENT_FAILURE candidate
- universal V3 correctness: UNKNOWN
- Microseed project correctness from V3: UNKNOWN / not claimed

## Collaborator execution preference recorded
Prefer bounded groups and durable execution that leaves logs/reports/receipts. Inspect after completion. Avoid long synchronous in-process hooks or open-ended waits unless they materially improve fidelity or alternatives are noticeably worse/unavailable.

## Server persistence
Server-side doctrine snapshot created: `state/doctrine_snapshot/RESEARCH_OS_UNIFIED_V3_DOCTRINE.md`.
This report created under `notes/maintenance/RESEARCH_OS_UNIFIED_V3_INSTALL_REPORT.md`.

## Open installation seam
The full V3 executable source tree and exact ZIP are not server-copied because the attachment bridge exposes no direct binary-ingress route to the ngrok filesystem. When the exact ZIP becomes visible on the user/server side, run server-local manifest verification, fresh extraction, bounded wrapper/constituent verification, and compare exact SHA before calling V3 fully installed server-side.