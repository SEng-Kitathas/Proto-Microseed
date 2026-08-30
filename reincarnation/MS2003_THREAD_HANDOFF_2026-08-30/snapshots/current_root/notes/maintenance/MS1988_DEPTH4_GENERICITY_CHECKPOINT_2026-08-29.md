# MS1988 Depth-4 Genericity Checkpoint — 2026-08-29

## Seal / publication
- Technical milestone: **MS1988**.
- Commit: `c734c366fa22a313f7eb4c07eac83a17e513bcfc`.
- Tree: `3db380d6ef3f13ddf43bda9a60dfb78d48a034e6`.
- Source/test snapshot: `656e06712f4a22599eed08280410640d6097ac1f4bb44f2929491d605ce719f5` / 313 Python files.
- Worktree clean at seal.
- GitHub `refs/heads/research/ms1888-replay`: remote readback exactly matched the seal.
- `origin/main`: unchanged at `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`.
- Canonical Main-Dev remains MS1527.

## Purpose
Test whether the MS1987 bounded recursive source-lineage evaluator works one representation generation deeper without changing Microseed core.

Target:
`A+B -> C`, `C+D -> E`, `E+F -> G`.

## Result
No core file changed.

Depth 1:
- source set A/B/C/D/F;
- E refused with `SOURCE_PROJECTION_RECURSIVE_DEPTH_EXCEEDS_BOUND`;
- G max-subset-2 candidate count 0.

Depth 2:
- source set A/B/C/D/E/F;
- one-source G candidate count 0;
- exact G positions `(4,5)` = E+F;
- validation 1.0;
- lift 0.53125;
- external process holdouts 64/64.

Currentness:
- E change stales G;
- C change stales current E.

Earned:
`THE_SAME_BOUNDED_SOURCE_LINEAGE_EVALUATOR_SUPPORTS_ONE_MORE_LEVEL_OF_OPAQUE_REPRESENTATION_COMPOSITION_WITHOUT_CORE_MECHANISM_CHANGE`.

## Verification
- focused cleanup-neutral `job-6c498585129d`: **1/1 PASS in 80.22s**;
- whole cleanup-neutral `job-d0fc85134a95`: **777/777 PASS in 457.06s**;
- whole stderr empty;
- self-test 81/81 PASS;
- compileall PASS;
- `git diff --check` PASS;
- `git diff -- microseed` empty.

## Scaling seam exposed
Generated projection records still bind the full source-vector basis lineage, not only the coordinates selected by the learned candidate. At MS1988 this produced ancestry widths C=4, E=5, G=6 even though each learned relation used only two coordinates.

This is safe but conservative. It can cause unnecessary staleness and will widen recursive evaluation work.

## Next pressure
MS1989 should first prove the false-staleness cost with a controlled unused-source change. If real, test the smallest lawful distinction between:
- evaluation basis ancestry; and
- selected dependency ancestry.

Do not weaken fail-closed currentness. Do not introduce a new manager unless the existing candidate/source-order surfaces cannot carry the distinction.