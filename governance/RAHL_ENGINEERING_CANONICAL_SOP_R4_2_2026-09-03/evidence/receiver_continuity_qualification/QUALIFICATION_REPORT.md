# Receiver Continuity Envelope v0.1 — Qualification Report

Status: **QUALIFIED ISOLATED CANDIDATE; LIVE PROMOTION NOT PERFORMED**
Date: 2026-09-02

## Donor intake boundary

The user supplied donor material proposing external/local session state and continuity reinjection through tool returns after chat-context loss. The architectural mechanism was admitted as donor signal. The donor's claims about the exact implementation of OpenAI front-end safety filtering, whether specific message blocks are removed from model working memory, and whether tool/system payloads receive categorically different filtering are **not verified here and are not required by this candidate**.

The candidate instead adopts the presentation-agnostic invariant:

> Locally persisted project state must remain recoverable even when the conversational/readback presentation surface is missing, blocked, compacted, stale, or otherwise unreliable.

This is continuity hardening, not a safety-filter bypass.

## Source/currentness

- Live receiver source root: `C:\Users\ancal\Desktop\PCMMAD_RECEIVER_V29_NATIVE_PROTOCOL_RC1\PCMMAD_receiver\baseline\pcmmad_receiver`
- Frozen isolated source files: **60**
- Frozen source tree SHA-256: `36b57da825f993b33ccf5fd1ebe755bb65d66a9a6f854ec43f4eb1f652e2b8f7`
- Pre-seal live-source recheck: **exactly the same tree hash**; no live drift detected.
- Live receiver mutation by this work: **NO**.

## Embodiment

### New module
`continuity_envelope.py`

Builds a compact read-only `pcmmad.continuity-envelope.v1` from the existing local project surfaces:
- Live Shadow
- Current State
- Next Steps
- Design Thread Stream pointer/size
- append-only runtime protocol status/continuity when actually initialized
- optional session identity

Envelope fields include:
- exact project/session identity when available
- state fingerprint
- explicit protocol initialization/ledger state
- file-derived `active_mode_hint` only when appropriate
- bounded resume summary and open loops
- anchor paths/hashes
- compact and server-native rehydration instructions
- explicit plane note that assistant readback/chat rendering are not server-observable

### Native lab router
`ToolResultEnvelope` now has an optional `continuity` field. Project-scoped `/lab/dispatch` tool results use the same continuity builder.

### Compact/direct action surface
`app_factory` installs one authenticated `after_request` bridge. Any JSON response associated with an authenticated project-scoped request receives the same envelope. This covers the compact imported route surface without editing every route individually.

If an authenticated `/project/*` or `/lab/*` request escapes as an unstructured non-JSON error, the middleware emits a generic JSON error plus continuity. Server traceback logging remains intact.

### Security boundary
The middleware revalidates the configured `X-GitHome-Key` before adding continuity. An unauthenticated 401 was directly verified to contain **no continuity data**.

No fake `[SYSTEM]` text, role impersonation, or stealth prompt injection is used. Continuity is ordinary structured response metadata.

## Authority correction earned during qualification

The HSP project has no initialized runtime-protocol ledger. `protocol_status(..., initialize=False)` therefore exposes the protocol model's default `DISCUSSION` value even though persisted HSP continuity says BUILD-COMMIT.

Candidate correction:
- protocol initialization is explicit;
- uninitialized default mode is **not** presented as active authority;
- locally persisted mode is exposed only as separately labeled `active_mode_hint`.

This prevents a default placeholder from silently overriding stronger persisted state.

## Verification

### Candidate regression suite
`tests/test_continuity_envelope.py`: **11/11 PASS** in 0.329 s.

Covered:
1. direct and nested project/session extraction;
2. optional ToolResultEnvelope continuity serialization;
3. bounded recovery content from real project anchors;
4. uninitialized protocol default cannot claim active mode authority;
5. fingerprint changes when Live Shadow changes;
6. envelope reads do not mutate the Live Shadow;
7. authenticated direct project action receives continuity;
8. unauthenticated action does not leak continuity;
9. native lab dispatch receives the same top-level envelope;
10. structured 404 retains continuity;
11. the known unhandled ranged-read `NameError` is normalized from HTML 500 into generic JSON **with continuity**;
12. serialized envelope size remains below the 3,000-character test ceiling.

(The suite contains 11 test methods; several methods assert multiple bullets above.)

### Compile
Full isolated source `python -m compileall -q .`: **PASS**.

### Scar replay
Known receiver ranged-read defect:
- route exception: `NameError: name 's' is not defined`
- HTTP status: 500
- before candidate: unstructured HTML response, no continuity
- candidate: `UNSTRUCTURED_SERVER_ERROR` JSON plus valid `state_fingerprint` and rehydrate instructions

Known missing-file structured error:
- HTTP status: 404
- `NOT_FOUND`
- continuity preserved

### Authentication
- `/project/info`, valid API key: continuity present
- `/project/info`, no API key: 401 and continuity absent

### Read-side nonmutation
Snapshot covered `state`, `continuity`, and `system/protocol` surfaces.
- digest before 100 envelope builds: `82de563d3159de52452f075801e991a3fea4e449a658f6ed0e57fcb525e8755b`
- digest after 100 envelope builds: same
- file size/mtime/hash rows identical: **YES**

### Deterministic concurrency
256 continuity builds through a 32-worker thread pool:
- unique fingerprints: **1**
- all same: **YES**
- elapsed: 719.18 ms
- effective average: 2.809 ms/call

### Sequential cost
200 warmed HSP envelope builds:
- total: 759.069 ms
- mean: **3.795 ms/call**
- serialized HSP envelope: approximately **2,343 characters**

## Diff surface

Changed existing files:
- `app_factory.py`
- `control_plane_models.py`
- `lab_tools.py`

Added:
- `continuity_envelope.py`
- `tests/test_continuity_envelope.py`

Missing source files: **0**.

Patch:
- `CONTINUITY_ENVELOPE_V0_1.patch`
- SHA-256 `59fef362ce36896a20379d1514ae865aad547b3ce57705fad9b8add382bc106a`
- 24,649 bytes
- generated diff accounting: +592 / -1 lines, dominated by new module and tests

## What this candidate deliberately does not do

- Does not claim OpenAI safety filters delete particular model-context tokens.
- Does not claim structured tool returns are immune to filtering or display loss.
- Does not bypass or weaken safety policy.
- Does not automatically write continuity on every read; existing state writers remain authoritative.
- Does not infer assistant readback or chat-render success from local server state.
- Does not make MCP a dependency; the receiver already has native rehydration and an MCP manifest capability, but this recovery path works without assuming an MCP client will be invoked.
- Does not mutate the live receiver.

## Promotion posture

Candidate is technically qualified for a separate PROMOTION review. A promotion pass should still verify:
1. current live tree remains identical to the frozen source;
2. exact patch application scope;
3. imported OpenAPI/Custom GPT response compatibility if any downstream client uses strict response schemas;
4. live smoke on direct project action, native lab dispatch, structured failure, and unstructured failure;
5. rollback path and remote/source checkpoint before restart.
