# Recovery and Operating Playbook

Date: 2026-08-30 ET
Purpose: concrete successor operating procedure for resuming this project without repeating thread loss, stale-state regressions, or control-plane execution failures.

## Part I — cold re-entry
### 1. Start in RECOVERY / R1
Do not start in R5 just because the user says “proceed.”
First recover state.

### 2. Verify package integrity
Run:
`python VERIFY_REINCARNATION_PACKAGE.py`

Require:
- all manifested files present;
- all hashes exact;
- no package verification error.

### 3. Read reconciliation before stale state files
Read:
- `02_VERIFIED_STATE_AND_CONTRADICTIONS.md`;
- `03_COMMANDERS_INTENT.md`;
- `05_SCARS_AND_DO_NOT_REINTRODUCE.md`;
- `06_AUTHORITY_LINEAGE_AND_PROMOTION_MAP.md`;
- `07_CURRENT_FRONTIER_MS2004_UNSEALED.md`.

Only then use the raw snapshots.

### 4. Check live Git if original server exists
At checkpoint creation the published research ref was:
`9946d4ddf37642615b5f4e5a47685f94397803ff`.

Run live:
- `git rev-parse HEAD`;
- `git status --short`;
- `git branch --show-current`;
- `git ls-remote origin refs/heads/research/ms1888-replay`.

If live verified research is newer than this package, do not downgrade.

### 5. Reconcile unsealed worktree
Compare live MS2004 files against packaged copies under `unsealed_worktree_snapshot/MS2004/`.

Do not overwrite either side until lineage is clear.

### 6. Compact ingress report
Before widening, report only:
- Mode;
- Role;
- Verified;
- Provisional;
- Baseline;
- Contradictions;
- Open seams;
- Exact live Git versus packaged Git;
- Immediate next action.

Then move to R5 if the frontier is stable.

## Part II — evidence and mutation order
Preferred order for any substantive campaign:

1. re-read Live Shadow / Current State if current;
2. inspect Git status/HEAD;
3. inspect relevant methodology/test/source;
4. write prewrites and nonclaims;
5. build or modify the smallest demonstrated missing distinction;
6. direct test;
7. focused lineage;
8. freeze hashes;
9. self-test / compile / diff checks;
10. one whole-suite witness;
11. interpret result;
12. post-witness hash readback;
13. stage exact files;
14. cached diff check;
15. local seal;
16. push;
17. independent remote readback;
18. continuity/state update;
19. move to next campaign.

Do not reverse 17 and 18 when claiming publication; remote readback is the publication witness.

## Part III — failure-aware execution rules
Recent thread experience produced a recurring class of control-plane failures. These are operationally important and must not be confused with scientific failures.

### Failure class A — supervision loss
Observed pattern:
pytest output can show all tests passed while the server job surface reports `SUPERVISION_LOST` / missing return code.

Rule:
That async job is not a valid witness by itself.
Use a clean independent rerun or direct local process readback.

### Failure class B — ghost job metadata
Observed pattern:
job controller says RUNNING while the process PID no longer exists.

Rule:
Controller metadata != process reality.
Check PID / output-file growth before declaring a job live.

### Failure class C — host preemption / `-9`
Rule:
Host kill != scientific test failure.
Do not repair code based only on a preempted run.

### Failure class D — oversized response/control route
Observed:
- broad job listings can return too much metadata;
- `ResponseTooLargeError`;
- output retrieval may 500.

Rule:
Use targeted job IDs, file-tail readback, capped outputs.
Do not repeat the same broad toxic request.

### Failure class E — convenience endpoint 500
Observed:
`readProjectFile` or structured output endpoint can intermittently return 500 while direct bounded local execution succeeds.

Rule:
Switch route. Do not interpret HTTP 500 as project failure.

### Failure class F — guessed focused-test path
Observed:
focused verification can fail because a filename was guessed incorrectly.

Rule:
Preflight exact test paths before pytest.

### Failure class G — buffered/slow output mistaken for hang
Rule:
Use PID existence + stdout size/mtime growth.
Polling timeout alone is not a hang.

### Failure class H — concurrent tree movement
Rule:
Witness belongs to exact bytes.
Do not mutate candidate files while a whole suite is running.
Freeze hashes before and compare after.

### Failure class I — duplicate whole-suite relaunch
Rule:
One frozen candidate -> one idempotent whole-suite job.
A noisy status UI is not permission to launch another.

### Failure class J — chat continuity behind server reality
Observed:
server-side jobs/commits continued while chat inference/tool turns failed, leaving Live Shadow/current prose behind Git.

Rule:
After any thread/tool failure period, re-establish Git reality before trusting continuity prose.

## Part IV — long campaign design
When user asks to “press the gas” or run overnight:
- run long work server-side;
- write the long campaign to a file rather than giant inline command arguments;
- use hash guards;
- make campaigns self-abort on tree drift;
- stop on first substantive failure;
- distinguish orthogonal campaigns from duplicate tests;
- avoid CPU contention that turns scientific results into scheduler noise.

Good overnight pattern:
1. deterministic hostile lifecycle repetitions;
2. randomized topology/fuzz pressure;
3. restart/reentry lineage repetitions;
4. whole-suite repetitions only if the candidate is frozen and earlier phases pass.

## Part V — continuity maintenance
The project has proven that continuity instruments themselves can lag.

### Live Shadow
Keep bounded/current.
Do not let it become a transcript.

### Design Thread Stream
Append chronology.
Do not depend on it alone for scientific currentness.

### Current State
Update after verified publication and material frontier change.

### Next Steps
Keep aligned with the strongest current baseline; do not leave an MS1998 baseline after research has reached MS2003.

### Revisit Ledger
Use for claims that must return under pressure.

### Trace Matrix
Use for load-bearing claim -> evidence -> embodiment -> verification lineage.

### If these conflict
Do not rewrite them silently.
Create a reconciliation note and then repair them under append-only discipline.

## Part VI — R3.1 engineering SOP use
Exact archive:
`archives/RAHL_ENGINEERING_IN_HOUSE_SOP_SPLIT_CANDIDATE_R3_1_2026-08-29.zip`.

Before treating R3.1 as authority:
- read project-local adoption notes;
- preserve R6/V5 ancestry where required;
- remember the original adoption status was shadow/project-local and not automatic universal replacement;
- verifier coverage is bounded to what it checks.

Use R3.1 to improve engineering discipline, not to erase project-specific scars.

## Part VII — Git/publication discipline
### Research branch
`research/ms1888-replay` is the published research lineage.

### Continuity branch
This reincarnation package is deliberately on a separate continuity branch so recovery docs do not masquerade as scientific MS2004 progress.

### Canonical Main-Dev
Remains MS1527 unless separately promoted.

### Push checklist
- clean staged scope;
- `git diff --cached --check`;
- commit message identifies scientific milestone vs continuity checkpoint;
- push correct branch;
- independent `ls-remote` readback;
- report exact SHA/tree.

## Part VIII — how to handle a donor/new idea
All inbound signal becomes controlled evidence.

For donor claims:
1. identify the concrete mechanism/test/scar;
2. search current corpus for prior equivalent;
3. distinguish new insight from rediscovery;
4. preserve useful pressure;
5. do not import donor architecture or confidence level automatically;
6. write project-local amendment only if it changes active doctrine.

## Part IX — language gate
Before language work:
- verify substrate promotion criteria;
- preserve signaling/reference scars;
- prewrite false-positive tests;
- do not evaluate meaning by readability alone;
- require referent binding/current premise evidence;
- keep utterance authority separate from production.

## Part X — immediate successor decision tree
### Case A: live research ref == packaged MS2003, live MS2004 matches package
Resume MS2004 verification/seal.

### Case B: live research ref == packaged MS2003, live MS2004 differs
Audit both MS2004 versions; preserve lineage; choose only after evidence.

### Case C: live research ref > MS2003
Recover the newer Git lineage first. Use this package for intent/scars/history, not as a rollback command.

### Case D: live server unavailable
Use this continuity branch + package manifest + embedded archives to reconstruct context. The repository itself contains full source/test/methodology through MS2003.

### Case E: package verifier fails
Stop widening. Identify missing/changed files. Do not pretend recovery is complete.

## Final recovery principle
The successor should not need the operator to narrate the project again.

If something appears unclear, search this package, sealed methodology, maintenance notes, and Git history before asking for history already preserved here.

Ask the operator only for genuinely new intent/authority decisions, not for facts the project already knows.
