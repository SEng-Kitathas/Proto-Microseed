from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from microseed.cognition.referents import OperationalReferentSignature
from microseed.development.action_learning import ExternalProjectionConditionedRelationQualifier
from microseed.development.capability_admission import ExternalCapabilityQualifier
from microseed.development.predictive_adaptation import PredictiveCurrentnessConfig
from microseed.development.rehearsal import CounterfactualRehearsalConfig
from research.substrate_shadow.environment_adapter import ShadowEnvironmentAdapter,AdapterConfig
from scratch.ms1997_lived_history_to_endogenous_program import MAIN
from scratch.ms1998_observable_context_assistance_removal import (
    ObservableContextWorld,_candidate_by_action,_close,qualify_relations_from_later_history,run_assisted_episode,
)
from scratch.ms2000_same_identity_capability_requalification import _effect,_fresh_support
from microseed.runtime.types import EpistemicStatus

PROBES=("Q0","Q1","Q2","Q3","Q4")
P_BOUNDARIES=((1,3),(1,3),(2,4),(2,4))
N_BOUNDARIES=((1,4),(1,4),(2,5),(2,5))
ALIASED_BOUNDARIES=((1,2),(1,2),(1,2),(1,2))


class UnifiedReferentLifetimeWorld(ObservableContextWorld):
    """One reality owner for regulatory outcomes and opaque referent probe channels."""
    name="MS2004-UNIFIED-REFERENT-LIFETIME-WORLD"

    def __init__(self)->None:
        super().__init__();self.referent_variant="MODE_BOUND";self._probe_step=0;self._referent=[0,0,0,0]

    def configure_referent_variant(self,variant:str)->None:
        if variant not in {"MODE_BOUND","ALIASED"}: raise ValueError("INVALID_REFERENT_VARIANT")
        self.referent_variant=variant

    def reset(self)->None:
        super().reset();self.reset_referent_probe()

    def reset_referent_probe(self)->None:
        self._probe_step=0;self._referent=[0,0,0,0]

    def _boundaries(self):
        if self.referent_variant=="ALIASED": return ALIASED_BOUNDARIES
        return P_BOUNDARIES if self.mode=="P" else N_BOUNDARIES

    def probe(self,opaque_probe_id:str)->dict[str,object]:
        if self._probe_step>=len(PROBES) or opaque_probe_id!=PROBES[self._probe_step]:
            raise RuntimeError("WORLD_REJECTED_OUT_OF_SEQUENCE_OPAQUE_PROBE")
        t=self._probe_step+1
        for i,b in enumerate(self._boundaries()):
            if t in b:self._referent[i]=1-self._referent[i]
        self._probe_step+=1
        return {"receipt":"opaque-probe-applied","probe_id":opaque_probe_id,"probe_step":self._probe_step}

    def observe_referent(self)->tuple[int,...]:
        return tuple(self._referent)


def _attach(root:Path,session:int):
    ms=Microseed(root);world=UnifiedReferentLifetimeWorld();adapter=ShadowEnvironmentAdapter(
        world,AdapterConfig(adapter_instance_id=f"MS2004-SESSION-{session}",viable_low=-.25,viable_high=.25))
    adapter.attach(ms)
    for capability_id in MAIN+(adapter.config.observation_capability_id,): ms.frames.bind_capability(adapter.config.frame_id,capability_id)
    return ms,world,adapter


def _probe_samples(world:UnifiedReferentLifetimeWorld)->tuple[tuple[int,...],...]:
    world.reset_referent_probe();rows=[world.observe_referent()]
    for probe in PROBES:
        world.probe(probe);rows.append(world.observe_referent())
    return tuple(rows)


def _sig(row:dict[str,object])->OperationalReferentSignature:
    return OperationalReferentSignature(
        "OPERATIONAL_REFERENT_SIGNATURE_DERIVED",str(row["signature_sha256"]),
        tuple((str(a),tuple(bool(x) for x in bits)) for a,bits in row["action_response_rows"]), # type: ignore[index]
        "AFFORDANCE_RELATIVE_BOUNDARY_RESPONSE_ONLY")


def _persist_mode_context(ms:Microseed,world:UnifiedReferentLifetimeWorld,mode:str)->dict[str,object]:
    world.configure_mode(mode);world.configure_referent_variant("MODE_BOUND");samples=_probe_samples(world)
    d=ms.derive_operational_referent_signatures_from_raw_trace(samples,PROBES)
    assert d["status"]=="OPERATIONAL_REFERENT_SIGNATURES_DERIVED_FROM_RAW_TRACE",d
    for i,row in enumerate(d["signature_classes"]):
        ms.record_operational_referent_signature(f"MS2004-REF-{mode}-{i}",_sig(row))
    c=ms.derive_current_operational_referent_class_set_context(samples,PROBES,max_records=256)
    assert c["status"]=="CURRENT_OPERATIONAL_REFERENT_SIGNATURE_CLASS_SET_CONTEXT",c
    return c


def _current_context(ms:Microseed,world:UnifiedReferentLifetimeWorld)->tuple[tuple[tuple[int,...],...],dict[str,object]]:
    samples=_probe_samples(world)
    c=ms.derive_current_operational_referent_class_set_context(samples,PROBES,max_records=256)
    return samples,c


def _routing_holdouts(ms:Microseed,projection,task:str,bucket:str,logs:list[dict[str,object]],prefix:str):
    refs=[]
    for i,row in enumerate(logs):
        refs.append(ms.append_evidence(f"MS2004-ROUTE-HOLD-{prefix}-{i}",{
            "kind":"PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT",
            "projection_id":projection.projection_id,"projection_epoch":projection.epoch,
            "projection_signature_sha256":projection.signature_sha256,"task_id":task,"horizon":1,
            "action_id":row["selected_action"],"channel_id":"opaque-control","projection_bucket_id":bucket,
            "actual_next_state_id":row["actual_next_state_id"],"actual_value_effect":row["actual_value_effect"],
        },EpistemicStatus.PRESSURE_SUPPORTED,source="MS2004-HSP-INDEPENDENT-HOLDOUT"))
    return tuple(refs)


def _qualify_referent_routing(ms:Microseed,projection,p_bucket:str,n_bucket:str,historical:dict[str,str],replacement:dict[str,str],p_logs,n_logs):
    task="MS2004-UNIFIED-REFERENT-CONTEXT"
    prop=ms.append_evidence("MS2004-ROUTE-PROP",{
        "kind":"ROUTING_PROPOSAL","basis":"PERSISTED_OPERATIONAL_SIGNATURE_CLASS_SET_CONTEXT",
        "caller_supplied_runtime_bucket":"NO","semantic_reference_authority":"NONE","identity_authority":"NONE",
    },EpistemicStatus.PRESSURE_SUPPORTED,source="MICROSEED-PROPOSAL")
    route=ms.nominate_projection_conditioned_relation_routing(
        projection_id=projection.projection_id,task_id=task,action_ids=MAIN,channel_ids=("opaque-control",),horizon=1,
        default_action_relations=tuple((a,historical[a]) for a in MAIN),
        bucket_action_overrides=tuple((n_bucket,a,replacement[a]) for a in MAIN),source_evidence_ids=(prop.evidence_id,))
    refs=_routing_holdouts(ms,projection,task,p_bucket,p_logs,"P")+_routing_holdouts(ms,projection,task,n_bucket,n_logs,"N")
    ticket=ExternalProjectionConditionedRelationQualifier(ms.evidence,qualifier_id="EXTERNAL-MS2004-UNIFIED-REFERENT-ROUTING").qualify(
        route,qualification_evidence=refs,relations=ms.action_outcome_learning.relations,min_support=24,min_accuracy=.95)
    admitted=ms.qualify_projection_conditioned_relation_routing(ticket)
    assert admitted["status"]=="CURRENT_PROJECTION_CONDITIONED_ROUTING",admitted
    return task,admitted["binding"]["binding_id"]


def _zero_row_unified_episode(ms:Microseed,adapter:ShadowEnvironmentAdapter,world:UnifiedReferentLifetimeWorld,*,mode:str,index:int,binding_id:str,task_id:str)->dict[str,object]:
    world.configure_mode(mode);world.configure_referent_variant("MODE_BOUND");world.reset();adapter.observe_control(ms,f"MS2004-ZERO-{index}-START")
    options=tuple(adapter.option(a) for a in MAIN);selected=[];buckets=[]
    for step in range(3):
        current=ms.action_closure.current_state;assert current is not None
        samples,context=_current_context(ms,world)
        assert context["status"]=="CURRENT_OPERATIONAL_REFERENT_SIGNATURE_CLASS_SET_CONTEXT",context
        proposal=ms.nominate_current_operational_referent_class_set_conditioned_rehearsal(
            (),options,samples,PROBES,start_state_id=current.state_id,value_id=adapter.config.value_id,
            projection_routing_id=binding_id,routing_task_id=task_id,routing_channel_id="opaque-control",
            max_records=256,config=CounterfactualRehearsalConfig(max_horizon=1,max_nodes=16))
        assert proposal is not None,(mode,step,context)
        intent=ms.nominate_bounded_action_intent(proposal.proposal_id,adapter.act_obligation())
        assert intent["status"]=="ACTION_INTENT_NOMINATED",intent
        action=intent["intent"]["capability_id"];assert action==MAIN[step],(mode,step,action)
        execution=adapter.execute_intent(ms,intent["intent"]["intent_id"]);assert execution["status"]=="ACTION_EXECUTED"
        out=adapter.record_execution_outcome(ms,execution["execution"]["execution_id"],evidence_id=f"MS2004-ZERO-OUT-{index}-{step}",capture_id=f"MS2004-ZERO-CAP-{index}-{step}")
        assert out["status"]=="ACTION_OUTCOME_OBSERVED",out
        selected.append(action);buckets.append(context["projection_bucket_id"])
    return {"selected_actions":selected,"buckets":buckets,"final_state":world.observe()["next_state_id"],"final_value":world.observe()["observed_value"],"supplied_rehearsal_rows":0}


def run_ms2004()->dict[str,object]:
    td=tempfile.TemporaryDirectory(prefix="ms2004-unified-referent-lifetime-");root=Path(td.name);receipts=[]
    historical={};replacement={};p_bucket=n_bucket=binding_id=task_id=""
    # S1: lived historical acquisition.
    ms,world,adapter=_attach(root,1)
    try:
        p_train=[]
        for i in range(12):p_train.extend(run_assisted_episode(ms,adapter,world,evaluator_mode="P",index=i,phase="MS2004-S1-P-TRAIN"))
        candidates=_candidate_by_action(ms);p_hold=[]
        for i in range(12):p_hold.extend(run_assisted_episode(ms,adapter,world,evaluator_mode="P",index=i,phase="MS2004-S1-P-HOLD"))
        historical=qualify_relations_from_later_history(ms,candidates,p_hold,prefix="MS2004-S1-P-REL")
        receipts.append({"session":1,"phase":"historical_acquisition","outcomes":len(ms.action_closure.outcomes)})
    finally:_close(ms)
    # S2: drift/relearning from real N outcomes.
    ms,world,adapter=_attach(root,2)
    try:
        n_drift=[]
        for i in range(16):n_drift.extend(run_assisted_episode(ms,adapter,world,evaluator_mode="N",index=i,phase="MS2004-S2-N-DRIFT"))
        repl={};dw={}
        for action in MAIN:
            assessed=ms.assess_action_outcome_predictive_currentness(historical[action],config=PredictiveCurrentnessConfig(window_size=8,min_accuracy=.75,consecutive_failure_windows=2))
            assert assessed["status"]=="DRIFT_WITNESS",assessed;dw[action]=assessed["witness"]["witness_id"]
            rows=ms.nominate_action_outcome_replacement_candidates(historical[action],dw[action],min_support=8,min_consistency=.78);assert len(rows)==1
            repl[action]=rows[0]
        n_hold=[]
        for i in range(12):n_hold.extend(run_assisted_episode(ms,adapter,world,evaluator_mode="N",index=i,phase="MS2004-S2-N-HOLD"))
        replacement=qualify_relations_from_later_history(ms,repl,n_hold,prefix="MS2004-S2-N-REL")
        receipts.append({"session":2,"phase":"drift_relearning","outcomes":len(ms.action_closure.outcomes)})
    finally:_close(ms)
    # S3: same external world supplies operational referent probes and routing holdout outcomes.
    ms,world,adapter=_attach(root,3)
    try:
        pc=_persist_mode_context(ms,world,"P");nc=_persist_mode_context(ms,world,"N")
        p_bucket=str(pc["projection_bucket_id"]);n_bucket=str(nc["projection_bucket_id"]);assert p_bucket!=n_bucket
        projection=ms.register_epistemic_projection("MS2004-UNIFIED-REFSET",ms.operational_referent_class_set_projection_signature_sha256(),assistance_ancestry=("SUPPLIED_OPAQUE_OPERATIONAL_SIGNATURE_CLASS_SET_COORDINATE","NO_SEMANTIC_REFERENCE_AUTHORITY"))
        p_logs=[];n_logs=[]
        for i in range(12):
            p_logs.extend(run_assisted_episode(ms,adapter,world,evaluator_mode="P",index=i,phase="MS2004-S3-ROUTE-P"))
            n_logs.extend(run_assisted_episode(ms,adapter,world,evaluator_mode="N",index=i,phase="MS2004-S3-ROUTE-N"))
        task_id,binding_id=_qualify_referent_routing(ms,projection,p_bucket,n_bucket,historical,replacement,p_logs,n_logs)
        receipts.append({"session":3,"phase":"referent_persistence_and_routing","p_bucket":p_bucket,"n_bucket":n_bucket,"outcomes":len(ms.action_closure.outcomes)})
    finally:_close(ms)
    # S4: zero-row policy after restart + co-present capability requalification.
    ms,world,adapter=_attach(root,4)
    try:
        rq=_effect("MS2004-RQ");ms.register_capability(rq);sig=ms.capabilities.contracts["MS2004-RQ"].computed_signature_sha256();auth=ms.capabilities.contracts["MS2004-RQ"].authority.value
        ms.invalidate_capability("MS2004-RQ",reason="MS2004-LIFETIME-DRIFT");epoch=ms.capabilities.epochs["MS2004-RQ"]
        ticket=ExternalCapabilityQualifier(ms.evidence,qualifier_id="MS2004-HSP-EXTERNAL").requalify(ms.capabilities.contracts["MS2004-RQ"],stale_epoch=epoch,qualification_evidence=(_fresh_support(ms,"MS2004-RQ-SUPPORT"),))
        ms.requalify_capability(ticket);assert ms.capabilities.contracts["MS2004-RQ"].computed_signature_sha256()==sig and ms.capabilities.contracts["MS2004-RQ"].authority.value==auth
        zp=_zero_row_unified_episode(ms,adapter,world,mode="P",index=0,binding_id=binding_id,task_id=task_id)
        zn=_zero_row_unified_episode(ms,adapter,world,mode="N",index=1,binding_id=binding_id,task_id=task_id)
        assert zp["selected_actions"]==zn["selected_actions"]==list(MAIN)
        assert zp["final_state"]=="u" and zn["final_state"]=="v" and zp["final_value"]==zn["final_value"]==0.0
        assert set(zp["buckets"])=={p_bucket} and set(zn["buckets"])=={n_bucket}
        # Same world, ambiguous referent surface: no policy should be formed.
        world.configure_mode("P");world.configure_referent_variant("ALIASED");world.reset();adapter.observe_control(ms,"MS2004-ALIASED-START")
        samples=_probe_samples(world);opts=tuple(adapter.option(a) for a in MAIN);current=ms.action_closure.current_state;assert current is not None
        blocked=ms.nominate_current_operational_referent_class_set_conditioned_rehearsal((),opts,samples,PROBES,start_state_id=current.state_id,value_id=adapter.config.value_id,projection_routing_id=binding_id,routing_task_id=task_id,routing_channel_id="opaque-control",max_records=256,config=CounterfactualRehearsalConfig(max_horizon=1,max_nodes=16))
        assert blocked is None
        receipts.append({"session":4,"phase":"zero_row_unified_policy","zero_p":zp,"zero_n":zn,"aliased_policy":"NONE"})
        return {
            "status":"PASS","sessions":receipts,"historical_relations":historical,"replacement_relations":replacement,
            "p_bucket":p_bucket,"n_bucket":n_bucket,"routing_binding_id":binding_id,"zero_p":zp,"zero_n":zn,
            "same_world_owns_control_and_referent_observations":"YES","restart_count":3,"session_count":4,
            "drift_relearning":"YES","persisted_referent_class_reentry":"YES","zero_row_policy":"YES",
            "ambiguous_referent_policy":"NONE","capability_requalification_co_present":"YES","capability_requalification_authority_gain":"NONE",
            "caller_supplied_runtime_bucket":"NO","caller_supplied_referent_class":"NO","caller_supplied_preferred_action":"NO",
            "identity_authority":"NONE","semantic_reference_authority":"NONE","truth_authority":"NONE",
            "new_cross_cutting_manager":"NO","new_referent_manager":"NO","new_policy_manager":"NO",
            "remaining_assistance":"FIXED_EXTERNALLY_EQUIPPED_OPAQUE_REFERENT_PROBE_SCHEDULE_PLUS_EXTERNAL_RELATION_AND_ROUTING_QUALIFICATION_AND_FRESH_SESSION_ENVIRONMENT_AUTHORITY",
            "remaining_boundary":"PROBE_SCHEDULE_SELECTION_NOT_ENDOGENOUS_AND_GENERAL_RICH_WORLD_AUTONOMY_NOT_PROVEN",
            "earned":"FOUR_SESSION_UNIFIED_EXTERNAL_LIFETIME_COMPOSES_DRIFT_RELEARNING_RESTART_CURRENTNESS_PERSISTED_OPERATIONAL_REFERENT_CLASS_PRESSURE_ZERO_ROW_DECISION_POLICY_AMBIGUITY_REFUSAL_AND_CO_PRESENT_CAPABILITY_REQUALIFICATION_WITHOUT_A_NEW_REFERENT_POLICY_OR_LIFECYCLE_MANAGER",
        }
    finally:_close(ms);td.cleanup()


def main()->None:print(json.dumps(run_ms2004(),indent=2,sort_keys=True,default=str))
if __name__=="__main__":main()
