from __future__ import annotations
import hashlib, json, random, tempfile
from pathlib import Path
from microseed import Authority, CapabilityContract, EpisodeSchemaContract, Microseed, Observation, OperationalFrameContract, QualificationState, QueryObligation, ValueVariableContract
from microseed.development.discovery import OperationalTrace

VALUES=("ENERGY","THERMAL","INTEGRITY")
BOUNDS={"ENERGY":(4.,8.),"THERMAL":(3.,7.),"INTEGRITY":(4.,9.5)}
EFFECTS={"HARVEST":(1.55,.42,-.28),"COOL":(-.28,-1.48,-.12),"REPAIR":(-.38,.22,1.42),"REST":(.42,-.44,.34)}

def obligation(): return QueryObligation("ACT","bounded-hostile-effect",required_authority=Authority.EFFECT,operational_scope_id="R2")

def seeded(root:Path):
    ms=Microseed(root); calls=[]
    ms.register_operational_frame(OperationalFrameContract("F","opaque-regulatory-frame",hashlib.sha256(b'F').hexdigest(),Authority.DERIVED_READ_ONLY,("MS1578-P1",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED))
    for vid in VALUES:
        lo,hi=BOUNDS[vid]
        ms.register_value_variable(ValueVariableContract(vid,"opaque-regulatory",lo,hi,hashlib.sha256(f'{vid}:{lo}:{hi}'.encode()).hexdigest(),Authority.DERIVED_READ_ONLY,("MS953-977",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=("SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE","SUPPLIED_VIABILITY_INTERVAL")))
        sid=f"E-{vid}"
        ms.register_episode_schema(EpisodeSchemaContract(sid,"opaque-single-value-effect-binding",hashlib.sha256(sid.encode()).hexdigest(),Authority.DERIVED_READ_ONLY,("MS1103-1127",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(("F",0),),value_epochs=((vid,0),)))
    for cid in EFFECTS:
        ms.register_capability(CapabilityContract(cid,"opaque-action",{}, {},(),(),Authority.EFFECT,("MS1578-P1",),"CURRENT",{},query_obligation_id="ACT",qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_: calls.append(_cid) or {"action":_cid,"physical_execution_marker":_cid},operational_scope_id="R2"))
    rng=random.Random(1535)
    noise=(.32,.28,.30)
    for cid,vec in EFFECTS.items():
        for vi,vid in enumerate(VALUES):
            for sample in range(61):
                observed=vec[vi]+rng.gauss(0,noise[vi])
                ms.record_operational_trace(OperationalTrace(f"{cid}-{vid}-{sample}",(cid,),((observed,),),frame_id="F",episode_schema_id=f"E-{vid}"))
    return ms,calls

def prepare(ms,suffix):
    ms.observe_value_state("ENERGY",3.2); ms.observe_value_state("THERMAL",7.6); ms.observe_value_state("INTEGRITY",6.0)
    ms.observe_opaque_control_state(Observation(f"CTRL-{suffix}","EXT","control","R2-STATE",authority=Authority.OBSERVATION_ONLY),evidence_id=f"E-CTRL-{suffix}")
    n=ms.nominate_multi_value_action_intent(VALUES,obligation()); assert n['status']=='ACTION_INTENT_NOMINATED',n
    e=ms.execute_bounded_action(n['intent']['intent_id'],obligation()); assert e['status']=='ACTION_EXECUTED',e
    return e['execution']['execution_id'],e

def main():
    with tempfile.TemporaryDirectory(prefix='ms1578-p1-') as td:
        ms,calls=seeded(Path(td))
        true_post={"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34} # illustrative actual REST-like consequence
        false_post={"ENERGY":4.60,"THERMAL":8.30,"INTEGRITY":5.10} # coherently misbound external stream
        accepted=[]
        for i in range(8):
            exid,ex=prepare(ms,f"M{i}")
            # Interface label/referent is syntactically correct; physical values are deliberately wrong.
            obs=Observation(f"OUT-M{i}",f"MISBOUND-SOURCE-{i%2}",f"action-execution:{exid}",{"next_state_id":"FALSE-NEXT","observed_values":false_post},authority=Authority.OBSERVATION_ONLY,lineage=("INTERFACE_LABELLED_ACTUAL",))
            r=ms.record_bounded_action_outcome(exid,obs,evidence_id=f"E-OUT-M{i}")
            accepted.append(r['status'])
        cands=ms.nominate_action_outcome_predictive_candidates(min_support=8,min_consistency=.78)
        rest=[c for c in cands if c.capability_id=='REST']
        learned={c.value_epoch[0]:c.value_effect for c in rest}
        expected_false={k:round(false_post[k]-v,3) for k,v in {"ENERGY":3.2,"THERMAL":7.6,"INTEGRITY":6.0}.items()}
        # Try arbitrary source/origin and empty lineage on a fresh entity; admission should be unchanged.
        ms2,calls2=seeded(Path(td)/'b')
        exid,_=prepare(ms2,'ORIGIN')
        arbitrary=ms2.record_bounded_action_outcome(exid,Observation('OUT-ORIGIN','TOTALLY-UNQUALIFIED-ORIGIN',f'action-execution:{exid}',{"next_state_id":"FALSE-NEXT","observed_values":false_post},authority=Authority.OBSERVATION_ONLY,lineage=()),evidence_id='E-OUT-ORIGIN')
        out={
          'pass':'MS1578_PASS01',
          'discriminator':'Can current Microseed distinguish syntactically valid outcome observations from coherently misbound actual-outcome streams?',
          'accepted_misbound_outcomes':accepted,
          'handler_calls':calls,
          'learned_rest_effects':learned,
          'misbound_effect_labels':expected_false,
          'illustrative_true_post_values_not_visible_to_organism':true_post,
          'arbitrary_origin_empty_lineage_status':arbitrary['status'],
          'observation_admission_checks_only': ['Authority.OBSERVATION_ONLY','referent == action-execution:<execution_id>','payload shape/value premises'],
          'result':'FALSE_GREEN_CONFIRMED__OUTCOME_STREAM_MAPPING_NOT_QUALIFIED',
          'authority':'RESEARCH_ONLY',
        }
        print(json.dumps(out,indent=2,sort_keys=True))
        Path('research/MS1578_PASS01_ACTUAL_STREAM_MISBINDING.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
if __name__=='__main__': main()
