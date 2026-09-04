# 07B — Design Thread Stream Protocol

Purpose: preserve chronological recovery fidelity.

After each meaningful exchange or state-changing event:
- append user/operator input and assistant/system response or highest-fidelity practical representation;
- preserve chronology and speaker/source attribution;
- tag state changes, decisions, failures, checkpoints, and artifact pointers when useful;
- compress only as necessary, never so far that reversals, rule changes, failures, or causal sequence become unrecoverable.

Fidelity priority: chronology -> attribution -> content -> state-change recoverability -> compactness.

The Design Thread Stream SHOULD interpret minimally. Interpretation belongs primarily in Live Shadow, RES, Doctrine Snapshot, and Trace Matrix.
