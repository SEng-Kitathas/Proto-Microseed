# Project-Local Doctrine — Substantive Pass Seal -> GitHub Publication

Date: 2026-08-29 ET
Authority: explicit operator directive in active thread
Scope: ProtoAGI Microseed research workstream

## Standing directive
At the end of every substantive pass:

`VERIFY -> SEAL LOCAL -> GITHUB PUBLISH -> REMOTE READBACK`

A pass is publication-eligible only after it earns a local seal under the active verification discipline.

## Publication target
Default publication target is the active research branch:
`origin/research/ms1888-replay`.

This standing rule does NOT automatically promote:
- `origin/main`;
- canonical Main-Dev;
- any public novelty or scientific priority claim.

Those remain separate authority/promotion transactions.

## Required publication truth states
Keep distinct:
1. prepared to publish;
2. local seal committed;
3. push submitted;
4. push transport returned success;
5. remote branch readback matches the exact sealed commit.

Only state 5 is `GITHUB_PUBLISHED`.

Preserve:
`PUSH_SUCCESS != REMOTE_MUTATION_UNTIL_READBACK`
`GITHUB_PUBLISHED != MAIN_PROMOTED != CANONICAL_PROMOTED`
`LOCAL_SEAL_REQUIRED_BEFORE_PUBLICATION`

## Failure behavior
If a substantive pass fails verification or cannot earn a local seal:
- do not publish the unsealed candidate;
- report the blocker/failure exactly;
- preserve the last remotely verified sealed research baseline.

If push transport succeeds but readback does not match:
- publication remains UNKNOWN/FAILED;
- do not claim GitHub publication;
- inspect/fix publication transport and re-read the remote ref.

## Credential scar
Current Git for Windows global helper is `helper-selector`, which historically stalled publication. The verified working route is explicit Git Credential Manager:
`git -c credential.helper= -c credential.helper=manager push ...`

Do not treat this implementation detail as permanent doctrine if local Git configuration changes; inspect current credential configuration before future pushes.
