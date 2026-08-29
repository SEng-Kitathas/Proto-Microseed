from __future__ import annotations

import json, random, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import ConstructorGrowthConfig, EpistemicStatus, ExternalConstructorQualifier
from scratch.ms1981_temporal_raw_constructor_boundary import (
    BITS, World, build, chain, external_holdout, proposals,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def run_ms1982():
    td=tempfile.TemporaryDirectory(prefix='ms1982-owned-temporal-raw-'); w=World(); m=build(Path(td.name),w)
    try:
        ps=proposals(m)
        for i in range(48): chain(m,w,ps,BITS[i%4],i)

        owned=m.derive_admitted_raw_constructor_projection_samples(max_lag=1)
        assert owned['status']=='ADMITTED_OWNED_RAW_CONSTRUCTOR_SAMPLES',owned
        assert not owned['receipt_rejections'],owned['receipt_rejections']
        target=[row for row in owned['samples'] if row.action_token=='B' and len(row.raw_history)==2]
        assert len(target)==48,len(target)
        shapes={row.raw_history for row in target}
        assert shapes=={(('0',),('0',)),(('1',),('0',)),(('0',),('1',)),(('1',),('1',))},shapes

        rows=list(target); random.Random(1982).shuffle(rows)
        train=tuple(rows[:28]); pressure=tuple(rows[28:38]); validation=tuple(rows[38:])
        for split in (train,pressure,validation): assert {x.effect_token for x in split}=={'SAME','DIFF'}

        cfg0=ConstructorGrowthConfig(max_support_ceiling=2,max_lag_ceiling=0,min_train_support=20,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=8)
        assert m.discover_epistemic_constructor_candidates(train,pressure,validation,cfg0)==[]

        cfg1=ConstructorGrowthConfig(max_support_ceiling=2,max_lag_ceiling=1,min_train_support=20,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=8)
        found=m.discover_epistemic_constructor_candidates(train,pressure,validation,cfg1);assert found,found
        cs=[m.epistemic_constructor_candidates[x['candidate_id']] for x in found]
        exact=[c for c in cs if set(a.token() for a in c.atoms)=={'L0:P0','L1:P0'}]
        assert len(exact)==1,[(tuple(a.token() for a in c.atoms),c.validation_accuracy,c.lift) for c in cs]
        c=exact[0];assert c.validation_accuracy==1.0

        holdout=external_holdout(c)
        qe=m.append_evidence('Q-MS1982',{'kind':'OWNED_TEMPORAL_RAW_HOLDOUT','candidate_sha256':c.digest(),'rows':holdout},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1982')
        ticket=ExternalConstructorQualifier(m.evidence,qualifier_id='EXTERNAL-MS1982').qualify(c,qualification_evidence=(qe,))
        rec=m.admit_epistemic_constructor_candidate(ticket,projection_id='P-MS1982');assert rec.current

        return {
            'status':'PASS','owned_sample_count':owned['sample_count'],'target_sample_count':len(target),
            'history_basis':owned['history_basis'],'raw_history_shapes':sorted([[list(x) for x in shape] for shape in shapes]),
            'current_only_candidates':0,'atoms':[a.token() for a in c.atoms],
            'validation_accuracy':c.validation_accuracy,'lift':c.lift,'external_holdout_count':len(holdout),
            'earned':'AUTHENTICATED_OWNED_RAW_OBSERVATION_RECEIPTS_CAN_BE_CHAINED_THROUGH_ACTION_ANCESTRY_TO_FEED_EXISTING_TEMPORAL_CONSTRUCTOR_GROWTH',
            'new_constructor_mechanism_added':'NO','sample_persistence':'NONE','qualification_authority':'EXTERNAL_ONLY',
            'semantic_coordinate_authority':'NONE','semantic_projection_authority':'NONE','truth_authority':'NONE','language_authority':'NONE',
        }
    finally:_close(m);w.close();td.cleanup()


def main():print(json.dumps(run_ms1982(),indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
