from __future__ import annotations

import json
import hashlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from research.substrate_shadow.environment_adapter import ShadowEnvironmentAdapter, AdapterConfig
from scratch.ms1949_shadow_substrate_adapter import ChargeWorld
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def run_restart():
    td=tempfile.TemporaryDirectory(prefix='ms1950-restart-'); root=Path(td.name)
    world1=ChargeWorld(); a1=ShadowEnvironmentAdapter(world1,AdapterConfig(adapter_instance_id="BOOT-1")); m1=Microseed(root)
    try:
        a1.attach(m1)
        relation_id,_=a1.train_actual_history(m1,'CHARGE')
        p=a1.zero_row_rehearsal(m1,'CHARGE'); assert p is not None
        proposal_id=p.proposal_id
        c1=m1.derive_bounded_action_commitment(proposal_id); assert c1.commitment.value=='YES'
        relation_digest=hashlib.sha256(json.dumps(m1.action_outcome_learning.relations[relation_id].serializable(),sort_keys=True,separators=(',',':')).encode()).hexdigest()
        before={'relation_id':relation_id,'relation_digest':relation_digest,'proposal_id':proposal_id,'proposal_status':m1.counterfactual_rehearsal_status(proposal_id),'relation_status':m1.action_outcome_predictive_relation_status(relation_id)}
    finally:
        _close(m1)

    # Restart from persisted organism state. Historical models/proposals may replay,
    # but operational contracts/handlers must not silently become current authority.
    m2=Microseed(root)
    try:
        assert relation_id in m2.action_outcome_learning.relations
        assert hashlib.sha256(json.dumps(m2.action_outcome_learning.relations[relation_id].serializable(),sort_keys=True,separators=(',',':')).encode()).hexdigest()==relation_digest
        assert proposal_id in m2.counterfactual_rehearsals.proposals
        pre_attach_rel=m2.action_outcome_predictive_relation_status(relation_id)
        pre_attach_prop=m2.counterfactual_rehearsal_status(proposal_id)
        # No live effect handler/contract should be assumed merely from historical competence.
        assert 'CHARGE' not in m2.capabilities.contracts

        world2=ChargeWorld(); a2=ShadowEnvironmentAdapter(world2,AdapterConfig(adapter_instance_id="BOOT-2"))
        a2.attach(m2)
        post_attach_rel=m2.action_outcome_predictive_relation_status(relation_id)
        post_attach_prop=m2.counterfactual_rehearsal_status(proposal_id)
        assert post_attach_rel['status']=='CURRENT_PREDICTIVE_RELATION',post_attach_rel
        assert post_attach_prop['status']=='CURRENT_REHEARSAL_PROPOSAL',post_attach_prop

        # Reuse historical proposal only after live adapter authority has been restored.
        a2.reset_control(m2,'REENTRY')
        c2=m2.derive_bounded_action_commitment(proposal_id); assert c2.commitment.value=='YES'
        intent=m2.nominate_bounded_action_intent(proposal_id,a2.act_obligation()); assert intent['status']=='ACTION_INTENT_NOMINATED'
        ex=m2.execute_bounded_action(intent['intent']['intent_id'],a2.act_obligation()); assert ex['status']=='ACTION_EXECUTED'
        c=a2.config
        out=m2.record_bounded_action_outcome_via_observation_basis(ex['execution']['execution_id'],observation_capability_id=c.observation_capability_id,observation_obligation=a2.obs_obligation(),basis_capability_id=c.observation_basis_id,basis_obligation=a2.basis_obligation(),evidence_id='E-MS1950-REENTRY',capture_id='CAP-MS1950-REENTRY')
        assert out['status']=='ACTION_OUTCOME_OBSERVED'
        assert out['outcome']['actual_next_state_id']=='LEVEL-2'
        assert hashlib.sha256(json.dumps(m2.action_outcome_learning.relations[relation_id].serializable(),sort_keys=True,separators=(',',':')).encode()).hexdigest()==relation_digest

        result={
            'status':'PASS',
            'before_restart':before,
            'after_restart_before_adapter':{'relation_status':pre_attach_rel,'proposal_status':pre_attach_prop,'live_charge_contract':False},
            'after_adapter_reattach':{'relation_status':post_attach_rel,'proposal_status':post_attach_prop,'live_charge_contract':True},
            'reentry_execution_outcome':out['outcome']['actual_next_state_id'],
            'earned':'PERSISTED_DEVELOPMENTAL_COMPETENCE_CAN_RECONNECT_TO_REALITY_AFTER_RESTART_ONLY_AFTER_EXPLICIT_CURRENT_ENVIRONMENT_REATTACHMENT',
            'historical_competence_authority':'NONE',
            'automatic_reauthorization':'NO',
        }
        return result
    finally:
        _close(m2); td.cleanup()

def main(): print(json.dumps(run_restart(),indent=2,sort_keys=True))

if __name__=='__main__': main()
