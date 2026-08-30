# MS1915 Pass 04 — Optional Priority / Information Authority Boundary

## Discriminator
`LOCAL_PRECHECK_OPTIONALITY != SAFE_PUBLIC_INTENT_API_IF_PRIORITY_INFORMATION_CAN_BE_OMITTED`

Derived laws:
- `LOCAL_PRECHECK != EXECUTION_LICENSE`
- `OMITTED_PREMISE != SATISFIED_PREMISE`
- `SUPPLIED_YES != BOUND_DECISION_PREMISE`

## Historical owner audit
MS1708 had already recorded the negative that `ACTION_LIMITED_UNKNOWN + FEASIBLE_ROUTE != LAWFUL_EPISTEMIC_INITIATION`. Later endogenous paths added decision-bearing priority and information, but the older public typed/grounded adapters remained callable and the lower commitment helper simply omitted absent premises from the conjunction.

## Pre-repair hostile result
Eight OARR Rangers established the bypass:
1. public typed path could nominate under zero regulatory pressure;
2. public grounded path could create an executable intent under zero regulatory pressure;
3. omitting explicit NO priority changed lower-owner result to YES;
4. public path could nominate when program information value was NO;
5. omitting explicit NO information changed lower-owner result to YES;
6. unrelated YES commitments could impersonate decision premises;
7. wrong-target information could ride on genuine priority;
8. information target without exact trial/priority ancestry could license.

Pre-repair durable hostile jobs failed in the unsafe direction as expected. No production claim was made from test failure alone; source ownership and historical intent were audited before repair.

## Repair
Production changes in:
- `microseed/development/epistemic_action.py`
- `microseed/runtime/entity.py`

Repair shape:
- introduced explicit zero-authority `derive_epistemic_program_step_local_precheck()` owning need/feasibility/route only;
- executable `derive_epistemic_program_step_commitment()` now requires priority and information commitments;
- priority must bind to exact current deficit target/ancestry;
- information must bind to exact trial/step and the exact priority commitment;
- public typed/grounded nomination adapters require a decision context before intent creation;
- endogenous candidate evaluation uses local precheck first, then derives decision-bearing priority and information;
- no generic planner/scheduler/manager introduced.

## Positive control
Added a decision-bound public-adapter positive control: when a current decision context genuinely earns both priority and information, the grounded public adapter still nominates with `decision_premises=PRIORITY_AND_INFORMATION_EXACTLY_BOUND` and no authority gain.

## Source mutation adequacy
Isolated source-mutant battery:
- `ALLOW_MISSING_PRIORITY` — REJECTED
- `ALLOW_MISSING_INFORMATION` — REJECTED
- `DROP_PRIORITY_BINDING` — REJECTED
- `DROP_INFORMATION_BINDING` — REJECTED

Survivors: 0. Unknown: 0.

## Historical test reclassification / demotion
Compatibility pressure exposed old tests that encoded superseded semantics. Tests were corrected to actual owners rather than weakening production repair:
- MS1703/MS1706 now test local need/feasibility/route prechecks plus decision-context-required boundary;
- MS1746 reason owner updated to local precheck;
- MS1902 remains probe-need owner, not execution-license proof;
- MS1912 direct-probe completed-evidence tests use explicitly scaffolded zero-authority action-closure records for downstream evidence-owner pressure;
- MS1913 lifecycle tests assert nomination-time decision-context closure.

Important demotion:
Current MS1904/1905 direct-probe fixture has exact discriminator satisfaction but current decision-bearing priority/information are UNKNOWN (`PROGRAM_RELATION_ANCESTRY_INCOMPLETE`). Therefore prior downstream direct-probe tests do NOT establish lawful organism execution. They remain valid only for the narrower downstream owners they explicitly pressure.

## Verification
Clean MS1915 hostile + positive-control surface: **10/10 PASS**.
Affected owner/reclassification surface: **46/46 PASS**.
Selective regression: **30/30 modern + 74/74 inherited + compileall PASS**.

Frozen full-suite verifier:
- source snapshot stable start=end=`f5873ceff7ee74816429485a2c47629ecc97ec2e380c2bbb2f1b5c6424876cfc`;
- compileall PASS;
- 0 negative assertion groups;
- 600 tests passed in selected bounded groups;
- five single-file leaves hit the 35s route ceiling and were initially UNKNOWN.

Surgical leaf closure, without global timeout increase:
- MS1533: 9/9 PASS, job `job-9f8e544573e6`;
- MS1534: 8/8 PASS, job `job-3f868ce16849`;
- MS1535: split 4/4 + 4/4 PASS, jobs `job-fd804d5d1a82`, `job-46250572bbbc`;
- MS1598: split 5/5 + 4/4 PASS, jobs `job-e77a3d6ac84e`, `job-a262b367050c`;
- MS1620: 6/6 PASS, job `job-368cc02f140a`.

Final exact compatibility closure:
- **640/640 tests PASS**;
- **173/173 test files covered**;
- source snapshot still exact `f5873ceff7ee74816429485a2c47629ecc97ec2e380c2bbb2f1b5c6424876cfc`;
- compileall PASS;
- no remaining negative or UNKNOWN test files.

Compatibility closure receipt: `reports/ms1915_pass04_compatibility_closure.json`, SHA-256 `bbaf057064a4f5526a9890b40d127f87219a6e3e3f8a8e52388b22859be55aef`.

## Git seal
Commit: `33e93566bee2bbd04cc17c005609a060fe7dbfad`
Message: `MS1915 require decision-bound priority and information`
12 files changed, 958 insertions, 153 deletions.
Worktree clean after commit.

## Authority / claim boundary
- Experimental research descendant only; Main-Dev remains MS1527.
- This pass earns closure of the optional-premise public authority bypass.
- It does NOT earn lawful direct-probe execution where priority/information ancestry remains incomplete.
- Compatibility breadth is separate from mutation adequacy; both were independently checked.

## Helix successor
`EXACT_DIRECT_PROBE_SATISFACTION != CURRENT_DECISION_BEARING_AUTHORIZATION`

Question: can a direct-probe trial that independently satisfies the exact missing discriminator also lawfully construct current decision-bearing priority/information from owned relation ancestry, or is current probe availability still only a local epistemic opportunity rather than authorization to execute?