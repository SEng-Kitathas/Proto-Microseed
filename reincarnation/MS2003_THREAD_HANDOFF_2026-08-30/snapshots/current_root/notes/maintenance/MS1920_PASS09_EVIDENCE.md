# MS1920 Pass 9 Evidence — Revisit Refinement Requires Owned Recurrent Visible History

## Discriminator
`AUTHENTICATED_PROBE_EVIDENCE_AND_REVISIT != LAWFUL_REVISED_SURFACE_REBINDING`

Refined local question:
`AUTHENTICATED_CHALLENGE_SAMPLE != SUFFICIENT_RECURRENT_VISIBLE_HISTORY_REFINEMENT`.

## Parent authority
- Parent sealed research head: `7aea15479dc968acc8326a602e93e0b8f9a4c1c0` — MS1919.
- Canonical Main-Dev remains MS1527; no promotion.

## Classification
**NEGATIVE / NO_PRODUCTION_CHANGE PASS.**

No runtime source was changed. No source-mutation battery is applicable because MS1920 introduces no new production guard/mechanism.

## Exact owner audit
`derive_admitted_one_step_visible_history_refinements(...)` requires each current transition row to have an exact predecessor relation recovered from owned history:
- current execution intent `control_state_evidence_id` must point to exactly one prior actual outcome;
- both prior and current executions must independently project as admitted opaque transitions;
- prior end token must equal current start token;
- both samples must be in the same current frame.

The refinement grammar then requires, for a `(frame,start,action)` slot:
- each previous-visible context must be endpoint-unanimous;
- each context endpoint must recur on at least **two distinct current origin handles**;
- at least **two contexts** must remain;
- at least **two distinct endpoints** must be represented across those contexts.

This is proposal-only structure. It grants no hidden-state, model-replacement, truth, or execution authority.

## Live MS1919/MS1920 direct-probe challenge
Authenticated surprise successfully produces:
`MODEL_SPACE_CHALLENGE -> REVISIT_REQUIRED`.

The challenge execution is current and independently admitted, but its intent was created after `_bound_at_probe_locus()` established `s1` through direct opaque-state observation:
- challenge start state: `s1`;
- challenge action: `B`;
- challenge intent `control_state_evidence_id`: `E-MS1904-PROBE-LOCUS-S1`;
- that evidence ID is **not** an action outcome evidence ID.

Therefore the challenge has no lawful predecessor/current action-history pair.

The fixture contains an older valid one-step refinement for `(s1,B)`, but the new challenge sample:
- is not in that candidate's `source_sample_ids`;
- has an endpoint outside that candidate's existing context outcomes.

The revisit join correctly returns `NO_BOUNDED_REFINEMENT_FOR_REVISIT` rather than retroactively absorbing the surprise into prior model structure.

## Hostile counterfactual
A diagnostic counterfactual forcibly replaced the challenge intent's control-state evidence pointer with a real authenticated prior `s0 -> s1` outcome (`E1858-LIVE-A`).

Result:
- successor pair count increased;
- the old one-step refinement disappeared;
- revisit still returned `NO_BOUNDED_REFINEMENT_FOR_REVISIT`.

Reason: the same previous-visible context `s0` would then contain conflicting observed endpoints (`sx` vs the new surprise). One grafted predecessor does not grant recurrence or unanimity.

Earned law:
`PREDECESSOR_LINK != RECURRENT_UNANIMOUS_VISIBLE_HISTORY`.

A separate attempted positive diagnostic tried to reinstall MS1858 helper capabilities inside a fixture that already contained them and failed early with duplicate-capability error. This is `INVALID_FIXTURE_COLLISION`, not scientific evidence, and is excluded from the result.

## Existing positive mechanism evidence
MS1858–MS1862 remain the positive mechanism owner:
- authenticated recurrent visible-history pairs can produce a bounded one-step refinement;
- MS1859 binds revisit refinement to the exact admitted challenge sample;
- MS1860 preserves proposal-only/no-reopen/no-replace behavior;
- MS1861 requires projection qualification before consequential routing;
- MS1862 reuses the existing external projection admission owner.

Therefore the current result is **missing evidence/history composition, not missing refinement machinery**.

## MS1920 audit suite
`tests/embodiment/test_ms1920_pass09_revisit_refinement_requires_owned_history.py`

4/4 PASS, job `job-0f3bfc14eea0`:
1. live direct-probe challenge has no owned predecessor outcome pair;
2. existing refinement surface cannot absorb a novel challenge endpoint retroactively;
3. grafting one real predecessor does not turn a single surprise into refinement;
4. no bounded refinement means no revision acceptance or successor creation.

## Compatibility / positive-owner checks
Focused owner job `job-70d41cf35ff9`:
- MS1858–MS1862 + MS1919 + MS1920: **16/16 PASS**.

Selective regression job `job-0a14e760515d`:
- modern: 30/30 PASS;
- inherited cleanup-neutral: 74/74 PASS;
- compileall PASS;
- overall PASS / COMPLETE.

Because MS1920 changes no production source, exact production compatibility remains inherited from sealed MS1919 (670/670 over 177 files) plus the new MS1920 audit evidence above. MS1920 does not claim a new full-suite aggregate count.

## Earned laws
- `AUTHENTICATED_CHALLENGE_SAMPLE != SUFFICIENT_RECURRENT_VISIBLE_HISTORY_REFINEMENT`.
- `DIRECT_STATE_OBSERVATION != OWNED_PREDECESSOR_ACTION_OUTCOME`.
- `PREDECESSOR_LINK != RECURRENT_UNANIMOUS_VISIBLE_HISTORY`.
- `ONE_SURPRISE != REVISED_MODEL`.
- `EXISTING_REFINEMENT != PERMISSION_TO_ABSORB_UNSEEN_CHALLENGE`.
- `EVIDENCE_INSUFFICIENCY != MECHANISM_INSUFFICIENCY`.

## Next developmental seam
The highest-information continuation is no longer “invent revision.” It is whether the organism can **lawfully earn the required recurrent admitted visible history** through actual bounded interaction rather than test-only history injection.

Provisional successor discriminator:
`REQUIRED_RECURRENT_VISIBLE_HISTORY != LAWFULLY_EARNED_ENDOGENOUS_HISTORY`.

## HSP/SOP posture
HSP remains advisory only. Any next-frontier selection must be made by an explicit external selector with model-adequacy status recorded.

## Claim boundary
MS1920 does not qualify or promote a revised model. It establishes why the current direct-probe experiment cannot yet enter the already-existing bounded refinement path, and it preserves that failure as evidence rather than filling the gap with inferred history.
