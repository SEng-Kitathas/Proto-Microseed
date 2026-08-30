# MS1935 — Authority Coupling / Unsafe Fault Containment

Status: NON-NOVELTY ARCHITECTURE-FACTOR EXPERIMENT.
Date: 2026-08-29 ET.
No organism source mutation. No canonical promotion.
Sealed organism head during run: MS1924 `6b0f012980a625143ea7137be848d6f13b57325b`.

## Question
Under an equal one-code-site stuck-YES mutation budget, does independent premise factorization bound unsafe authorization corruption relative to a named architecture that routes all premise types through one shared evaluator? Does any apparent advantage require physically distributed owners, or can a centralized manager with the same typed submodules match it?

## Grounding in actual Microseed semantics
Source:
`microseed/runtime/commitment.py`
SHA-256 during run:
`aced0107fd17d391e6c01d3416ac9f4f06699754c5baf84f4ffcc66cbb490701`.

Actual conjunction law:
- a current/evaluable NO vetoes;
- YES is licensed only when every required premise licenses YES;
- otherwise result is UNKNOWN.

Program-step executable premise axes grounded from current Microseed:
- NEED;
- PRIORITY;
- INFORMATION;
- FEASIBILITY;
- ROUTE.

## Harness / receipt
Harness:
`tools/run_ms1935_authority_coupling.py`
SHA-256:
`8c7bfd1090f79f1a2d118345afb4a110079ea380520fe5d686a759658c00a634`.

Receipt:
`reports/ms1935_authority_coupling/receipt.json`
SHA-256:
`8dc598384bc0f63f57cbf45b8919be70d316bc6c97dc4458b6c234794fa94739`.

Durable job:
`job-64f3bbdad248`.
Exit 0.
Checks: 10/10 PASS.
Organism worktree clean.

## Synthetic decision matrix
45 cases total:
- 5 all-premises-YES contexts;
- for each of 5 premise axes: 4 contexts where only that premise is NO;
- for each axis: 2 contexts where only that premise is UNKNOWN;
- 10 double-NO contexts covering every unordered pair of premise axes.

Correct stance counts:
- YES: 5;
- NO: 30;
- UNKNOWN: 10.

One logical mutation site is injected per run.

## Architecture A — MICROSEED_TYPED_PREMISE_GATE
Uses the real `conjoin_required_commitments` semantics.
One independently addressable premise evaluator is forced to YES per run.

For every mutated axis:
- false authorizations: 6 / 45;
- false refusals/abstentions: 0;
- the six wrong cases are exactly the four sole-NO + two sole-UNKNOWN cases for that one premise;
- every double-NO case remains blocked because the other independent NO still vetoes.

## Architecture B — CENTRALIZED_TYPED_SUBMODULE_BASELINE
One centralized manager contains the same five independently addressable typed premise evaluators and uses the same conjunction semantics.

Unmutated behavior matched Microseed on all 45 cases.
Under each corresponding single-site stuck-YES mutation:
- false authorizations: 6 / 45;
- wrong case IDs: exactly identical to Microseed;
- all double-NO cases remain blocked;
- every final stance matches Microseed.

This is the critical fairness control.

## Architecture C — CENTRAL_SHARED_PREMISE_EVALUATOR_BASELINE
Named coupled baseline:
all five premise types route through one shared evaluator function.
A single mutation makes that shared evaluator return YES for every premise type.

Under one stuck-YES fault:
- false authorizations: 40 / 45;
- false refusals/abstentions: 0;
- every originally NO or UNKNOWN case becomes YES.

The 5 originally authorized cases remain YES.

## Result
Independent typed factorization materially bounds the unsafe semantic blast radius of a single evaluator fault relative to the named shared-evaluator architecture.

Under this matrix:
- typed-factorized single-site fault: 6 false authorizations;
- shared-evaluator single-site fault: 40 false authorizations;
- unsafe false-authorization blast ratio: 40/6 ≈ 6.67x larger for the shared evaluator.

However, physical distribution is NOT required.
The centralized typed-submodule baseline matches Microseed exactly.

## Earned engineering statement
`INDEPENDENT_PREMISE_FACTORIZATION_BOUNDS_SINGLE_EVALUATOR_UNSAFE_AUTHORITY_FAULT_BLAST_RADIUS_UNDER_THIS_MATRIX`.

Companion:
`CENTRALIZED_TYPED_SUBMODULES -> SAME_FAULT_CONTAINMENT_AS_LOCAL_TYPED_OWNERS` under equivalent semantics/mutation.

Rejected overclaim:
`PHYSICAL_DISTRIBUTION_OF_PREMISE_OWNERS_IS_REQUIRED_FOR_FAULT_CONTAINMENT`.

## What this does NOT prove
- It does not prove Microseed is uniquely robust.
- It does not prove all centralized managers are coupled.
- It does not model arbitrary code corruption, memory corruption, correlated bugs, or malicious mutation.
- It does not estimate real-world fault probabilities.
- It does not establish novelty.
- The shared-evaluator baseline is intentionally a named coupled design, not a claim about all monolithic implementations.

## Scientific interpretation
MS1935 further shifts the residual architecture story away from physical module placement and toward **semantic factorization**:
- independent veto-capable premise axes reduce how much one stuck-YES evaluator can erase;
- a centralized architecture can preserve the same containment by keeping those axes independently addressable;
- collapsing them through a shared evaluator increases coupling and unsafe fault blast radius under the tested mutation.

This is a concrete engineering property of factorization, not novelty.

## Next Pareto-useful pressure
MS1934 showed rich typed traces improve root-cause precision but carry payload overhead. The next useful question is therefore trace efficiency:

> can the emitted invalidation trace be projected into a compact, hash-bound causal certificate that preserves exact root localization, final stale closure, and dependency-graph identity while materially reducing diagnostic payload?

A successful projection should remain read-only and should NOT replace the full canonical event stream unless a separate audit/recovery argument is earned.
