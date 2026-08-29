# MS1970 — Affordance Split Does Not Establish Genealogy

Date: 2026-08-29 ET
Status: negative genealogy/identity boundary; operational decomposition survives
Parent: MS1969 `02d9e88fdea3ad47882e2369c6d72c28bbfe587f`

## Discriminator
If one distinguishable operational referent's affordance response later decomposes into two distinguishable current referent responses, does that evidence establish a genealogical split or numerical identity inheritance?

Prewrite:
`AFFORDANCE_DECOMPOSITION != GENEALOGICAL_SPLIT`.

## First nonresult
Initial world exposed only the parent referent before transition. All parent channels were globally synchronous, so existing `nominate_by_boundary_coherence(...)` correctly returned:
`UNKNOWN_INCOMPLETE / BOUNDARY_SYNCHRONY_DOES_NOT_IDENTIFY_DISTINCT_REFERENTS`.

This did not test split continuity. It showed that a single globally synchronous channel group cannot be promoted to a distinct referent merely because the harness intends it to be one.

The world was strengthened with an unrelated background referent, allowing the target parent to be distinguished without supplied grouping.

A second run reached the intended partition but the scratch evaluator incorrectly assumed one occurrence per action; repeated `FX-N` made that a harness nonresult. Response algebra was corrected to preserve the full per-action boolean tuple and compare decomposition position-by-position.

Neither nonresult was counted as scientific evidence for or against the split hypothesis.

## Reality world
`research/substrate_shadow/referent_split_world_server.py`

Pre-transition:
- target parent group responds to both `FX-L` and `FX-R`;
- unrelated background group responds to `FX-BG`.

Post-transition:
- one current child group responds only to `FX-L`;
- another responds only to `FX-R`;
- background remains separately distinguishable.

Two evaluator-only variants expose exactly the same operational observations:
1. genuine split: child lineage points to the parent generation;
2. hidden replacement: two new same-affordance children appear with no parent lineage.

## Result
Scratch:
`scratch/ms1970_affordance_split_not_genealogy.py`

Final durable job:
`job-0a31d88e8608`

Result: `BOUNDARY_CONFIRMED`, rc=0.

Parent target response:
- `FX-L -> (True,)`;
- `FX-R -> (True,)`;
- `FX-BG -> (False,)`;
- `FX-N -> (False,False)`.

Current child responses:
- child L: only `FX-L` true;
- child R: only `FX-R` true.

The per-action OR of the two child response tuples equals the parent response tuple exactly.

However, genuine-split and hidden-replacement variants produce identical:
- parent groups/signatures;
- child groups/signatures;
- child response rows;
- parent→children affordance decomposition.

Only evaluator-hidden lineage differs.

Earned:
`PARENT_AFFORDANCE_CAN_DECOMPOSE_INTO_MULTIPLE_CURRENT_CHILD_AFFORDANCES_WITHOUT_ESTABLISHING_GENEALOGICAL_SPLIT_OR_IDENTITY_INHERITANCE`.

## Authority ceiling
- affordance decomposition authority: `OPERATIONAL_RELATION_ONLY`;
- genealogy authority: NONE;
- numerical identity inheritance authority: NONE;
- semantic reference authority: NONE;
- language authority: NONE.

## Architectural consequence
No new Microseed referent manager or genealogy owner is justified by this evidence.

Existing operational signatures are sufficient to expose the one-to-many affordance decomposition. They are deliberately insufficient to claim where the current children came from.

A later language layer may express an operational decomposition only if it preserves this scope. Words like "split", "same", "child", or "became" carry stronger genealogical/identity semantics and require additional continuity evidence before they can be asserted as world truth.

## Next scientific seam
The proto-reference program now has explicit boundaries for:
- noisy calibrated frame currentness;
- cross-frame handoff continuity;
- no-overlap re-association;
- hidden substitution;
- one-to-many affordance decomposition vs genealogy.

The next highest-value question should move toward what evidence can lawfully strengthen operational re-association into persistence/identity claims, or toward open representational growth if numerical identity is not required for the first bounded language gate.