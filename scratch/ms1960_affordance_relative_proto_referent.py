from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed.cognition.referents import nominate_by_boundary_coherence, derive_affordance_relative_referent_signature
from scratch.ms1958_proto_referent_boundary_coherence import ReferentProcessWorld, boundaries

# Opaque experimental effect handles. Their semantics are not supplied to the
# referent derivation. The harness alone maps them to external operations.
ACTIONS=('FX-A','FX-B','FX-G')


def apply_opaque(world,action):
    if action=='FX-A': world.transform(0)
    elif action=='FX-B': world.transform(1)
    elif action=='FX-G': world.global_transform()
    else: raise ValueError(action)


def collect(mapping,schedule):
    w=ReferentProcessWorld(mapping)
    try:
        samples=[w.observe()]
        for action in schedule:
            apply_opaque(w,action); samples.append(w.observe())
        traces=tuple(tuple(sample[i] for sample in samples) for i in range(4))
        b=boundaries(traces)
        n=nominate_by_boundary_coherence(b)
        return {'mapping':mapping,'schedule':schedule,'boundaries':b,'nomination':{'status':n.status,'groups':n.groups,'reason':n.reason,'identity_authority':n.identity_authority}}
    finally:w.close()


def temporal_group_signatures(result):
    out=[]
    for group in result['nomination']['groups']:
        sigs={tuple(result['boundaries'][i]) for i in group}; assert len(sigs)==1
        sig=next(iter(sigs)); out.append(hashlib.sha256(json.dumps(sig).encode()).hexdigest())
    return tuple(sorted(out))


def affordance_signature(result,group):
    derived=derive_affordance_relative_referent_signature(
        result['boundaries'],group,result['schedule']
    )
    assert derived.status=='OPERATIONAL_REFERENT_SIGNATURE_DERIVED',derived
    assert derived.signature_sha256 is not None
    assert derived.identity_authority=='NONE'
    assert derived.semantic_reference_authority=='NONE'
    return derived.signature_sha256,derived.action_response_rows

def group_affordances(result):
    return tuple({'group':tuple(g),'signature':affordance_signature(result,g)[0],'response_rows':affordance_signature(result,g)[1]} for g in result['nomination']['groups'])


def evaluator_alignment(result,rows):
    mapping=result['mapping']; out={}
    for row in rows:
        latent={mapping[i] for i in row['group']}; assert len(latent)==1
        out[row['signature']]=next(iter(latent))
    return out


def run_affordance_relative():
    s1=('FX-A','FX-A','FX-B','FX-G','FX-B','FX-A','FX-B')
    s2=('FX-B','FX-G','FX-A','FX-B','FX-A','FX-B','FX-A')
    a=collect((0,0,1,1),s1)
    b=collect((1,0,1,0),s2)
    assert a['nomination']['status']==b['nomination']['status']=='REFERENT_PARTITION_NOMINATED'

    # Temporal boundary hashes depend on protocol ordering and should not survive.
    assert set(temporal_group_signatures(a))!=set(temporal_group_signatures(b))

    aa=group_affordances(a); bb=group_affordances(b)
    siga={x['signature'] for x in aa}; sigb={x['signature'] for x in bb}
    assert siga==sigb and len(siga)==2,(aa,bb)
    assert evaluator_alignment(a,aa)==evaluator_alignment(b,bb)

    # Global effect handle appears in both signatures; source-selective opaque handles
    # distinguish the two operational partitions without a semantic source label.
    return {
        'status':'PASS',
        'session_a':{'schedule':s1,'groups':aa,'temporal_signatures':temporal_group_signatures(a)},
        'session_b':{'schedule':s2,'groups':bb,'temporal_signatures':temporal_group_signatures(b)},
        'shared_affordance_signatures':sorted(siga),
        'evaluator_alignment':evaluator_alignment(a,aa),
        'earned':'OPAQUE_ACTION_RESPONSE_STRUCTURE_CAN_REASSOCIATE_PROTO_REFERENT_PARTITIONS_ACROSS_SENSOR_AND_PROTOCOL_ORDER_CHANGES',
        'identity_authority':'NONE',
        'semantic_reference_authority':'NONE',
        'remaining_boundary':'AFFORDANCE_RELATIVE_OPERATIONAL_REFERENT != NUMERICAL_OBJECT_IDENTITY',
    }


def main(): print(json.dumps(run_affordance_relative(),indent=2,sort_keys=True))
if __name__=='__main__': main()
