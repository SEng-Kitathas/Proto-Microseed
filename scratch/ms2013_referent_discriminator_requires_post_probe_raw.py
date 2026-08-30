from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from microseed.development.epistemic_program import advance_epistemic_program_trial
from scratch.ms2010_runtime_owned_referent_decision_surface import oob,bob
from scratch.ms2012_referent_probe_authenticated_observation_closure import _epistemic_fixture
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import _close

def _advance(m,trial,n,x):
    eid=x['execution']['execution_id'];intent=m.action_closure.intents[n['intent']['intent_id']];execution=m.action_closure.executions[eid];outcome=next(o for o in m.action_closure.outcomes.values() if o.execution_id==eid)
    advanced=advance_epistemic_program_trial(trial,intent=intent,execution=execution,outcome=outcome,capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs));assert advanced.status=='COMPLETE',advanced
    return advanced

def authenticated_no_post_raw():
    td,m,calls,world,bid,ba,bb,trial,dc,n,x=_epistemic_fixture()
    try:
        eid=x['execution']['execution_id']
        out=m.record_bounded_action_outcome_via_observation_basis(eid,observation_capability_id='OBS',observation_obligation=oob(),basis_capability_id='BASIS',basis_obligation=bob(),evidence_id='MS2013-E-P2-AUTH',capture_id='MS2013-C-P2-AUTH')
        assert out['status']=='ACTION_OUTCOME_OBSERVED',out
        admitted=m.derive_admitted_opaque_transition_sample(eid);assert admitted['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE',admitted
        prefix=m.derive_current_owned_opaque_probe_prefix(max_steps=3)
        advanced=_advance(m,trial,n,x)
        complete=m.record_completed_epistemic_program_evidence(advanced,evidence_id='MS2013-E-COMPLETE-NO-RAW')
        return {'status':'OBSERVED','admitted':admitted['status'],'prefix_without_post_raw':prefix,'program_evidence':complete,'deficit_state':m.epistemic_deficits.records['MS2012-D'].state.value,'accepted_without_post_raw':complete.get('status')=='PROGRAM_EVIDENCE_RECORDED'}
    finally:_close(m);td.cleanup()

def main():print(json.dumps(authenticated_no_post_raw(),indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
