# B/C Nested Currentness Rebase Audit V1 — 2026-09-01

Status: **REBASING SERIALIZATION COMPLETE / FOCUSED GREEN / RESEARCH ONLY / NOT CANON**

## Baseline
B/C was previously quarantined because it independently touched `microseed/runtime/entity.py`, the same owner admitted by MS Substrate Hardening V1.

Current canon before this rebase:
- Public main: `28489c6feaa9d1d777b8bca0cca2ec3e35042144`
- Canonical label: `PRELINGUAL_SUBSTRATE_V1_P1A_N1A_BOUNDED_HIERARCHY_V1_MS_SUBSTRATE_HARDENING_V1`
- Canonical tag commit: `0f6cf0b3d660c8a4bb9561a65d7f1fd95e1b99f7`
- Canonical Microseed subtree: `88f5a058cc5a4e92b1006c36d31b95cf727d197f`

## Rebase result
Created branch:

`research/hardening-bc-nested-currentness-rebased-on-hardening-canon-v1`

Current head:

`3f386fa487e12f738e71393eb0cc1665ebe5d2a4`

Microseed subtree:

`4c8051563279d20f2ea555d21d7b3305b039e771`

Method: cherry-picked B/C source commit `4188e40dce4c560726b0bdaa6661c031b8ddc0e0` onto current public main. `microseed/runtime/entity.py` auto-merged, but semantic admission is **not** inferred from auto-merge.

## Production delta from current canon
- `microseed/development/rehearsal.py`
- `microseed/runtime/entity.py`

## Semantic claim
B/C rebased research repairs scoped routing currentness. Routed rehearsal proposals preserve `projection_routing_id` and `projection_bucket_id` ancestry; projection-conditioned relation currentness is revalidated against exact binding, selected bucket, relation, and post-binding routed actual outcomes; ambiguous legacy routed descendants fail closed.

## Verification
- Direct unpatched focused run: 6 passed, 6 failed due Windows SQLite `TemporaryDirectory.cleanup` only.
- Cleanup-neutral focused run: **12/12 PASS** in 63.90s, `PYTEST_RC=0`.
- Compileall: PASS for `microseed` and B/C focused tests.
- Public verifier: PASS, issues empty; continuity check only, not canon admission.
- Current-canon identity guard: **1 failed, 1 passed as expected** because branch `HEAD:microseed = 4c805156...` differs from canon `88f5a058...`.

## Decision
B/C is now serialized onto the hardening canon as a research branch. It is **not admitted** and **not canon**.

## Required before admission
Run broader adjacent/whole-suite verification and a separate admission audit, with the current-canon identity guard handled explicitly.
