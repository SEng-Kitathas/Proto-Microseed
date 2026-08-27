from __future__ import annotations
import json
from pathlib import Path
import tempfile
from microseed import (
    Authority, CapabilityContract, Microseed,
    OpaqueTransitionSample, QualificationState, QueryObligation,
    discover_opaque_action_composition_candidates,
)
from microseed.cognition.hypothesis import Hypothesis, HypothesisSet

SCOPE='AFF-SCOPE'; OBL=QueryObligation('AFF-Q','bounded discriminating probe',required_authority=Authority.EFFECT,operational_scope_id=SCOPE)

def cap(cid, calls):
    return CapabilityContract(cid,'opaque-primitive',{}, {},(),(),Authority.EFFECT,('MS1678-RESEARCH',),'CURRENT',{},query_obligation_id='AFF-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid, **_: calls.append(_cid) or {'receipt':_cid},operational_scope_id=SCOPE)

def row(tag,s,a,e,origin=None):
    return OpaqueTransitionSample(tag,origin or f'phys-{tag}',s,a,e,'OPAQUE-FRAME',0)

def route_current(ms, steps):
    reasons=[]
    for cid in steps:
        c=ms.capabilities.contracts.get(cid)
        if c is None: reasons.append((cid,'NO_PATH')); continue
        if c.qualification not in {QualificationState.QUALIFIED,QualificationState.SHADOW_QUALIFIED} or c.currentness!='CURRENT': reasons.append((cid,'NOT_CURRENT')); continue
        if c.authority!=Authority.EFFECT: reasons.append((cid,'NO_EFFECT_AUTHORITY')); continue
        if c.query_obligation_id and c.query_obligation_id!=OBL.obligation_id: reasons.append((cid,'QUERY_MISMATCH')); continue
        if c.operational_scope_id and c.operational_scope_id!=OBL.operational_scope_id: reasons.append((cid,'SCOPE_MISMATCH')); continue
        if c.handler is None: reasons.append((cid,'NO_HANDLER'))
    return len(reasons)==0,reasons

def entropy_probe(hs, routes):
    return hs.best_probe(routes)

def run():
    td=tempfile.TemporaryDirectory(prefix='ms1678-p1-'); calls=[]
    try:
        ms=Microseed(Path(td.name))
        for cid in ('A','B','C'): ms.register_capability(cap(cid,calls))
        # Opaque history supports C ≈ A∘B on two physically distinct origins/starts.
        rows=[
            row('0a','s0','A','m0','o0a'),row('0b','m0','B','e0','o0b'),row('0c','s0','C','e0','o0c'),
            row('1a','s1','A','m1','o1a'),row('1b','m1','B','e1','o1b'),row('1c','s1','C','e1','o1c'),
        ]
        comps=discover_opaque_action_composition_candidates(rows,min_positive_support=2)
        target=[c for c in comps if (c.direct_action_token,c.first_action_token,c.second_action_token)==('C','A','B')]
        assert target
        # Current single actions are observationally identical under both live alternatives.
        h1=Hypothesis('INCUMBENT',lambda x: {'A':'u','B':'v','C':'w',('A','B'):'macro-left'}[x])
        h2=Hypothesis('SEQUENCE_ALT',lambda x: {'A':'u','B':'v','C':'w',('A','B'):'macro-right'}[x])
        hs=HypothesisSet([h1,h2])
        singles=['A','B','C']
        single_probe=entropy_probe(hs,singles)
        assert single_probe is None
        # Candidate macro comes from the earned opaque relation, not an invented action token.
        macro=(target[0].first_action_token,target[0].second_action_token)
        macro_probe=entropy_probe(hs,[macro])
        ok,reasons=route_current(ms,macro)
        assert macro_probe==('A','B') and ok and not reasons
        # Search never invokes handlers.
        assert calls==[]
        # A symbolic token is not an actuator.
        symbolic_ok,symbolic_reasons=route_current(ms,('A_then_B',))
        assert not symbolic_ok and symbolic_reasons==[('A_then_B','NO_PATH')]
        out={
            'milestone':'MS1678','pass':1,
            'single_capability_probe':single_probe,
            'opaque_composition_candidate':target[0].serializable(),
            'composed_probe':list(macro_probe),
            'composed_route_current':ok,
            'search_side_effect_calls':calls,
            'symbolic_action_route':{'current':symbolic_ok,'reasons':symbolic_reasons},
            'disposition':'ONE_STEP_DISCRIMINATOR_ABSENT__COMPOSED_EXISTING_AFFORDANCE_NOMINATED__EXECUTION_NOT_YET_EARNED',
            'next_discriminator':'CAN_ORDINARY_CONTROL_REALIZE_SELECTED_MACRO_ONE_PRIMITIVE_PER_TICK_WITH_ACTUAL_OUTCOMES_AND_ONE_EPISTEMIC_TRIAL_IDENTITY',
        }
        Path(__file__).with_name('MS1678_PASS01_AFFORDANCE_SEARCH.json').write_text(json.dumps(out,indent=2,sort_keys=True))
        print(json.dumps(out,indent=2,sort_keys=True))
    finally: td.cleanup()
if __name__=='__main__': run()
