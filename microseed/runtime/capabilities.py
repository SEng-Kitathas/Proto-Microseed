from __future__ import annotations
from typing import Any, Callable
from .types import Authority, CapabilityContract, QualificationState, QueryObligation


InvalidationCallback = Callable[[str, set[str], str], None]


class CapabilityRegistry:
    """Qualified capability registry with transitive currentness.

    MS841-843 exposed an integration mismatch: direct capability metadata only
    staled one dependency edge while DevelopmentRegistry already propagated
    invalidation transitively. The registry now maintains the same transitive
    semantics. Recursive composition was already conservative; metadata now
    agrees with executable currentness instead of depending on that accidental
    safety net.
    """

    def __init__(self, *, on_invalidate: InvalidationCallback | None = None):
        self.contracts: dict[str, CapabilityContract] = {}
        self.epochs: dict[str, int] = {}
        self.reverse_deps: dict[str, set[str]] = {}
        self._on_invalidate = on_invalidate

    def assess_dependency_closure(self, capability_id: str) -> dict[str, Any]:
        """Assess executable currentness through the declared capability graph.

        Structural registration may contain forward references and cycles.  Those
        shapes are not declared false merely because they are unresolved.  This
        ephemeral assessment answers the narrower operational question: can this
        capability be used *now* from a fully registered/current dependency closure?

        The traversal is iterative and memoized per call so wide/deep graphs do not
        require recursive Python stack growth.  A cycle without a separately qualified
        closure mechanism fails closed for executable currentness; it is not promoted
        to a universal claim that cycles are invalid.
        """
        root = str(capability_id)
        if root not in self.contracts:
            return {
                "status": "UNKNOWN_INCOMPLETE", "reason": f"CAPABILITY_NOT_FOUND:{root}",
                "capability_id": root, "visited_count": 0, "edge_count": 0,
                "max_depth": 0, "cycle": (), "authority": Authority.NONE.value,
            }

        done: set[str] = set()
        active_index: dict[str, int] = {}
        path: list[str] = []
        # stack rows are [capability_id, next_dependency_index]
        stack: list[list[Any]] = [[root, 0]]
        visited_count = 0
        edge_count = 0
        max_depth = 1

        while stack:
            cid = str(stack[-1][0])
            next_index = int(stack[-1][1])
            if next_index == 0:
                current = self.contracts.get(cid)
                if current is None:
                    return {
                        "status": "UNKNOWN_INCOMPLETE",
                        "reason": f"DEPENDENCY_NOT_REGISTERED:{cid}",
                        "capability_id": root, "visited_count": visited_count,
                        "edge_count": edge_count, "max_depth": max_depth,
                        "cycle": (), "authority": Authority.NONE.value,
                    }
                if current.qualification not in {QualificationState.QUALIFIED, QualificationState.SHADOW_QUALIFIED} or current.currentness != "CURRENT":
                    return {
                        "status": "UNKNOWN_INCOMPLETE",
                        "reason": f"DEPENDENCY_NOT_CURRENT:{cid}:{current.qualification.value}:{current.currentness}",
                        "capability_id": root, "visited_count": visited_count,
                        "edge_count": edge_count, "max_depth": max_depth,
                        "cycle": (), "authority": Authority.NONE.value,
                    }
                active_index[cid] = len(path)
                path.append(cid)
                visited_count += 1

            current = self.contracts[cid]
            deps = tuple(current.dependencies)
            if next_index >= len(deps):
                stack.pop()
                active_index.pop(cid, None)
                if path and path[-1] == cid:
                    path.pop()
                done.add(cid)
                continue

            dep = str(deps[next_index])
            stack[-1][1] = next_index + 1
            edge_count += 1
            if dep in done:
                continue
            if dep in active_index:
                start = active_index[dep]
                cycle = tuple(path[start:] + [dep])
                return {
                    "status": "UNKNOWN_INCOMPLETE",
                    "reason": "DEPENDENCY_CYCLE_UNQUALIFIED:" + "->".join(cycle),
                    "capability_id": root, "visited_count": visited_count,
                    "edge_count": edge_count, "max_depth": max_depth,
                    "cycle": cycle, "authority": Authority.NONE.value,
                }
            if dep not in self.contracts:
                return {
                    "status": "UNKNOWN_INCOMPLETE",
                    "reason": f"DEPENDENCY_NOT_REGISTERED:{dep}",
                    "capability_id": root, "visited_count": visited_count,
                    "edge_count": edge_count, "max_depth": max_depth,
                    "cycle": (), "authority": Authority.NONE.value,
                }
            stack.append([dep, 0])
            max_depth = max(max_depth, len(stack))

        return {
            "status": "CURRENT_DEPENDENCY_CLOSURE", "reason": "CURRENT",
            "capability_id": root, "visited_count": visited_count,
            "edge_count": edge_count, "max_depth": max_depth,
            "cycle": (), "authority": Authority.NONE.value,
        }

    def is_locally_current(self, capability_id: str) -> bool:
        """Return only this contract's own qualification/currentness metadata.

        This deliberately does not traverse dependencies.  It exists for owner-specific
        diagnostics where local staleness must remain distinguishable from transitive
        unusability.  Executable use must continue to call ``is_current``/``invoke``.
        """
        current = self.contracts.get(str(capability_id))
        return bool(
            current is not None
            and current.qualification in {QualificationState.QUALIFIED, QualificationState.SHADOW_QUALIFIED}
            and current.currentness == "CURRENT"
        )

    def is_current(self, capability_id: str) -> bool:
        return self.assess_dependency_closure(capability_id)["status"] == "CURRENT_DEPENDENCY_CLOSURE"

    def register(self, contract: CapabilityContract) -> None:
        if contract.capability_id in self.contracts:
            raise ValueError(f"duplicate capability: {contract.capability_id}")
        self.contracts[contract.capability_id] = contract
        self.epochs[contract.capability_id] = 0
        for dep in contract.dependencies:
            self.reverse_deps.setdefault(dep, set()).add(contract.capability_id)

    def invalidate(self, capability_id: str, *, reason: str = "DEPENDENCY_CHANGED") -> set[str]:
        """Stale a changed capability and all transitive dependents.

        History is not deleted and rejection is not rewritten as staleness.
        CANDIDATE/RESEARCH/SHADOW/QUALIFIED structures all require requalification
        if a prerequisite in their declared dependency graph changes.
        """
        stale: set[str] = set()
        queue = [capability_id]
        while queue:
            cid = queue.pop()
            if cid in stale:
                continue
            stale.add(cid)
            c = self.contracts.get(cid)
            if c is not None and c.qualification != QualificationState.REJECTED:
                c.qualification = QualificationState.STALE
                c.currentness = "STALE"
            queue.extend(sorted(self.reverse_deps.get(cid, ())))
        if self._on_invalidate is not None:
            self._on_invalidate(capability_id, stale, reason)
        return stale

    def change_dependency(self, capability_id: str, *, reason: str = "DEPENDENCY_CHANGED") -> set[str]:
        self.epochs[capability_id] = self.epochs.get(capability_id, 0) + 1
        return self.invalidate(capability_id, reason=reason)

    def invoke(self, capability_id: str, obligation: QueryObligation, **kwargs: Any) -> dict[str, Any]:
        c = self.contracts.get(capability_id)
        if c is None:
            return {"status": "NO_PATH", "authority": Authority.NONE.value}
        closure = self.assess_dependency_closure(capability_id)
        if closure["status"] != "CURRENT_DEPENDENCY_CLOSURE":
            return {"status": "UNKNOWN_INCOMPLETE", "reason": closure["reason"],
                    "dependency_closure": closure, "authority": Authority.NONE.value}
        if c.query_obligation_id and c.query_obligation_id != obligation.obligation_id:
            return {"status": "UNKNOWN_INCOMPLETE", "reason": "QUERY_OBLIGATION_MISMATCH",
                    "authority": Authority.NONE.value}
        if c.operational_scope_id and c.operational_scope_id != obligation.operational_scope_id:
            return {"status": "UNKNOWN_INCOMPLETE", "reason": "OPERATIONAL_SCOPE_MISMATCH",
                    "authority": Authority.NONE.value}
        if c.handler is None:
            return {"status": "UNKNOWN_INCOMPLETE", "reason": "NO_HANDLER",
                    "authority": Authority.NONE.value}
        value = c.handler(**kwargs)
        return {"status": "CAPABILITY_RESULT", "capability_id": capability_id,
                "authority": c.authority.value, "value": value}

    def snapshot(self) -> dict[str, Any]:
        return {k: v.serializable() for k, v in sorted(self.contracts.items())}
