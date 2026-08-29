from __future__ import annotations

import json
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import ConstructorGrowthConfig, EpistemicStatus, ExternalConstructorQualifier
from scratch.ms1974_deeper_history_constructor_boundary import (
    DeepAliasWorld, build, prepare_proposals, run_chain, external_sample,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def external_heldout(candidate):
    rows=[]
    for context in ('s0','r'):
        for i in range(8):
            before,after=external_sample(context,'B')
            raw=(('s2',),('s1',),(context,))
            bucket=candidate.project(raw)
            rows.append({'context':context,'raw_history':raw,'bucket':bucket,'actual_end':after['next_state_id']})
    predictions={(bucket,action):effect for bucket,action,effect in candidate.bucket_action_prediction}
    assert all(row['bucket'] is not None and predictions[(row['bucket'],'B')]==row['actual_end'] for row in rows)
    return rows


def run_ms1975():
    td=tempfile.TemporaryDirectory(prefix='ms1975-owned-constructor-');root=Path(td.name);world=DeepAliasWorld();m=build(root,world)
    try:
        proposals=prepare_proposals(m)
        for i in range(36):
            context='s0' if i%2==0 else 'r'
            run_chain(m,world,proposals,context,i)

        owned=m.derive_admitted_constructor_projection_samples(max_lag=2)
        assert owned['status']=='ADMITTED_OWNED_CONSTRUCTOR_SAMPLES',owned
        assert owned['history_basis']=='AUTHENTICATED_CONTROL_STATE_PREDECESSOR_CHAIN'
        b_rows=[row for row in owned['samples'] if row.action_token=='B' and len(row.raw_history)==3]
        assert len(b_rows)==36,len(b_rows)
        # The bridge must derive the deep visible history itself. Evaluator inspection
        # checks the expected shape but never supplies these tokens to the bridge.
        shapes={row.raw_history for row in b_rows}
        assert shapes=={(('s2',),('s1',),('s0',)),(('s2',),('s1',),('r',))},shapes

        shuffled=list(b_rows);random.Random(1975).shuffle(shuffled)
        train=tuple(shuffled[:18]);pressure=tuple(shuffled[18:27]);validation=tuple(shuffled[27:])
        for split in (train,pressure,validation):
            assert {x.effect_token for x in split}=={'sx','sy'}
        cfg=ConstructorGrowthConfig(
            max_support_ceiling=3,max_lag_ceiling=2,min_train_support=12,
            min_validation_accuracy=0.95,min_lift_over_action_baseline=0.40,
            min_scope_accuracy=0.95,max_candidates=4,
        )
        found=m.discover_epistemic_constructor_candidates(train,pressure,validation,cfg)
        assert found,found
        candidates=[m.epistemic_constructor_candidates[x['candidate_id']] for x in found]
        candidates=[c for c in candidates if c.lag_depth_used==2 and any(a.lag==2 for a in c.atoms)]
        assert candidates,candidates
        c=candidates[0]
        assert [a.token() for a in c.atoms]==['L2:P0'],c.atoms
        assert c.validation_accuracy==1.0 and c.lift>=0.40

        heldout=external_heldout(c)
        qe=m.append_evidence(
            'Q-MS1975-EXTERNAL-HOLDOUT',
            {'kind':'OWNED_HISTORY_CONSTRUCTOR_HOLDOUT','candidate_sha256':c.digest(),'rows':heldout},
            EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-PROCESS-MS1975-QUALIFIER',
        )
        ticket=ExternalConstructorQualifier(m.evidence,qualifier_id='EXTERNAL-PROCESS-MS1975-CONSTRUCTOR').qualify(c,qualification_evidence=(qe,))
        rec=m.admit_epistemic_constructor_candidate(ticket,projection_id='P-MS1975')
        assert rec.current and rec.projection_origin=='ENDOGENOUS_CONSTRUCTOR_GROWTH_EXTERNALLY_QUALIFIED'

        return {
            'status':'PASS',
            'owned_sample_count':owned['sample_count'],
            'owned_target_sample_count':len(b_rows),
            'history_basis':owned['history_basis'],
            'target_raw_history_shapes':sorted([[list(x) for x in shape] for shape in shapes]),
            'candidate_id':c.candidate_id,'candidate_sha256':c.digest(),
            'atoms':[a.token() for a in c.atoms],'lag_depth_used':c.lag_depth_used,
            'validation_accuracy':c.validation_accuracy,'lift':c.lift,
            'external_holdout_count':len(heldout),
            'projection':rec.serializable(),
            'earned':'AUTHENTICATED_OWNED_ACTION_HISTORY_CAN_EPHEMERALLY_SUPPLY_THE_EXISTING_BOUNDED_LAG2_CONSTRUCTOR_AND_EARN_EXTERNALLY_QUALIFIED_DEEPER_OPERATIONAL_REPRESENTATION',
            'new_constructor_mechanism_added':'NO',
            'sample_persistence':'NONE','qualification_authority':'EXTERNAL_ONLY',
            'semantic_projection_authority':'NONE','truth_authority':'NONE','language_authority':'NONE',
        }
    finally:
        _close(m);world.close();td.cleanup()


def main(): print(json.dumps(run_ms1975(),indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
