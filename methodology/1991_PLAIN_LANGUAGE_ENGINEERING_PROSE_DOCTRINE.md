# 1991 Plain-Language Engineering Prose Doctrine

Date adopted: 2026-08-29 ET
Status: active project-local doctrine
Scope: Microseed engineering prose, methodology notes, reports, code comments/docstrings, continuity summaries, and operator-facing explanations

## Core rule
Use ordinary educated English for the prose around a mechanism. Keep the real technical term when it names a real technical distinction.

Compact form:

> **Plain language around the mechanism, proper language for the mechanism.**

Priority form:

> **Mechanism first. Precision second. Style third. Vocabulary never gets to compete with understanding.**

## Practical vocabulary target
“1991-ish” is a practical vocabulary target, not an instruction to imitate writing from the year 1991.

General prose should usually sit near a 9th/10th-grade vocabulary level: clear, ordinary educated English before the modern academic, consulting, and LLM habit of reaching for the most sophisticated available synonym.

This target applies to general-language wording, not to necessary engineering terms.

## Rules
1. **Keep the hard thinking in the engineering, not in decoding the sentence.**
   Vocabulary should not consume attention that belongs on mechanisms, evidence, code, tests, or decisions.

2. **Technical terms must pay rent.**
   If `invariant`, `provenance`, `extensional`, `epistemic`, `idempotent`, or another technical term is the correct name for a real distinction and compresses useful meaning, use it.

3. **Do not turn technical material into baby talk.**
   The rule is not “simple words only.” It is plain language around the mechanism and proper technical language for the mechanism.

4. **No collegiate-vocabulary Olympics.**
   A rarer, more academic, or more impressive-sounding word is not better merely because it sounds precise.

5. **Explain the mechanism plainly before leaning on its formal name.**
   A reader should understand what the thing does even if they have never seen the formal term before.

6. **Take the short path to the point.**
   Avoid academic fog, padding, ornate transitions, euphemism, and abstraction that makes a simple causal statement harder to see.

7. **Rewrite academic camouflage.**
   If prose becomes ornate, inaccessible, or starts hiding a simple mechanism behind abstract language, rewrite it into the plainest accurate form that preserves the real idea.

8. **Do not erase real complexity.**
   Complexity belongs where reality requires it. A difficult mechanism may remain difficult. The prose should not add a second, artificial layer of difficulty.

9. **Precision beats style, but understanding beats ornamental precision.**
   Prefer the exact technical distinction when it matters. Do not choose a complicated synonym when a common word says the same thing.

10. **Code and evidence keep their exact names.**
    Identifiers, error codes, invariant names, hashes, formal rules, test names, and earned doctrine statements should remain exact when exactness matters.

## Application examples
Prefer:
- “The source projection changed, so the dependent projection becomes stale.”

Over:
- “Mutation of the antecedent representational substrate induces invalidation of downstream epistemic dependents.”

Prefer:
- “The operation is idempotent: running it again with the same input does not change the result.”

Over either extreme:
- unexplained jargon: “The operation is idempotent.”
- baby talk that loses the useful term: “Doing it twice is okay.”

Prefer:
- “Provenance records where this result came from and what evidence it depends on.”

Then use `provenance` normally after the mechanism is clear.

## Engineering relationship
This doctrine changes prose, not the burden of proof.

It does not weaken:
- exact evidence handling;
- lineage/currentness checks;
- formal identifiers;
- technical distinctions;
- test rigor;
- explicit uncertainty;
- authority ceilings.

It only removes needless vocabulary cost around those mechanisms.

## Anti-patterns
Rewrite when prose shows any of these:
- sophisticated synonym chosen where a common word is equally exact;
- long abstract noun chains;
- ornate transition phrases;
- passive wording that hides the actor or cause;
- formal terminology introduced before its mechanism is explained;
- compressed jargon that forces the reader to decode the sentence before seeing the causal structure;
- simplistic replacement of a useful technical term that makes the mechanism less precise.

## Final standard
A good sentence should make the mechanism easier to inspect.

The reader’s effort should go into understanding the system, not proving they can decode the prose.
