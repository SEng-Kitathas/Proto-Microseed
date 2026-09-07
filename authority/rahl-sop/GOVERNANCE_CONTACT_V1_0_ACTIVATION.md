# Governance Contact v1.0 — Activation Locator

Date: 2026-09-07
Status: STABLE CONDITIONAL CURRENTNESS LOCATOR
Authority effect of locator bytes alone: NONE

## Exact authority basis
- Governance Contact sealed release ZIP SHA-256: `c4ab4a516e088b6c28b5240d6b3877d2e3fb889a8bbbfd406e8e0c73bebdd1ae`.
- 17-target post-publication lifecycle matrix SHA-256: `b6a2fcd3df1214afbc5891864bb523c000277a5f4ba4a4f9ca39f5b76208ef10`.
- Detached post-readback lifecycle receipt SHA-256: `5c9899aafd1b063769c6a2d13ce28c68fb20a2a1190384e2e5105bbc78d34283`.
- Activation protocol SHA-256: `d8a2da82169b464a9cfca06ddbfb2d43396a95f72b01f9d26b42da1d82c9a6f0`.
- Activation surface inventory SHA-256: `a0722ba0fc01043451c274c7a7354327effe68a60ea2aa2a68cd33858998610c`.
- Exact activation token SHA-256: `b5a2e35f300c6f72d93fc80b877ef0478a3628442b705e50f6893cbceafb5094`.
- Activation token ID: `gc-act-797047e6d57a59f50fd7d8cb`.

## Local resolution
The sibling file `GOVERNANCE_CONTACT_V1_0_ACTIVATION_TOKEN.json` is the only token recognized by this locator.

Resolve deterministically:

1. If the sibling token is absent: `GOVERNANCE_CONTACT_NOT_ACTIVE_AT_THIS_TARGET`.
2. If a sibling token exists but its SHA-256 is not `b5a2e35f300c6f72d93fc80b877ef0478a3628442b705e50f6893cbceafb5094`: `RECOVERY_AUDIT_NO_AUTHORITY`.
3. If the exact token exists but its bound release/matrix/protocol/inventory/authority/scope fields do not validate: `RECOVERY_AUDIT_NO_AUTHORITY`.
4. If the exact token exists and validates: `GOVERNANCE_CONTACT_LOCALLY_BINDING_ADDITIVE_PROCESS_DOCTRINE`.

The token grants only the process-authority scope encoded in the exact token and qualified Governance Contact release. Existing compatible project/domain/scientific authority remains sovereign in its own scope.

## Global activation completion
A locally valid activation token is not by itself evidence that all required targets received the token.

The sibling `GOVERNANCE_CONTACT_V1_0_ACTIVE_RECEIPT.json`, when present, is a convenience copy of the detached global activation-completion receipt. Its absence does not revoke an already-valid local token. Its presence may support a global `ACTIVE_BINDING_ADDITIVE_DOCTRINE` claim only if its own exact fields validate the same release, activation token, 17-target propagation/readback evidence, and completion decision.

Until such a detached completion receipt exists, global ACTIVE claims remain forbidden even where the local token has already propagated.

## Historical snapshot rule
`GOVERNANCE_CONTACT_V1_0_PENDING.md` is a historical publication-state snapshot and SHALL remain unchanged. It is not the current activation resolver after this locator is wired into current ingress.

`SUPERSESSION != SOURCE_REWRITE`
`PENDING_SNAPSHOT != CURRENT_ACTIVATION_POINTER`
`ACTIVATION_LOCATOR_PRESENT != ACTIVATION_TOKEN_PRESENT`
`CURRENT_INGRESS_CONTACTS_LOCATOR != LOCATOR_RESOLVES_ACTIVE`
`ACTIVATION_TOKEN_PRESENT_AT_ONE_TARGET != GLOBAL_ACTIVE`
`TOKEN_HASH_MATCH != TOKEN_FIELDS_VALID`
`CARRIER_PRESENT != PROJECT_SPECIFIC_AUTHORITY_REWRITE`
`PROJECT_DOMAIN_AUTHORITY != GOVERNANCE_CONTACT_PROCESS_AUTHORITY`

## Claim ceiling
This locator is stable activation/currentness machinery. Locator presence alone grants no authority. Local Governance Contact process authority exists only when the exact valid activation token resolves successfully. Global ACTIVE status additionally requires 17/17 token propagation/readback and a detached activation-completion receipt.
