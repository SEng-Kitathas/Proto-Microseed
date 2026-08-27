# Proto-Microseed Main-Dev Operating Profile v2.8

Extends v2.7 only at the MS1478–1502 composition-ancestry seam.

- Reuses the existing `OperationalTrace → residual discovery → CapabilityCandidate → external qualification → CapabilityRegistry` lineage.
- Adds **no new core relation, multi-child planner, state registry, semantic child-role ontology, or qualification subsystem**.
- Operational traces may bind only already-current recruitment topology, opaque-counterparty, and coordination relations.
- A bound recruitment topology must also contain at least one qualified relation edge wholly present in the executed trace steps; current-but-unrelated topology is rejected as false ancestry.
- Coordination bindings inherit their already-declared participant-counterparty ancestry.
- Recurrent candidate discovery requires uniform current topology/counterparty/coordination epoch ancestry across the supporting traces.
- Discovered composite candidates preserve those epoch families in the existing `operational_signature`; admission uses the already-existing epoch validation path.
- Drift after qualification but before admission blocks admission; bound drift after admission selectively stales the composite without laundering child/global authority.
- Preserves `LOCAL_GREEN != COMPOSITIONAL_GREEN`, `DERIVED_COMPOSITION != QUALIFIED_COMPOSITION`, and `PAIRWISE_SUCCESS != HIGHER_ORDER_COMPLETENESS`.
- Hard stop: MS1503 not started.
- Selected breadth frontier: persistent rich online hostile whole-organism embodiment under noise, partial observability, drift, and hard resource bounds.
