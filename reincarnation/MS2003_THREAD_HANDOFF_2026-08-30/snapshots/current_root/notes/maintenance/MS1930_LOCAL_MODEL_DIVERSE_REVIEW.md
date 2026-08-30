# MS1930 — Local Model-Diverse Review Evidence

Status: MODEL-DIVERSE CRITIQUE / SOURCE-EVIDENCE GATE NOT SATISFIED.
Date: 2026-08-28 ET.
Input packet: `notes/maintenance/MS1929_INDEPENDENT_SPECIALIST_CHALLENGE_PACKET.md`.
No organism code mutation.

## Purpose
Use genuinely different local model weights/families to pressure the MS1929 architecture/prior-art packet while keeping model prose separate from verified source evidence.

## Reviewer 1 — Qwen2.5 Coder 7B
Job: `job-3055e1ad7bc0`.
Model ID: `Qwen2.5-Coder-7B-Instruct-abliterated-Q4_K_M`.
Model SHA-256: `b77b39f196ddd460b622fe101a500723887c470db50aebd217fec7370e6724c3`.
Runtime: llama.cpp b8831 CUDA13.
Completion: COMPLETE / exit 0.
Observed prompt throughput: ~126.5 tok/s.
Observed generation throughput: ~11.4 tok/s.

Raw stdout:
`reports/ms1929_model_diverse_review/qwen7.stdout.log`
SHA `fe72b9949c7518b1e6b07a2132731033db12628ac3ea073f3fd54b09f1ee0396`.

Raw stderr:
`reports/ms1929_model_diverse_review/qwen7.stderr.log`
SHA `7614c9494fb3f7e03012176cc4627dddafc323ffc859ed616bd2fb6e30469325`.

Substantive posture:
- claimed System X is not significantly distinct from existing architectures;
- said many properties reduce to known mechanisms;
- strongest surviving distinction was nuanced abstention based on incomplete authority.

Evidence defect:
- source table used placeholders `[1]` through `[7]` without titles/authors/years;
- therefore the response did not satisfy the packet’s required source discipline.

Classification:
`MODEL_DIVERSE_STRUCTURAL_PRESSURE_VALID / PRIOR_ART_SOURCE_EVIDENCE_NOT_EARNED`.

## Reviewer 2 — CapybaraHermes / Mistral 7B
Job: `job-7a3bf401c0d2`.
Model ID: `CapybaraHermes-2.5-Mistral-7B-Q3_K_S`.
Model SHA-256: `17736f224b217133bee8ee6b5cbb0c8d0bed45466008f9c96c3d058c9d078515`.
Completion: COMPLETE / exit 0.
Observed prompt throughput: ~51.8 tok/s.
Observed generation throughput: ~14.5 tok/s.

Raw stdout:
`reports/ms1929_model_diverse_review/mistral7.stdout.log`
SHA `0a9ae1bf7b4d9a1d8d237366c4fa97c36b0a25f42250bbe8fd3d68547849fb0b`.

Raw stderr:
`reports/ms1929_model_diverse_review/mistral7.stderr.log`
SHA `671234738a531a166edaad507ecd52b1ec9f9d063b651be41d4eb2a03c9337d4`.

Substantive posture:
- described System X as mostly a combination of established mechanisms;
- named adaptive BDI, proof-carrying authorization and runtime assurance as closest families;
- strongest surviving distinction was explicit representation/rederivation of authorization premises.

Evidence defect:
- response supplied concrete-looking IEEE IDs/DOIs, but bounded external verification did not corroborate the claimed mappings;
- exact identifiers were therefore not admitted as verified source evidence.

Classification:
`MODEL_FAMILY_DIVERSE_STRUCTURAL_PRESSURE_VALID / CITATION_PROVENANCE_UNVERIFIED`.

## Reviewer 3 — Qwen2.5 Coder 14B
Job: `job-3ce3afed2c25`.
Model ID: `Qwen2.5-Coder-14B-Instruct-abliterated-Q4_K_L`.
Model SHA-256: `0ab24a52bbfcc5f7cae4f9d57d5134aa140524132b3851519dbe4bf3af6e5db4`.
Completion: COMPLETE / exit 0.
Observed prompt throughput: ~61.9 tok/s.
Observed generation throughput: ~5.6 tok/s.

Raw stdout:
`reports/ms1929_model_diverse_review/qwen14.stdout.log`
SHA `342efb38451fe2eede2bfc88ff0e5812a640ea53b2e00fcd33d7729e00bb1d24`.

Raw stderr:
`reports/ms1929_model_diverse_review/qwen14.stderr.log`
SHA `bee76ea913ac478728b852060495ca5d3cc26e6c8873f92b78006229a1262597`.

Substantive posture:
- unlike Qwen7, claimed the integration may be distinctive;
- emphasized explicit abstention based on authority/provenance/currentness and developmental acquisition without a central executive;
- recommended more prior-art search before claiming distinctiveness.

Evidence defect:
- source table again used placeholder `[1]` through `[3]` rather than inspectable citations.

Classification:
`STRONGER_SAME_FAMILY_CRITIQUE_VALID / PRIOR_ART_SOURCE_EVIDENCE_NOT_EARNED`.

## Cross-review result
The blind reviewers do not converge on a novelty/distinctiveness verdict:
- Qwen7: mostly known / not significantly distinct;
- Mistral7: mostly known mechanisms with a narrower explicit-rederivation distinction;
- Qwen14: potentially distinctive integration, but more search required.

This disagreement is useful because it demonstrates that the question is not robustly resolved by model intuition alone.

Qwen7 and Qwen14 share the Qwen2.5 family and SHALL NOT be counted as independent family corroboration.
Qwen-family versus Mistral-family pressure is materially model-diverse.

## Aggregate classification
For model-diverse critique:
`VALID`.

For source-grounded prior-art adjudication:
`INVALID / INSUFFICIENT`.

For novelty verdict:
`INSUFFICIENT_INFORMATION`.

No favorable or unfavorable model vote changes the project’s prior posture:
`NOVELTY = UNKNOWN / NOT_ENTITLED_TO_CLAIM`.

## Why this is not a failure
The independent-review gate is doing its job. It prevented:
- placeholder citations from becoming sources;
- plausible-looking DOI strings from becoming provenance;
- majority-vote novelty claims;
- same-family models from being counted as independent corroboration.

The local models are now useful as blind falsifier generators and architecture critics. They are not trusted bibliographic authorities without an external source-verification stage.

## Durable setup
Reviewer profile file:
`tools/local_model_review_profiles.json`
SHA `fcbced579abaa3f898e4736fd2b8e1313cf818d298de63484521a7888a328ab7`.

Launcher:
`tools/run_local_model_review.py`
SHA `ba1a6128251099721f4cbdca34698c3fe126e0ed877705f682f9f28d7382b758`.

Model hashes:
`reports/ms1929_model_diverse_review/model_hashes.json`.
Consolidated raw-review receipt:
`reports/ms1929_model_diverse_review/receipt.json`.

## Next useful review mode
Use the models for one of two clearly labeled roles:
1. `BLIND_STRUCTURAL_CRITIC` — no source claims trusted; useful for generating falsifiers and architecture comparisons.
2. `SOURCE_ANCHORED_MODEL_DIVERSE_ADJUDICATOR` — models receive an externally verified source packet and compare mechanisms; reasoning may be model-diverse, but source lineage remains shared and therefore is not independent source discovery.

A genuinely independent human/specialist or source-grounded external reviewer is still required before any favorable novelty claim.
