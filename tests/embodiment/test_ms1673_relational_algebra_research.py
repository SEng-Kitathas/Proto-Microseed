import random
from microseed import OpaqueTransitionSample, discover_opaque_action_composition_candidates, predict_opaque_action_composition

def row(tag,s,a,e,origin=None,epoch=0):
    return OpaqueTransitionSample(tag, origin or f'o-{tag}', s,a,e,'F',epoch)

def clean():
    ss=['s0','s1','s2','s3','s4'];out=[]
    for i,s in enumerate(ss):
        out += [row(f'a{i}',s,'a',ss[(i+1)%5]), row(f'b{i}',s,'b',ss[(i+2)%5])]
    for i,s in enumerate(ss[:3]): out.append(row(f'c{i}',s,'c',ss[(i+3)%5]))
    return out

def target(cs): return [c for c in cs if (c.direct_action_token,c.first_action_token,c.second_action_token)==('c','a','b')]

def test_discovers_opaque_composition_and_predicts_heldout():
    rs=clean(); cs=discover_opaque_action_composition_candidates(rs,min_positive_support=2); assert target(cs)
    p=predict_opaque_action_composition('s3','c',target(cs),rs); assert p['status']=='RELATIONAL_PREDICTION' and p['prediction']=='s1'

def test_observed_counterexample_blocks_global_candidate():
    rs=clean()+[row('cx','s3','c','s2')]; assert target(discover_opaque_action_composition_candidates(rs,min_positive_support=2))==[]

def test_same_origin_replay_does_not_manufacture_support():
    rs=[r for r in clean() if (r.start_token,r.action_token) in {('s0','a'),('s1','b'),('s0','c')}]
    rs += [row(f'replay{i}-{r.sample_id}',r.start_token,r.action_token,r.end_token,origin=r.origin_id) for r in list(rs) for i in range(6)]
    assert target(discover_opaque_action_composition_candidates(rs,min_positive_support=2))==[]

def test_conflicting_endpoint_key_is_not_last_write_wins():
    rs=clean()+[row('conflict','s0','a','s4')]
    cs=discover_opaque_action_composition_candidates(rs,min_positive_support=2)
    p=predict_opaque_action_composition('s0','c',target(cs),rs)
    assert p['status']=='UNKNOWN_INCOMPLETE'

def test_relational_disagreement_returns_unknown():
    rs=clean();
    for i,s in enumerate(['s0','s1','s2','s3','s4']): rs.append(row(f'd{i}',s,'d',f'm{i}'))
    for i,e in enumerate(['s3','s4','s0','s2','s1']): rs.append(row(f'e{i}',f'm{i}','e',e))
    cs=[c for c in discover_opaque_action_composition_candidates(rs,min_positive_support=2) if c.direct_action_token=='c' and (c.first_action_token,c.second_action_token) in {('a','b'),('d','e')}]
    p=predict_opaque_action_composition('s3','c',cs,rs); assert p['status']=='UNKNOWN_INCOMPLETE' and p['reason']=='RELATIONAL_DISAGREEMENT'

def test_injective_gauge_renaming_preserves_relation():
    rs=clean(); sm={x:f'X{i}' for i,x in enumerate(['s0','s1','s2','s3','s4'])}; am={'a':'q','b':'r','c':'t'}
    rr=[row('g'+x.sample_id,sm[x.start_token],am[x.action_token],sm[x.end_token],origin='g'+x.origin_id) for x in rs]
    cs=discover_opaque_action_composition_candidates(rr,min_positive_support=2)
    z=[c for c in cs if (c.direct_action_token,c.first_action_token,c.second_action_token)==('t','q','r')]; assert z
    assert predict_opaque_action_composition(sm['s3'],'t',z,rr)['prediction']==sm['s1']

def test_mixed_frame_epochs_do_not_nominate_one_relation():
    rs=clean(); rs[-1]=row(rs[-1].sample_id,rs[-1].start_token,rs[-1].action_token,rs[-1].end_token,origin=rs[-1].origin_id,epoch=1)
    assert discover_opaque_action_composition_candidates(rs,min_positive_support=2)==()

def test_candidate_carries_zero_truth_qualification_execution_independence_authority():
    c=target(discover_opaque_action_composition_candidates(clean(),min_positive_support=2))[0]
    assert c.proposal_authority==c.qualification_authority==c.semantic_action_authority==c.truth_authority==c.execution_authority==c.evidence_independence_authority=='NONE'

def test_missing_component_path_returns_unknown_not_synthesis():
    rs=[r for r in clean() if not (r.start_token=='s4' and r.action_token=='b')]
    cs=target(discover_opaque_action_composition_candidates(rs,min_positive_support=2)); assert cs
    p=predict_opaque_action_composition('s3','c',cs,rs); assert p['status']=='UNKNOWN_INCOMPLETE' and p['prediction'] is None

def test_relational_prediction_never_carries_truth_or_execution_authority():
    rs=clean(); cs=target(discover_opaque_action_composition_candidates(rs,min_positive_support=2))
    p=predict_opaque_action_composition('s3','c',cs,rs)
    assert p['status']=='RELATIONAL_PREDICTION'
    assert p['truth_authority']==p['execution_authority']=='NONE'

def test_distinct_event_keys_with_one_shared_physical_origin_do_not_form_two_supports():
    # Two endpoint-equivalence witnesses, but every event declares the same physical origin.
    rs=[
        row('x0','s0','a','m0',origin='ROOT'), row('x1','m0','b','e0',origin='ROOT'), row('x2','s0','c','e0',origin='ROOT'),
        row('y0','s1','a','m1',origin='ROOT'), row('y1','m1','b','e1',origin='ROOT'), row('y2','s1','c','e1',origin='ROOT'),
    ]
    assert target(discover_opaque_action_composition_candidates(rs,min_positive_support=2))==[]


def test_prediction_refuses_a_later_conflicting_component_key_even_if_candidate_was_formed_cleanly():
    clean_rows=clean(); cs=target(discover_opaque_action_composition_candidates(clean_rows,min_positive_support=2)); assert cs
    conflicted=list(clean_rows)+[row('late-conflict','s3','a','s0')]
    p=predict_opaque_action_composition('s3','c',cs,conflicted)
    assert p['status']=='UNKNOWN_INCOMPLETE' and p['prediction'] is None
