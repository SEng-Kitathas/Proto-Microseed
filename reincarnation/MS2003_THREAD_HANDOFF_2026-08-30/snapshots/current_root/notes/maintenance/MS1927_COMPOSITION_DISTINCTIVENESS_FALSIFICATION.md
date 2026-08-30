# MS1927 — Orthogonal Composition-Distinctiveness Falsification

Status: RESEARCH / DEMOTION PASS. No organism mutation. No novelty promotion.
Date: 2026-08-27.
Parent sealed technical head: `6b0f012980a625143ea7137be848d6f13b57325b` (MS1924).
Upstream: `MS1925_PRIOR_ART_MECHANISM_COMPARISON.md`, `MS1926_EQUIPPED_EXPERIMENTAL_INTERVENTION_WARRANT_DESIGN.md`.
Canonical Main-Dev remains MS1527.

## Question
After MS1925 demoted every ingredient-level novelty claim, does the remaining integration hypothesis survive contact with architectures that combine several relevant mechanisms in one system?

## Result
The hypothesis is narrowed again.

No contacted architecture was found to reproduce the exact Microseed whole, but several architecture families already combine large subsets that MS1925 had tentatively left as a potentially distinctive composition.

Therefore the status is no longer a broad `POTENTIALLY_DISTINCTIVE_COMPOSITION` claim. It is now:

`UNRESOLVED_RESIDUAL_COMPOSITION_DIFFERENCE / NOT_ENTITLED_TO_NOVELTY_CLAIM`.

Absence of an exact duplicate in this bounded search is not novelty evidence.

## 1. BOID / normative BDI — cognition plus norms/obligations

Broersen, Dastani, Hulstijn, Huang & van der Torre (2001), *The BOID Architecture: Conflicts Between Beliefs, Obligations, Intentions and Desires*:
- explicitly separates beliefs, obligations, intentions and desires;
- uses feedback loops to consider effects before commitment;
- resolves conflicts among the outputs of those components.

Criado, Argente & Botti (AAMAS 2010), *A BDI Architecture for Normative Decision Making*:
- extends multi-context BDI with Recognition and Normative contexts;
- agents acquire norms dynamically from observed/communicated environment;
- norms are recognized and then considered in decision making;
- beliefs/desires feed the normative context to determine when a norm is active;
- norm-derived beliefs/desires feed back into mental contexts;
- agents maintain autonomy while norm constraints affect behavior.

Meneguzzi/Rodrigues-line normative BDI work further uses obligations, permissions and prohibitions to guide/customize plan choice while preserving more autonomy than simply hard-wiring norms as static constraints.

### Pressure on Microseed
This substantially demotes any claim that separately represented normative/epistemic state plus action deliberation is unusual by itself.

Difference that remains:
- Microseed does not currently have a generic norm-recognition/normative context, BDI goal architecture, plan library or explicit normative policy engine;
- its regulatory/epistemic premises are local typed owners rather than a general deontic reasoning layer.

Classification: `KNOWN_ARCHITECTURAL_ANALOGUE`; exact equivalence `UNRESOLVED`.

## 2. Adaptive BDI — learned action models plus plan repair

Stringer, Cardoso, Huang & Dennis (2020), *Adaptable and Verifiable BDI Reasoning*, and later *Adaptive Cognitive Agents: Updating Action Descriptions and Plans*:
- long-term autonomous agents track when capabilities/actions no longer behave as expected;
- maintain explicit action descriptions/self-model;
- collect action-performance data;
- learn new action descriptions;
- adapt/patch affected plans at runtime.

### Pressure on Microseed
This is a strong architectural analogue for developmental learned consequence models, currentness/drift pressure and downstream action adaptation.

Difference that remains:
- BDI architecture brings explicit beliefs/goals/intentions/plans;
- Microseed intentionally avoids a general planner/plan library and asks how far cognition grows from smaller operational mechanisms.

Classification: `KNOWN_ARCHITECTURAL_ANALOGUE`; developmental-learning ingredient is not distinctive.

## 3. Aegis — action-boundary governance with active policy/provenance and fail-closed behavior

Mazzocchetti (2026), *Runtime Governance for Agentic AI: Action-Boundary Control with Trusted Provenance and Fail-Closed Execution*:
- treats model outputs as proposals, not authority;
- trusted runtime decides whether side-effectful action may execute;
- evaluates active policy state at the action boundary;
- resolves provenance server-side rather than trusting governed actor-supplied evidence;
- fails closed under unmet requirements/uncertainty;
- separates proposal, decision, settlement, trusted provenance and execution outcome in auditable traces.

### Pressure on Microseed
This is a very close analogue for:
- `PROPOSAL != EXECUTION_AUTHORITY`;
- current action-boundary mediation;
- provenance as an authorization input;
- fail-closed/abstain behavior;
- separation of proposal/evidence/decision/outcome planes.

Difference that remains:
- Aegis is an external governance/control plane around agentic AI, not a minimal developmental cognitive organism;
- its active policy and trusted-runtime layers are explicit manager/governance architecture, whereas Microseed tries not to install such a general manager inside the organism.

Classification: `STRONG_KNOWN_ARCHITECTURAL_ANALOGUE`.

## 4. Proof-Carrying Agent Actions — certificate-bearing proposal-to-outcome chain

Wang (2026), *Proof-Carrying Agent Actions: Model-Agnostic Runtime Governance for Heterogeneous Agent Systems*:
- asks what action was authorized, under whose authority, with which approval semantics and evidence after execution;
- centers governance on an action certificate;
- organizes control around pre-action admissibility, action open, assumption capture, approval and outcome closure;
- binds checkpoints to action envelopes, runtime/approval receipts and replay-ready proof;
- carries boundary/provenance facts and explicit enforceability classes.

### Pressure on Microseed
This strongly overlaps the shape of exact-premise-bound action requests, approval/authorization separation, execution records and authenticated outcome closure.

Difference that remains:
- PCAA is governance infrastructure, not learned/developmental cognition;
- its certificate does not itself describe Microseed-style learned consequence ancestry, epistemic deficit/priority/information or developmental qualification.

Classification: `STRONG_KNOWN_ARCHITECTURAL_ANALOGUE`.

## 5. AgentBound — multiple independent authorities, current context, exact policy provenance

Kaul, Lan & Gupta (2026), *Behavioral Governance for Autonomous AI Agents: The AgentBound Framework*:
- existing delegated authorization is explicitly insufficient to decide whether an otherwise authorized action should run under current behavioral/operational context;
- evaluates each action using three authorities: delegation, owner-signed behavioral constitution and site action contract;
- conservatively composes these judgments to permit/review/deny before execution;
- generates cryptographically verifiable governance receipts binding every action to exact delegation/policy/semantic artifacts;
- supports continuously refreshed policy with revocability and bounded authority.

### Pressure on Microseed
This is a direct convergence analogue for:
- authority factorization;
- exact artifact/premise binding;
- current-context authorization;
- conservative composition rather than single scalar confidence;
- revocability/currentness;
- replay-verifiable provenance.

Difference that remains:
- authorities are external governance/policy principals, not developmental cognitive premises;
- the framework is a deterministic governance layer rather than a cognition-growth mechanism.

Classification: `STRONG_KNOWN_ARCHITECTURAL_ANALOGUE`.

## 6. Simplex / runtime assurance around learning controllers

Black-Box Simplex and related runtime-assurance systems:
- unverified/learning-capable advanced controller may generate actions;
- runtime decision mechanism mediates control authority;
- control can switch to a safe baseline based on current runtime checks;
- safety authority remains separate from the learned controller’s capability/performance.

### Pressure on Microseed
Strong analogue for capability/proposal separated from final execution permission under current checks.

Difference that remains:
- Simplex owns a safety envelope and fallback controller rather than epistemic/regulatory/provenance premises inside developmental cognition.

Classification: `KNOWN_ARCHITECTURAL_ANALOGUE`.

## 7. What is actually left after MS1927

The remaining difference cannot defensibly be stated as:
- proposal/authority separation;
- current-at-use authorization;
- provenance-bound authorization;
- conservative multi-premise authority composition;
- fail-closed execution;
- receipt/outcome closure;
- normative reasoning alongside beliefs/intentions;
- adaptive learning of action descriptions;
- runtime adaptation to changed action behavior;
- explicit abstention;
- developmental/information-seeking action.

All of those have substantial prior art or strong architecture analogues.

The only surviving residue is narrower:

> Microseed attempts to realize a similar set of pressures *without* installing a general BDI plan architecture, normative policy manager, trusted external runtime-governance manager, global curiosity/reward scalar or self-certifying world model, while allowing learned consequence relations and developmental capability composition themselves to become exact current premises in action authorization.

This may be a meaningful architectural choice.
It is NOT yet demonstrated novelty.

Classification:
`UNRESOLVED_RESIDUAL_COMPOSITION_DIFFERENCE`.

## 8. Why novelty still cannot be claimed
1. Exact-combination novelty cannot be inferred from a bounded negative search.
2. Aegis/PCAA/AgentBound are very close on runtime authority/provenance/action-boundary composition.
3. normative/adaptive BDI is close on cognition + norms + learning/adaptation.
4. the apparent difference may reduce to architectural factoring: internal local owners versus external/global manager contexts.
5. whether that factoring creates a substantively new mechanism or only a smaller decomposition has not been independently adjudicated.
6. contemporary 2026 governance work shows active convergence toward several Microseed design pressures, reducing confidence in any broad distinctiveness narrative.

## 9. Stronger next discriminator
The next useful novelty question is no longer “does anyone combine these ideas?”

It is:

`LOCAL_COMPOSITION_OF_TYPED_AUTHORITY_OWNERS != FUNCTIONALLY_EQUIVALENT_GLOBAL_GOVERNANCE_OR_NORMATIVE_MANAGER`

Plain language:
Does Microseed’s avoidance of a generic manager produce a causally different capability/authority behavior, or is it merely the same reference-monitor/normative-governance logic distributed across smaller local components?

This is a mechanism discriminator, not a literature-counting exercise.

## 10. Required pressure before any distinctiveness claim
- derive a behavioral/causal test where local owner composition and a functionally equivalent manager architecture make different predictions;
- or obtain an independent specialist critique demonstrating a known architecture that already realizes the same local composition;
- or demote the distinction to implementation/factoring style if no causally discriminating behavior can be identified.

Do not claim novelty from absence of an exact named architecture.

## Disposition
MS1927 is a RESEARCH / DEMOTION pass.
No production mutation.
No canonical promotion.
Novelty remains `UNKNOWN / NOT_ENTITLED_TO_CLAIM`.

Same-lineage prior-art search is approaching diminishing returns. Attention Reservoir should now prefer an independent specialist/blind challenge or a mechanism-level manager-equivalence discriminator rather than another broad literature sweep.
