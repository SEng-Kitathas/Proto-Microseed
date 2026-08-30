# Project-Local External Validation & Scar Re-Earning Amendment — 2026-08-27

Authority source: explicit collaborator/user instruction informed by an external forensic critique of Microseed.
Scope: Microseed research process. This does not rewrite Unified Research OS V3 source; it supersedes weaker project-local validation assumptions.

## Core finding incorporated
Internal engineering/evidence discipline is strong, but self-authored hostiles have a structural independence ceiling: the same reasoning process that writes a mechanism tends to write tests around already-visible failure modes. Internal green therefore proves bounded implementation claims, not independent validation completeness.

## Law 1 — validation provenance is load-bearing
Every significant validation result must distinguish at least:
- `SELF_AUTHORED_VALIDATION`: test/mutant/discriminator authored within the same research lineage as the mechanism;
- `BLIND_EXTERNAL_CHALLENGE`: mutant/discriminator/challenge authored independently of the mechanism-writing lineage;
- `EXTERNAL_LITERATURE_PRESSURE`: prior-art/counterexample/comparator pressure from outside the project;
- `REPLICATION_ONLY`: rerun of an existing challenge, useful for reproducibility but not independent breadth.

A self-authored PASS may be VERIFIED for the exact tested proposition, but must not be rhetorically promoted into evidence that the blind-spot surface is exhausted.

## Law 2 — scars do not carry campaign authority automatically
A scar is a historical warning/invariant, not perpetual verified authority.

At each campaign close, every scar relied upon by the new campaign must be classified:
- `CAMPAIGN_REEARNED`: a fresh campaign-local discriminating test/mutant/counterexample would fail if the enforcing mechanism were removed or inverted;
- `INHERITED_UNVERIFIED`: historically earned but not re-earned in the current campaign;
- `SUPERSEDED`: no longer the correct formulation because the mechanism/authority boundary changed;
- `NONLOADBEARING_HISTORY`: retained as historical context only.

Campaign close must not silently treat `INHERITED_UNVERIFIED` scars as freshly verified.

Preferred re-earning procedure:
1. identify the exact mechanism/branch/invariant the scar claims;
2. construct a fresh mutant that deletes/inverts/short-circuits that mechanism;
3. run the scar's discriminating test against the mutant;
4. verify the mutant is actually applied and restored;
5. record mutant hash/diff, test result, restoration hash, and classification;
6. if the mutant survives, demote the scar and strengthen the test before relying on it.

Where an independently authored blind mutant exists, it outranks a self-authored re-earning mutant for validation breadth.

## Law 3 — campaign close is a re-authorization boundary
Microseed runtime re-earns authority at each tick; campaign methodology must mirror that property.

Campaign close therefore re-authorizes only the claims/scars for which current evidence is present. Historical scar presence alone cannot authorize new promotion, exactly as historical action authorization cannot authorize a later EFFECT tick.

## Law 4 — external contact before novelty/promotion claims
Before claiming novelty, broad architectural significance, or superiority over established approaches, run a server-side prior-art pressure map covering the closest relevant literatures. For the present frontier these include at least:
- developmental robotics / intrinsically motivated learning;
- curiosity and competence-progress exploration;
- active inference / epistemic action / expected free energy;
- Bayesian experimental design / value of information / active learning;
- autonomous scientific discovery / experiment selection where relevant.

External research is donor/pressure evidence only. Do not wholesale-import architecture or ontology. Extract mechanisms, invariants, failure modes, comparators, and counterexamples. Record whether Microseed is novel, convergent, rediscovered, orthogonal, or presently incomparable.

## Law 5 — independent grader outranks more same-lineage passes when available
When a blind external challenge or independently authored mutant set is available, it receives higher Attention Reservoir priority than another internally generated pass on the same mature mechanism, unless an immediate safety/correctness defect blocks it.

If no independent human grader is available, use the most independent available model/tool/process as a weaker proxy and label it `PROXY_INDEPENDENT`, never equivalent to human/blind external review.

## Law 6 — apparatus tax enters Pareto accounting
The Attention Reservoir must explicitly charge process/artifact growth against scientific information gain.

Signals of apparatus tax:
- validation/report/schema growth substantially exceeds mechanism/result growth;
- long disposition/name strings hinder outside comprehension;
- multiple artifacts restate the same claim without adding independent evidence;
- process maintenance displaces the highest-value discriminator;
- auditability machinery becomes a moat against review.

Response:
- consolidate representations without deleting lineage;
- add plain-language aliases/glosses for long symbolic labels;
- prefer one durable receipt plus compact evidence index over redundant artifacts;
- preserve exact hashes/lineage while minimizing ceremony;
- do not reduce rigor merely to reduce file count.

## Law 7 — result modesty is not a defect
Narrow claims remain preferred to inflated claims. `COMPLETED_EXPERIMENT != ANSWER`, `TICK0_SELECTION != TICK1_AUTHORITY`, and similar scars retain historical value, but their current campaign status must still be explicit under Law 2.

## Immediate authority correction
The previously selected internal Pass 3 (`program-realization equivalence vs ambiguity`) is not discarded, but is demoted from SELECTED to OPEN because external/blind validation now has higher expected information gain.

New selected frontier: `VALIDATION_PASS_V1 — blind mutation / scar re-earning + external prior-art pressure map`.

## Known external-audit signal requiring recheck
The external critique specifically reports that `EPISTEMIC_UNCERTAINTY != NORMATIVE_PRIORITY` was inherited across campaigns on a test that could survive deletion of its enforcing branch. Server corpus inspection confirms the scar originates at MS1707 and campaign-close MS1727 does not itself enumerate/re-earn scar authority. The exact reported surviving mutant remains externally observed until reproduced against the current descendant; therefore current status is `INHERITED_UNVERIFIED`, not disproven and not campaign-re-earned.