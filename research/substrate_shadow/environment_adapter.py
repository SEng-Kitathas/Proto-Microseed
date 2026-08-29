from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Callable

from microseed import (
    Authority, CapabilityContract, EpisodeSchemaContract, EpistemicStatus,
    ExternalActionOutcomeRelationQualifier, FeasibilityState, Microseed,
    Observation, OperationalFrameContract, QualificationState, QueryObligation,
    RecruitmentOption, RehearsalTransitionObservation, ValueVariableContract,
)


class ExternalWorld(Protocol):
    """Research-side world contract. It owns reality; Microseed does not."""
    name: str
    action_ids: tuple[str, ...]
    compatibility_sha256: str

    def reset(self) -> None: ...
    def apply(self, action_id: str) -> dict: ...
    def observe(self) -> dict: ...
    def fork(self) -> "ExternalWorld": ...


@dataclass(frozen=True)
class AdapterConfig:
    adapter_instance_id: str = "ADAPTER-0"
    scope_id: str = "SUBSTRATE-SCOPE"
    frame_id: str = "SUBSTRATE-FRAME"
    episode_id: str = "SUBSTRATE-EPISODE"
    value_id: str = "SUBSTRATE-VALUE"
    observation_capability_id: str = "SUBSTRATE-OBSERVE"
    observation_basis_id: str = "SUBSTRATE-OBS-BASIS"
    environment_binding_basis_id: str = "SUBSTRATE-ENV-BINDING"
    viable_low: float = 2.0
    viable_high: float = 3.0


class ShadowEnvironmentAdapter:
    """External shadow adapter for reality pressure; grants no organism authority by itself."""
    def __init__(self, world: ExternalWorld, config: AdapterConfig | None = None):
        self.world = world
        self.config = config or AdapterConfig()

    def act_obligation(self) -> QueryObligation:
        return QueryObligation("SUBSTRATE-ACT", "opaque environment effect", Authority.EFFECT, operational_scope_id=self.config.scope_id)

    def obs_obligation(self) -> QueryObligation:
        return QueryObligation("SUBSTRATE-OBS-Q", "opaque environment observation", Authority.OBSERVATION_ONLY, operational_scope_id=self.config.scope_id)

    def basis_obligation(self) -> QueryObligation:
        return QueryObligation("SUBSTRATE-BASIS-Q", "bounded observation basis", Authority.DERIVED_READ_ONLY, operational_scope_id=self.config.scope_id)

    def environment_binding_obligation(self) -> QueryObligation:
        return QueryObligation("SUBSTRATE-ENV-BIND-Q", "current environment compatibility basis", Authority.DERIVED_READ_ONLY, operational_scope_id=self.config.scope_id)

    def attach(self, ms: Microseed) -> None:
        c=self.config
        ms.register_operational_frame(OperationalFrameContract(c.frame_id,"environment-neutral-shadow-frame","f"*64,Authority.DERIVED_READ_ONLY,("MS1949",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=("EXTERNAL_WORLD_FRAME",)))
        ms.register_value_variable(ValueVariableContract(c.value_id,"environment-regulatory-coordinate",c.viable_low,c.viable_high,"v"*64,Authority.DERIVED_READ_ONLY,("MS1949",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=("EXTERNAL_WORLD_VALUE_COORDINATE","SUPPLIED_VIABILITY_INTERVAL")))
        self.world.reset(); obs=self.world.observe(); ms.observe_value_state(c.value_id,float(obs["observed_value"]))
        for action_id in self.world.action_ids:
            def handler(_aid=action_id, **_): return self.world.apply(_aid)
            ms.register_capability(CapabilityContract(action_id,"environment-effect",{}, {"output":"opaque-effect-receipt"},("WORLD_ADAPTER_EFFECT != WORLD_MODEL","NO_SEMANTIC_GOAL_AUTHORITY"),(),Authority.EFFECT,("MS1949",),"CURRENT",{},query_obligation_id="SUBSTRATE-ACT",qualification=QualificationState.SHADOW_QUALIFIED,handler=handler,operational_scope_id=c.scope_id,assistance_ancestry=("EXTERNAL_WORLD_EFFECT_CAPABILITY",)))
        ms.register_capability(CapabilityContract(c.observation_capability_id,"environment-observation",{}, {"output":"opaque-world-observation"},("OBSERVATION != TRUTH_AUTHORITY",),(),Authority.OBSERVATION_ONLY,("MS1949",),"CURRENT",{},query_obligation_id="SUBSTRATE-OBS-Q",qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{**self.world.observe(),"value_id":c.value_id},operational_scope_id=c.scope_id))
        ms.register_capability(CapabilityContract(c.observation_basis_id,"bounded-observation-basis",{}, {},("NO_TRUTH_AUTHORITY",),(),Authority.DERIVED_READ_ONLY,("MS1949",),"CURRENT",{},dependencies=(c.observation_capability_id,),query_obligation_id="SUBSTRATE-BASIS-Q",qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{"claim":"BOUNDED_USE_ONLY"},operational_scope_id=c.scope_id))
        fp=str(getattr(self.world,"compatibility_sha256","")).lower()
        if len(fp)!=64 or any(ch not in "0123456789abcdef" for ch in fp):
            raise ValueError("EXTERNAL_WORLD_COMPATIBILITY_SHA256_REQUIRED")
        premise_ids=tuple(self.world.action_ids)+(c.observation_capability_id,c.observation_basis_id)
        premise_sigs=tuple((cid,ms.capabilities.contracts[cid].computed_signature_sha256()) for cid in premise_ids)
        ms.register_capability(CapabilityContract(
            capability_id=c.environment_binding_basis_id,
            purpose="environment-compatibility-admission-basis",
            boundary={
                "environment_compatibility_sha256":fp,
                "admission_premise_signatures":[list(x) for x in premise_sigs],
            },
            interface={},
            invariants=(
                "SAME_ADAPTER_INTERFACE != SAME_ENVIRONMENT_DYNAMICS",
                "ENVIRONMENT_COMPATIBILITY_BASIS != TRUTH_AUTHORITY",
                "ENVIRONMENT_COMPATIBILITY_BASIS != EXECUTION_AUTHORITY",
            ),
            hazards=(), authority=Authority.DERIVED_READ_ONLY, lineage=("MS1952",),
            currentness="CURRENT", resources={}, dependencies=premise_ids,
            query_obligation_id="SUBSTRATE-ENV-BIND-Q",
            qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda **_:{"claim":"CURRENT_ENVIRONMENT_COMPATIBILITY_BASIS","compatibility_sha256":fp},
            operational_scope_id=c.scope_id,
            assistance_ancestry=("EXTERNALLY_DECLARED_ENVIRONMENT_COMPATIBILITY_FINGERPRINT",),
        ))
        ms.register_episode_schema(EpisodeSchemaContract(c.episode_id,"environment-episode","e"*64,Authority.DERIVED_READ_ONLY,("MS1949",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=((c.frame_id,0),),value_epochs=((c.value_id,0),)))
        self.observe_control(ms,"ATTACH")

    def observe_control(self, ms: Microseed, tag: str) -> dict:
        c=self.config; obs=self.world.observe()
        ms.observe_value_state(c.value_id,float(obs["observed_value"]))
        ms.observe_opaque_control_state(Observation(f"{self.world.name}-{c.adapter_instance_id}-{tag}","EXTERNAL-WORLD","opaque-control",str(obs["next_state_id"]),authority=Authority.OBSERVATION_ONLY),evidence_id=f"E-{self.world.name}-{c.adapter_instance_id}-{tag}")
        return obs

    def reset_control(self, ms: Microseed, tag: str) -> dict:
        self.world.reset(); return self.observe_control(ms,tag)

    def _external_probe(self, action_id: str) -> dict:
        probe=self.world.fork(); probe.reset(); probe.apply(action_id); return probe.observe()

    def equipped_seed_rows(self, action_id: str, n: int = 12) -> tuple[RehearsalTransitionObservation,...]:
        """Explicit external equipment: one separately generated world probe supplies a seed prediction."""
        c=self.config; before=self.world.fork(); before.reset(); start=before.observe(); after=self._external_probe(action_id)
        effect=float(after["observed_value"])-float(start["observed_value"])
        return tuple(RehearsalTransitionObservation(f"MS1949-SEED-{self.world.name}-{action_id}-{i}",str(start["next_state_id"]),action_id,str(after["next_state_id"]),effect,0,c.frame_id,0,c.episode_id,0) for i in range(n))

    def option(self, action_id: str) -> RecruitmentOption:
        return RecruitmentOption(action_id,FeasibilityState.FEASIBLE,local_cost=0.1)

    def record_execution_outcome(self, ms: Microseed, execution_id: str, *, evidence_id: str, capture_id: str) -> dict:
        c=self.config
        return ms.record_bounded_action_outcome_via_observation_basis(
            execution_id,
            observation_capability_id=c.observation_capability_id,
            observation_obligation=self.obs_obligation(),
            basis_capability_id=c.observation_basis_id,
            basis_obligation=self.basis_obligation(),
            admission_basis_capability_id=c.environment_binding_basis_id,
            admission_basis_obligation=self.environment_binding_obligation(),
            evidence_id=evidence_id,
            capture_id=capture_id,
        )

    def train_actual_history(self, ms: Microseed, action_id: str, n: int = 12) -> tuple[str, dict]:
        c=self.config; rows=self.equipped_seed_rows(action_id,n)
        start=self.world.fork(); start.reset(); start_obs=start.observe()
        p=ms.nominate_counterfactual_rehearsal(rows,(self.option(action_id),),start_state_id=str(start_obs["next_state_id"]),value_id=c.value_id)
        if p is None: raise AssertionError("equipped seed proposal unavailable")
        for i in range(n):
            self.reset_control(ms,f"TRAIN-{action_id}-{i}")
            intent=ms.nominate_bounded_action_intent(p.proposal_id,self.act_obligation()); assert intent["status"]=="ACTION_INTENT_NOMINATED"
            ex=ms.execute_bounded_action(intent["intent"]["intent_id"],self.act_obligation()); assert ex["status"]=="ACTION_EXECUTED"
            out=self.record_execution_outcome(ms,ex["execution"]["execution_id"],evidence_id=f"E-{self.world.name}-{c.adapter_instance_id}-{action_id}-{i}",capture_id=f"CAP-{self.world.name}-{c.adapter_instance_id}-{action_id}-{i}")
            assert out["status"]=="ACTION_OUTCOME_OBSERVED", out
        candidates=[x for x in ms.nominate_action_outcome_predictive_candidates() if x.capability_id==action_id]
        if len(candidates)!=1: raise AssertionError(f"expected one candidate for {action_id}, got {len(candidates)}")
        candidate=candidates[0]
        refs=[]
        for i in range(16):
            probe=self.world.fork(); probe.reset(); before=probe.observe(); probe.apply(action_id); after=probe.observe()
            base={"kind":"ACTION_OUTCOME_HOLDOUT","start_state_id":candidate.start_state_id,"capability_id":candidate.capability_id,"capability_epoch":candidate.capability_epoch,"frame_epochs":[list(x) for x in candidate.frame_epochs],"episode_schema_epochs":[list(x) for x in candidate.episode_schema_epochs],"value_epoch":list(candidate.value_epoch),"topology_epochs":[list(x) for x in candidate.topology_epochs],"coordination_epochs":[list(x) for x in candidate.coordination_epochs],"evidence_premise_epochs":[list(x) for x in candidate.evidence_premise_epochs],"evidence_premise_signatures":[list(x) for x in candidate.evidence_premise_signatures]}
            refs.append(ms.append_evidence(f"HOLDOUT-{self.world.name}-{c.adapter_instance_id}-{action_id}-{i}",{**base,"actual_next_state_id":str(after["next_state_id"]),"actual_value_effect":float(after["observed_value"])-float(before["observed_value"]),"holdout_index":i},EpistemicStatus.PRESSURE_SUPPORTED,source="EXTERNAL-WORLD-HOLDOUT"))
        ticket=ExternalActionOutcomeRelationQualifier(ms.evidence,qualifier_id=f"SHADOW-WORLD-{self.world.name}").qualify(candidate,qualification_evidence=tuple(refs))
        q=ms.qualify_action_outcome_predictive_relation(ticket); assert q["status"]=="CURRENT_PREDICTIVE_RELATION"
        return q["relation"]["relation_id"], candidate.serializable()

    def zero_row_rehearsal(self, ms: Microseed, action_id: str):
        c=self.config; start=self.reset_control(ms,f"ZERO-{action_id}")
        return ms.nominate_counterfactual_rehearsal((),(self.option(action_id),),start_state_id=str(start["next_state_id"]),value_id=c.value_id)
