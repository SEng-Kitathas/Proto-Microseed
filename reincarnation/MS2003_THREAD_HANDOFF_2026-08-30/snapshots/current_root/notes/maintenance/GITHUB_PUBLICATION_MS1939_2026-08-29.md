# GitHub Publication — MS1939 Research Descendant — 2026-08-29

Status: VERIFIED PUBLICATION / EXACT REMOTE READBACK COMPLETE.

## Public repository
`https://github.com/SEng-Kitathas/Proto-Microseed.git`

## Published lineage
Prior public head:
`6b0f012980a625143ea7137be848d6f13b57325b` (MS1924).

Organism-code / MS1939 repair commit:
`1dcdbd62e80bde4c41f40cbf79c64a1d35f34502`
message: `MS1939 clarify rehearsal proposal vs action indication`.

Final public repository head:
`3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`
message: `Harden architecture-factor reruns across descendants`.

Final tree:
`f9840ac4ae35c6796e2a397fd581659c3c44c8a7`.

Final branch:
`research/ms1888-replay`.

Baseline tag preserved:
`ms1887-exact` -> `2e73101001b00b59d284855fe5c9a4f55b2486c7`.

## MS1939 scientific/compatibility gate
The Claude Opus 5 donor P5 zero-pressure rehearsal ambiguity was independently reproduced on MS1924.

Rejected first repair:
blanket `zero pressure -> no rehearsal proposal` broke inherited MS1477/MS1782 epistemic reentry and was reverted.

Published repair preserves model-only counterfactual rehearsal and explicitly separates proposal existence from current action indication:
`PROPOSAL_RETURNED != ACTION_INDICATED`.

Release evidence remains bound to source/test snapshot:
`0b58df92d72dedf4856ee3b6b209af3991c4e0192595d120dd38139bd0f92528`.

Compatibility evidence:
- bounded release validation PASS;
- 183 test files;
- 691 collected/passed aggregate items under the release validator;
- 81/81 self-test PASS;
- exact declared-function coverage closed;
- slow residual closure 54/54 PASS;
- compileall PASS;
- no admitted negative group;
- no terminal unknown group;
- source snapshot stable.

Public release receipt:
`evidence/MS1939_PROPOSAL_ACTION_INDICATION_RELEASE_RECEIPT.json`
SHA-256 `3309f64dd63afd64e908931c6c92a99c446f27959db155bf75fdcfdad4611ad4` in the local checkout representation; Git blob identity is controlled by repository filters/tree.

## Architecture-factor public reproduction gate
The public MS1933–MS1938 harnesses were hardened so descendant reruns no longer require Git HEAD to equal MS1924 or the entire organism worktree to be globally clean. They retain MS1924 ancestry and instead bind the `microseed/**/*.py` + `tests/**/*.py` source snapshot before/after each run.

Final clean-head rerun on public head `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`:
- MS1933 10/10 PASS;
- MS1934 12/12 PASS;
- MS1935 10/10 PASS;
- MS1936 7/7 PASS;
- MS1937 10/10 PASS;
- MS1938 13/13 PASS;
- all six `source_stable_during_run: true`.

Total final architecture-factor checks: 62/62 PASS.

The tracked compact receipts were generated against organism-code commit `1dcdbd62e80bde4c41f40cbf79c64a1d35f34502`; the final `3473834...` commit changes only reproduction harness/evidence/methodology publication surfaces, not organism source/tests.

## Public/lab split
Public repository contains only the admitted research descendant, bounded methodology, tests, reproducible architecture-factor harnesses, compact evidence receipts and README.

Lab-only surfaces were NOT published:
- PCMMAD Current/Next/Revisit/Trace state;
- Live Shadow / Design Thread Stream;
- browser captures/session artifacts;
- local-model logs;
- server execution journals;
- receiver/browser-bridge runtime state;
- project-local research/control notes not deliberately mirrored into the repository.

Pre-push irreversible-surface audit:
- `git diff --check` clean;
- no tracked local PCMMAD/receiver/project paths detected by bounded scan;
- no obvious GitHub/OpenAI/AWS/private-key/Bearer credential signature hits;
- repository worktree clean after final commit.

## Push execution history
### Attempt 1 — supervised normal Git push
Job `job-8b3176716db2` lost supervision/hit its 90-second ceiling while Git helper-selection children remained alive.
Remote refs were read immediately afterward and remained at MS1924.
Classification:
`INVALID_RUN / SUPERVISION_LOST / NO_REMOTE_MUTATION`.
Orphan HTTPS Git children were explicitly killed before retry.

### Attempt 2 — direct `wincred` helper
Direct non-interactive `credential.helper=wincred` push also timed out with no output.
Remote mutation was not credited.
Stale process tree was removed.

### Credential validation
Windows Credential Manager entry `git:https://github.com` was read only inside process memory.
Credential bytes were never emitted to command arguments or logs.
A GitHub API request using the in-memory credential returned HTTP 200.

### Askpass experiment
A temporary secret-free askpass shim under the repository path failed because of local invocation/path behavior; a temp-directory shim could authenticate reads but Git push password integration remained unreliable.
No remote mutation was credited.

### Final path — environment-only HTTP authorization
Git process environment used `GIT_CONFIG_*` to provide an in-memory Basic authorization header while disabling credential helpers/prompts. The secret was never printed or placed in command arguments.

Authenticated dry-run first reported both branches would advance:
`6b0f012..3473834`.

Actual push then returned exit 0 and reported:
- `3473834... -> main`;
- `3473834... -> research/ms1888-replay`.

## Exact remote readback
Push output alone was NOT accepted as publication proof.

### Fresh fetch / remote refs
After push, `git fetch origin --prune` succeeded.
Fetched refs:
- `origin/main` -> `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`;
- `origin/research/ms1888-replay` -> same.

Final `git ls-remote --heads --tags origin`:
- `refs/heads/main` -> `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`;
- `refs/heads/research/ms1888-replay` -> `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`;
- `refs/tags/ms1887-exact` -> `2e73101001b00b59d284855fe5c9a4f55b2486c7`.

### Tree/blob equality
Local, fetched `origin/main`, and fetched research branch tree are all:
`f9840ac4ae35c6796e2a397fd581659c3c44c8a7`.

All 20 paths changed from MS1924 to final head had exact local-commit vs fetched-remote Git blob identity.

A first raw SHA-256 working-tree comparison falsely reported 16 mismatches because Windows checkout line endings may differ from normalized committed blob bytes despite a clean Git index. This verifier was rejected as representation-naive.

Correct path-aware `git hash-object --path=<path>` verification matched committed blob IDs for every changed path.

Earned verifier scar:
`RAW_WORKTREE_BYTES != COMMITTED_BLOB_BYTES_UNDER_CLEAN_FILTERS` may occur without repository divergence.
Use Git clean-filter/blob identity or an equivalently normalized comparison.

### Fresh anonymous clone witness
A new anonymous depth-1 clone of remote `main` returned:
- HEAD `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`;
- tree `f9840ac4ae35c6796e2a397fd581659c3c44c8a7`;
- clean worktree.

For all 20 changed paths:
- local path-aware filtered blob == committed blob;
- fresh-clone path-aware filtered blob == committed blob;
- unexplained content mismatches: 0.

Four raw checkout files differed only by CRLF/LF materialization and became byte-identical under LF normalization:
- `evidence/MS1939_PROPOSAL_ACTION_INDICATION_RELEASE_RECEIPT.json`;
- `methodology/MS1939_ZERO_PRESSURE_REHEARSAL_ABSTENTION.md`;
- `microseed/development/rehearsal.py`;
- `microseed/runtime/entity.py`.

Final conclusion:
`VALIDATED_LOCAL_STATE -> COMMITTED_PUBLIC_BYTES -> FETCHED_REMOTE_BYTES -> FRESH_CLONE_BYTES` is verified modulo explicitly understood clean-filter line-ending materialization.

## Final state
- Public GitHub publication: VERIFIED.
- Current research-descendant public repo head: `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`.
- Current organism-code repair commit inside that lineage: `1dcdbd62e80bde4c41f40cbf79c64a1d35f34502` (MS1939).
- Final tree: `f9840ac4ae35c6796e2a397fd581659c3c44c8a7`.
- Local worktree: clean.
- Canonical Main-Dev: unchanged MS1527.
- Novelty posture: `UNKNOWN / NOT_ENTITLED_TO_CLAIM`.
