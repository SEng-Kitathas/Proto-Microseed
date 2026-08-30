# GitHub Publication Evidence — Proto-Microseed

Date: 2026-08-28 ET.
Target: `https://github.com/SEng-Kitathas/Proto-Microseed.git`
Visibility observed before push: PUBLIC.

## Pre-push audit
Local repo: `research_ms1888_replay`.
Current sealed experimental head: `6b0f012980a625143ea7137be848d6f13b57325b` (MS1924).
Local active branch: `research/ms1888-replay`.
Baseline tag: `ms1887-exact` -> `2e73101001b00b59d284855fe5c9a4f55b2486c7`.

Public-history hygiene before push:
- current tracked files: 778;
- current tracked secret-pattern hits: 0;
- current tracked files >=5 MiB: 0;
- historical blobs inspected: 814;
- total historical blob volume ~9.7 MiB;
- historical private-key / GitHub-token / OpenAI-key / AWS-key signature hits: 0;
- no large historical model/blob payload was found in Git history.

No README or LICENSE was invented during publication. No source/docs were changed merely to make the first public push look polished.

## Remote setup
Local `origin` configured as:
`https://github.com/SEng-Kitathas/Proto-Microseed.git`

GitHub CLI itself was not logged in, but Windows Git Credential Manager had a stored GitHub HTTPS credential. Credential bytes were never printed, embedded in the remote URL, or written into the repository.

Two early helper routes were abandoned safely:
- GUI/helper selection route hung before transfer;
- a first temporary askpass shim was malformed and was cleaned; no remote refs were created.

A later authenticated push reached GitHub but received a transient remote HTTP 500. Remote readback after that failure still showed no refs.

## Successful push
Durable job: `job-1a7db5a54d5b`.
Return code: 0.

Published refs:
- local HEAD -> remote `main`;
- local `research/ms1888-replay` -> remote `research/ms1888-replay`;
- local tag `ms1887-exact` -> remote tag `ms1887-exact`.

Exact remote readback after push:
- `refs/heads/main` -> `6b0f012980a625143ea7137be848d6f13b57325b`;
- `refs/heads/research/ms1888-replay` -> `6b0f012980a625143ea7137be848d6f13b57325b`;
- `refs/tags/ms1887-exact` -> `2e73101001b00b59d284855fe5c9a4f55b2486c7`.

Local worktree readback after push: clean.

## Authority / publication boundary
The GitHub publication does not alter canonical authority:
- Canonical Main-Dev remains MS1527.
- Public repository `main` currently points to the latest sealed experimental research descendant MS1924.
- `research/ms1888-replay` is also published explicitly so the research lineage is not hidden by the convenience `main` ref.
- `ms1887-exact` preserves the exact recoverable research baseline tag.

The publication is a transport/publication event, not a canonical promotion event.
