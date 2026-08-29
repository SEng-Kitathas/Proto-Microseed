from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from scratch.ms1958_proto_referent_boundary_coherence import collect


def group_signatures(result):
    boundaries=result['boundaries']
    out=[]
    for group in result['nomination']['groups']:
        sigs={tuple(boundaries[i]) for i in group}
        assert len(sigs)==1, (group,sigs)
        boundary=next(iter(sigs))
        digest=hashlib.sha256(json.dumps({'boundary_signature':boundary},sort_keys=True,separators=(',',':')).encode()).hexdigest()
        out.append({'group':tuple(group),'boundary_signature':boundary,'operational_signature_sha256':digest})
    return tuple(out)


def run_cross_session_signature():
    schedule=(0,0,1,'G',1,0,1)
    a=collect((0,0,1,1),schedule)
    b=collect((1,0,1,0),schedule)
    sa=group_signatures(a); sb=group_signatures(b)

    # Concrete channel membership changes across sensor permutation.
    assert tuple(x['group'] for x in sa) != tuple(x['group'] for x in sb)
    # But group content signatures survive because they are computed from the same
    # protocol-relative response boundaries rather than channel indices.
    set_a={x['operational_signature_sha256'] for x in sa}
    set_b={x['operational_signature_sha256'] for x in sb}
    assert set_a==set_b and len(set_a)==2,(sa,sb)

    # Evaluator-only check: each shared signature corresponds to the same latent
    # source across sessions. Latent mapping is never used to compute the signature.
    def latent_by_sig(result,sigs):
        mapping=result['mapping']; d={}
        for row in sigs:
            latent={mapping[i] for i in row['group']}; assert len(latent)==1
            d[row['operational_signature_sha256']]=next(iter(latent))
        return d
    la=latent_by_sig(a,sa); lb=latent_by_sig(b,sb)
    assert la==lb

    return {
        'status':'PASS',
        'session_a':{'groups':sa},
        'session_b':{'groups':sb},
        'shared_operational_signatures':sorted(set_a),
        'evaluator_latent_alignment':la,
        'earned':'NOMINATED_BOUNDARY_GROUP_CONTENT_CAN_REASSOCIATE_OPERATIONAL_REFERENT_PARTITIONS_ACROSS_SENSOR_PERMUTATION_WITHOUT_CHANNEL_IDENTITY',
        'authority':'NONE',
        'identity_authority':'NONE',
        'semantic_reference_authority':'NONE',
        'remaining_boundary':'PROTOCOL_RELATIVE_OPERATIONAL_SIGNATURE != GENERAL_REFERENT_IDENTITY',
    }


def main(): print(json.dumps(run_cross_session_signature(),indent=2,sort_keys=True))
if __name__=='__main__': main()
