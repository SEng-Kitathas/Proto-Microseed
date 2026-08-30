# MS1995 Crossing/Occlusion Reassociation Checkpoint — 2026-08-29

## Seal / publication
- Technical milestone: **MS1995**.
- Commit: `a3e82f4f80bbe910234590f2cdf982293ac4fa96`.
- Tree: `d6b5539f8313db555a995dc04d081ac6c5a64c00`.
- Source/test snapshot: `26f82c0c8a1ecb5953945b1c09b4ba068271dbf5f1b6bb7446af0faee21a73d6` / 319 Python files.
- Worktree clean at seal.
- GitHub research ref remote readback exactly matched the seal.
- `origin/main` unchanged at `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`.
- Canonical Main-Dev remains MS1527.

## Boundary
Two operational referents undergo:
- channel/presentation crossing;
- full temporary occlusion of one referent;
- complete observation gap;
- post-gap channel swap;
- raw affine appearance change.

Re-association follows existing affordance-relative action-response signatures, not fixed channel positions.

## Hidden hostile variants
- persistent A/B;
- unmarked replacement of A;
- unmarked replacement of B;
- perfect-copy replacement of both;
- post-gap action-effect aliasing.

## Result
- PRE: A `[0,1]`, B `[2,3]`;
- CROSS: A `[0,3]`, B `[1,2]`;
- POST: A `[2,3]`, B `[0,1]`.
- Full A occlusion -> `UNKNOWN_INCOMPLETE` rather than guessed persistence.
- Persistent world -> A/B traces RETAINED.
- Replace A unmarked -> A LOST, B RETAINED.
- Replace B unmarked -> A RETAINED, B LOST.
- Perfect-copy world -> operationally identical to persistent world; numerical identity remains NONE.
- Aliased post evidence -> `UNKNOWN_INCOMPLETE_NO_GUESS`; trace test is not used to manufacture a partition.

Earned:
`AFFORDANCE_RELATIVE_REASSOCIATION_PLUS_IDEMPOTENT_INTERVENTION_TRACE_TESTS_CAN_PRESERVE_OPERATIONAL_MULTI_REFERENT_CONTINUITY_THROUGH_PRESENTATION_CROSSING_OCCLUSION_AND_APPEARANCE_CHANGE_WHILE_DEFERRING_ON_ALIASED_EVIDENCE`.

## Mechanism verdict
No new referent-core mechanism was required. No object tracker, persistent ID manager, semantic class, or genealogy layer was added.

## Verification
- direct boundary: PASS;
- focused referent regression `job-e68615bd6252`: **17/17 PASS in 2.67s**;
- whole cleanup-neutral suite `job-845b93c2ac68`: **792/792 PASS in 613.52s**;
- stderr empty;
- self-test **81/81 PASS**;
- compileall PASS;
- `git diff --check` PASS.

A later duplicate whole-suite job `job-ce55bbc849ab` was intentionally terminated after the stronger whole-suite witness completed and is not used as evidence.

## Next frontier
MS1996: endogenous intervention/probe candidate construction from authenticated learned opaque structure and already-qualified primitives, while preserving:
- candidate construction != execution authority;
- opaque action handles != semantic action names;
- information-bearing proposal != permission to execute;
- NAKED unknown-effect first probe remains constitutionally blocked.