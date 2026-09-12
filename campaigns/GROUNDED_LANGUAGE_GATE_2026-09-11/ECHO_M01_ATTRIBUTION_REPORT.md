# Echo-M01 Attribution — Grounded Conversational Episodic Memory

## Origin
Echo Chamber smoke pressure immediately exposed `MEMORY_PRESSURE`: conversational interaction asks whether Veya can recognize prior interaction, while the chamber runtime was intentionally disposable. This observation generated a clean experiment; it did not itself become memory.

## Earned focused mechanism
An explicitly recorded conversational episode is stored as exact Veya evidence with session ID, opaque counterpart ID, counterpart epoch, turn ID, utterance hash, and episode identity hash. The same Veya state can close/restart and later recall the prior-session utterance from bounded recent evidence.

## Epistemic ceiling
The recalled object is **a historical utterance event**, not a proposition Veya may treat as true. If the remembered utterance says `X`, Veya has evidence only that the counterpart uttered `X`. Truth/semantic commitment remain NONE.

Counterpart identity is also deliberately weak: an opaque experimental ID plus epoch. M01 does not earn human identity recognition, personhood continuity, social relationship semantics, or user-profile truth.

## Currentness / isolation
Wrong counterpart IDs do not recall. Counterpart epoch changes stale the old memory without deleting history. Same-session recall is blocked by default. Corrupt hashes fail closed. Generic/unowned evidence is not memory. External Echo transcript files are not auto-ingested. Retrieval is bounded to recent evidence and does not claim general memory search.

## What the embodiment taught us
The clean roadmap had prioritized analogy/schema composition; Echo pressure correctly identified conversational continuity as an immediate ecological bottleneck. The substrate could support a narrow memory mechanism without adding a parallel store or generic language model.
