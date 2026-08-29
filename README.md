# Proto-Microseed

Proto-Microseed is an experimental developmental cognitive runtime focused on a narrow question: how much cognition can be earned through grounded operational mechanisms and lawful composition before a large supplied semantic ontology or generic planner becomes necessary?

This repository is a **research descendant**, not a declaration of canonical Main-Dev promotion. MS1924 was the prior sealed organism-code baseline. **MS1939** is the current research-descendant release in this repository: it preserves model-only counterfactual rehearsal while making explicit that a returned rehearsal proposal is **not** itself a current action indication.

## Current bounded claims

The project does **not** claim architectural novelty. Prior-art pressure supports the conservative description:

> Mostly known mechanisms with a specific authority factorization and developmental integration.

Measured engineering results are narrower:

- declared dependency locality can reduce invalidation/recheck blast radius versus a named global-epoch baseline for local drift;
- explicit typed causal trace information improves root-cause localization versus a flat reason vector, while a centralized implementation with equivalent typed trace information matches it;
- independent premise factorization bounds the unsafe blast radius of a single stuck-YES evaluator fault versus a named shared-evaluator baseline, while centralized typed submodules match the local factorization;
- compact hash-bound causal certificates can preserve root/closure readback with lower payload while the full event stream remains audit/recovery authority;
- exact content-addressed inventory/topology manifests are required for historical certificate decode;
- canonical edge-set hashing removes meaningless graph serialization-order churn while ordered bitmap inventories remain strictly position-bound;
- a counterfactual rehearsal proposal remains `MODEL_OUTPUT_ONLY` and now explicitly reports `action_indicated: false` / `action_indication_authority: NONE`; current action indication must be derived separately from current pressure, current control state, and current proposal ancestry.

These are fixture- and baseline-bounded engineering measurements, **not novelty or universal-superiority claims**.

## MS1939 — proposal returned != action indicated

An external donor evaluation drove the public MS1924 code in an unseen synthetic world and identified a real API ambiguity: with the regulated value already inside its viable interval and current pressure equal to zero, counterfactual rehearsal could still return a sequence because viable routes tie at residual pressure zero.

That behavior was independently reproduced on the exact MS1924 code. The donor's suggested cheap repair—return `None` whenever starting pressure is zero—was then rejected by compatibility pressure because zero-pressure rehearsal also serves legitimate **model-only epistemic relation-reentry** paths in MS1477 and MS1782.

The corrected MS1939 repair therefore preserves those counterfactual proposals and makes the distinction explicit:

```text
PROPOSAL_RETURNED != ACTION_INDICATED
MODEL_ONLY_COUNTERFACTUAL_REHEARSAL MAY EXIST WITHOUT CURRENT_REGULATORY_ACTION_INDICATION
CURRENT_ACTION_INDICATION_REQUIRES_SEPARATE_CURRENT_BOUNDED_ACTION_COMMITMENT
```

The presentation-only clarification is excluded from proposal digest identity, so historical proposal lineage is not rewritten.

Release evidence:

- focused MS1939 + affected inherited chain: **42/42 PASS**;
- `Microseed.self_test()`: **81/81 PASS**;
- exact test universe: **183/183 files**, **686/686 declared test functions**, **691 pytest items collected**, all covered by durable PASS receipts;
- compileall: PASS;
- release source snapshot: `0b58df92d72dedf4856ee3b6b209af3991c4e0192595d120dd38139bd0f92528`.

See `methodology/MS1939_ZERO_PRESSURE_REHEARSAL_ABSTENTION.md` and `evidence/MS1939_PROPOSAL_ACTION_INDICATION_RELEASE_RECEIPT.json`.

## Reproduce the MS1933–MS1938 architecture-factor checkpoint

The public harnesses live in `tools/architecture_factor/`. Raw local receipts are written beneath `reports/`; compact final receipts are checked in under `evidence/architecture_factor/`.

Run from the repository root:

```powershell
python tools/architecture_factor/run_ms1933_invalidation_blast_radius.py
python tools/architecture_factor/run_ms1934_fault_localization.py
python tools/architecture_factor/run_ms1935_authority_coupling.py
python tools/architecture_factor/run_ms1936_causal_trace_certificate.py
python tools/architecture_factor/run_ms1937_dynamic_manifest_certificate.py
python tools/architecture_factor/run_ms1938_graph_canonicalization_lifecycle.py
```

A successful checkpoint produces, respectively: **10/10, 12/12, 10/10, 7/7, 10/10, and 13/13** passing checks.

See `methodology/MS1933_MS1938_ARCHITECTURE_FACTOR_CHECKPOINT.md` for named baselines, fairness controls, measured results, and scope limits.

## Repository layout

- `microseed/` — organism/runtime implementation
- `tests/` — embodiment and hostile tests
- `methodology/` — operating profiles and bounded methodology/results notes
- `research/` — historical experiment artifacts
- `evidence/` — compact evidence receipts
- `tools/` — validation and experiment harnesses

## Authority boundary

A passing experiment does not promote a research claim to canonical truth. A research-descendant GitHub release does not change canonical Main-Dev authority. Prediction, observation, qualification, currentness, proposal, action indication, and execution authority are intentionally distinct surfaces.

No license file is asserted by this README; repository usage remains subject to whatever rights the repository owner separately grants.
