from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from scratch.ms1960_affordance_relative_proto_referent import collect, group_affordances, evaluator_alignment


def rename_schedule(schedule, rename):
    return tuple(rename.get(x,x) for x in schedule)


def canonical_unlabeled_incidence(rows):
    # Strip opaque action labels and retain only the multiset of response patterns.
    # This intentionally asks what survives if actuator handles are renamed.
    patterns=[]
    for row in rows:
        pats=tuple(bool(x) for x in row['response_rows'][0][1]) if False else None
        patterns.append(tuple(sorted(tuple(pattern) for _,pattern in row['response_rows'])))
    return tuple(sorted(patterns))


def run_joint_symmetry():
    # Session A: FX-A affects latent 0, FX-B affects latent 1.
    s=('FX-A','FX-B','FX-G','FX-A','FX-B')
    a=collect((0,0,1,1),s)
    aa=group_affordances(a)

    # Session B permutes sensors AND swaps the opaque names attached to the two
    # selective external effects. The evaluator still knows the physical mapping,
    # but that mapping is not supplied to the referent mechanism.
    # We realize the name swap by translating the schedule before applying the
    # underlying external actions: displayed FX-A now drives physical source 1,
    # displayed FX-B drives source 0.
    displayed=('FX-A','FX-B','FX-G','FX-A','FX-B')
    physical=rename_schedule(displayed,{'FX-A':'FX-B','FX-B':'FX-A'})
    b=collect((1,0,1,0),physical)
    bb_raw=group_affordances(b)
    # Relabel response rows back to the displayed actuator names to model what the
    # second session locally observes.
    bb=[]
    inverse={'FX-A':'FX-B','FX-B':'FX-A','FX-G':'FX-G'}
    import hashlib
    for row in bb_raw:
        relabeled=tuple(sorted((inverse[action],pattern) for action,pattern in row['response_rows']))
        sig=hashlib.sha256(json.dumps({'opaque_action_response':relabeled},sort_keys=True,separators=(',',':')).encode()).hexdigest()
        bb.append({'group':row['group'],'response_rows':relabeled,'signature':sig})
    bb=tuple(bb)

    # Labeled signatures are not stable once actuator handles are permuted.
    siga={x['signature'] for x in aa}; sigb={x['signature'] for x in bb}
    assert siga==sigb  # locally the same named relation graph is reconstructed

    # But evaluator alignment flips under the name swap: the exact same local
    # signature can denote the opposite latent source in the other session.
    la=evaluator_alignment(a,aa)
    mapping_b=b['mapping']; lb={}
    for row in bb:
        latent={mapping_b[i] for i in row['group']}; assert len(latent)==1
        lb[row['signature']]=next(iter(latent))
    assert la != lb
    assert set(la)==set(lb)
    assert all(la[k] != lb[k] for k in la)

    return {
        'status':'PASS',
        'session_a_alignment':la,
        'session_b_alignment_after_joint_alias_swap':lb,
        'shared_local_signatures':sorted(siga),
        'earned':'JOINT_SENSOR_AND_ACTUATOR_ALIAS_SYMMETRY_MAKES_CROSS_SESSION_NUMERICAL_REFERENT_IDENTITY_UNIDENTIFIABLE_FROM_LOCAL_AFFORDANCE_STRUCTURE_ALONE',
        'identity_authority':'NONE',
        'semantic_reference_authority':'NONE',
        'required_breaker':'ADDITIONAL_CONTINUITY_OR_ASYMMETRIC_EVIDENCE_REQUIRED',
    }


def main(): print(json.dumps(run_joint_symmetry(),indent=2,sort_keys=True))
if __name__=='__main__': main()
