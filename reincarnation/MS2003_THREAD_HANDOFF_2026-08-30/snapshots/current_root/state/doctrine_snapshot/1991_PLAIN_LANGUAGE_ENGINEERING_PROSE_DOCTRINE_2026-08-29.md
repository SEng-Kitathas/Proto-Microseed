# 1991 Plain-Language Engineering Prose Doctrine — Project-Local Adoption

Date: 2026-08-29 ET
Authority: explicit operator directive in active thread
Scope: ProtoAGI Microseed engineering prose, methodology notes, reports, code comments/docstrings, continuity summaries, and operator-facing explanations

## Compact rules
**Plain language around the mechanism, proper language for the mechanism.**

**Mechanism first. Precision second. Style third. Vocabulary never gets to compete with understanding.**

## Practical target
“1991-ish” is a vocabulary target, not a request to imitate writing from 1991.

General prose should usually use ordinary educated English around a 9th/10th-grade vocabulary level. Keep genuine engineering terms when they name a real distinction and save explanation or ambiguity.

## Rules
1. Keep the hard thinking in the engineering, not in decoding the sentence.
2. Technical terms must pay rent. Use terms such as `invariant`, `provenance`, `epistemic`, `idempotent`, or `extensional` when they are the right technical name for a real distinction.
3. Do not replace useful technical vocabulary with baby talk.
4. Do not choose a rarer or more academic word merely because it sounds more precise.
5. Explain what the mechanism does plainly before leaning on its formal term.
6. Take the short path to the point. Avoid academic fog, padding, ornate transitions, euphemism, and needless abstraction.
7. When prose becomes ornate or starts hiding a simple causal statement, rewrite it into the plainest accurate form that preserves the real idea.
8. Real mechanism complexity may remain difficult. Prose must not add a second artificial difficulty layer.
9. Exact identifiers, hashes, test names, formal rules, authority states, and earned doctrine statements stay exact when exactness matters.
10. This doctrine changes prose, not the burden of proof, verification standard, lineage rules, or authority ceilings.

## Priority order
1. Mechanism.
2. Precision.
3. Style.

Style may improve readability, but it may not hide the mechanism or compete with understanding.

## Enforcement posture
Apply this rule during drafting and revision. If a sentence sounds academic, consulting-heavy, LLM-ornate, or needlessly indirect, rewrite it unless the technical vocabulary is doing real work.

The correct test is not “Is every word simple?”
The correct test is “Can the reader spend attention on the system rather than on decoding the prose?”

## Repo embodiment / publication
Repository doctrine artifact:
`methodology/1991_PLAIN_LANGUAGE_ENGINEERING_PROSE_DOCTRINE.md`

Doctrine-only seal:
`e0c948d32c006d21ad4a867d6f5941c75d7208f7`

Tree:
`4d2c3c3b339ecece5043fea7b844985f3c42199c`

GitHub publication:
`refs/heads/research/ms1888-replay` remote readback exactly matched `e0c948d32c006d21ad4a867d6f5941c75d7208f7`.

Latest technical milestone remains MS1986 `383196060c0bb88980a2e22b972972a4e09f58a5`; this doctrine-only successor does not change Microseed mechanism or test state.