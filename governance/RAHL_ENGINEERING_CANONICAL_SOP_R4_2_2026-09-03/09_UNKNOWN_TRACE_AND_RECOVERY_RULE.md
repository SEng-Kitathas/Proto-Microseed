# 09 — Unknown, Trace, and Recovery Rule

When work exposes something unclear, contradictory, partly visible, or present only through traces whose meaning/origin cannot be established, do not guess, smooth the gap away, invent provenance, or silently route around it.

Required order:
1. **Inspect first.** Search available local project state, version control, files, receipts, logs, manifests, execution state, and other evidence surfaces.
2. **Separate known from unknown.** Label verified, observed, inferred, and unknown portions.
3. **Ask when the remaining unknown is load-bearing.** If it could change architecture, authority, evidence meaning, mutation safety, execution interpretation, project direction, or lawful next action, ask the authority that owns the missing information.
4. **Ask on unexplained traces.** Do not treat an unidentified artifact, dependency, prior action, external input, or state as understood merely because traces exist.
5. **Do not ask for already-persisted history.** Recovery should first use durable state; questions are for genuinely missing/load-bearing gaps.
6. **Use reversible information-buying action when safe.** Bounded, observable, non-destructive probes are lawful when they cannot alter load-bearing state or erase evidence. If the probe itself changes the decision surface, qualify/authorize it first.

Compact form:
> **Inspect first. If a load-bearing unknown remains, ASK. If you see traces you cannot identify, ASK. Never guess across the gap.**

`TRACE_PRESENT != TRACE_UNDERSTOOD`
`UNKNOWN != PERMISSION_TO_INVENT`
`ZERO_REEXPLANATION != NEVER_ASK`
