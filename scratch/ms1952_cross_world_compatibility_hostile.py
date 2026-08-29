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


class DriftedChargeWorld(ChargeWorld):
    """Same external action/interface identity; materially different dynamics."""
    name='CHARGE-WORLD'
    action_ids=('CHARGE',)
    compatibility_sha256=hashlib.sha256(b'CHARGE-WORLD:v2:CHARGE->LEVEL-1:value0.0').hexdigest()
    def apply(self, action_id):
        assert action_id=='CHARGE'
        self.level=min(1,self.level+1)
        return {'receipt':'charged-v2','level':self.level}
    def observe(self):
        return {
            'next_state_id':f'LEVEL-{self.level}',
            'observed_value':0.0 if self.level<2 else 2.4,
            'raw_level':self.level,
        }


def run_hostile():
    td=tempfile.TemporaryDirectory(prefix='ms1952-cross-world-'); root=Path(td.name)
    original=Microseed(root); a1=ShadowEnvironmentAdapter(ChargeWorld(),AdapterConfig(adapter_instance_id='ORIGINAL'))
    try:
        a1.attach(original)
        relation_id,_=a1.train_actual_history(original,'CHARGE')
        proposal=a1.zero_row_rehearsal(original,'CHARGE'); assert proposal
        proposal_id=proposal.proposal_id
        assert proposal.final_state_id=='LEVEL-2'
        assert original.action_outcome_predictive_relation_status(relation_id)['status']=='CURRENT_PREDICTIVE_RELATION'
    finally:
        _close(original)

    reopened=Microseed(root)
    try:
        assert reopened.action_outcome_predictive_relation_status(relation_id)['status']=='STALE_PREDICTIVE_RELATION'
        drifted=ShadowEnvironmentAdapter(DriftedChargeWorld(),AdapterConfig(adapter_instance_id='DRIFTED'))
        drifted.attach(reopened)

        # This is the hostile: same adapter-facing ids/epochs but different real dynamics.
        rel_after=reopened.action_outcome_predictive_relation_status(relation_id)
        prop_after=reopened.counterfactual_rehearsal_status(proposal_id)

        result={
            'status':'VIOLATED' if rel_after['status']=='CURRENT_PREDICTIVE_RELATION' and prop_after['status']=='CURRENT_REHEARSAL_PROPOSAL' else 'BLOCKED',
            'relation_after_incompatible_attach':rel_after,
            'proposal_after_incompatible_attach':prop_after,
            'old_predicted_final_state':'LEVEL-2',
            'new_world_actual_after_charge':'LEVEL-1',
            'boundary':'SAME_ADAPTER_INTERFACE_AND_EPOCH != SAME_ENVIRONMENT_DYNAMICS',
        }
        assert result['status']=='BLOCKED', result
        return result
    finally:
        _close(reopened); td.cleanup()

def main(): print(json.dumps(run_hostile(),indent=2,sort_keys=True))
if __name__=='__main__': main()
