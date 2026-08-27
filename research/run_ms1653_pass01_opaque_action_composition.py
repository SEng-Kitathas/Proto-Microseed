from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib, json, random
from pathlib import Path
from collections import defaultdict, Counter

OUT = Path(__file__).with_name('MS1653_PASS01_OPAQUE_ACTION_COMPOSITION.json')


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':'), default=str).encode()).hexdigest()

@dataclass(frozen=True)
class Transition:
    evidence_id: str
    start: str
    action: str
    end: str

@dataclass(frozen=True)
class CompositionWitness:
    evidence_id: str
    start: str
    first_action: str
    second_action: str
    middle: str
    composed_end: str
    direct_action: str
    direct_end: str

@dataclass(frozen=True)
class CompositionAlternative:
    candidate_id: str
    first_action: str
    second_action: str
    direct_action: str
    support: int
    source_evidence_ids: tuple[str, ...]
    proposal_authority: str = 'NONE'
    truth_authority: str = 'NONE'
    execution_authority: str = 'NONE'


def cyclic_world(prefix='S'):
    states = [f'{prefix}{i}' for i in range(4)]
    # No coordinate semantics are exposed to the constructor. This function is evaluator-only.
    def step(s, a):
        i = states.index(s)
        if a == 'A': return states[(i+1)%4]
        if a == 'B': return states[(i+3)%4]
        if a == 'C': return states[(i+2)%4]
        raise KeyError(a)
    return states, step


def make_training():
    states, step = cyclic_world()
    rows=[]; witnesses=[]
    # Full A/B transitions are observed; direct C only on S0,S1. No numeric meaning is supplied.
    for s in states:
        for a in ('A','B'):
            e=step(s,a)
            rows.append(Transition(digest(('T',s,a,e)), s,a,e))
    for s in states[:2]:
        e=step(s,'C')
        rows.append(Transition(digest(('T',s,'C',e)), s,'C',e))
        # Witness A then A vs direct C.
        m=step(s,'A'); ee=step(m,'A')
        witnesses.append(CompositionWitness(digest(('W',s,'A','A','C')), s,'A','A',m,ee,'C',e))
        # B then B does NOT equal C in this 4-cycle? Actually -1-1 == +2 mod4, so it also does.
        # We omit B,B from the selected candidate grammar in the identifiable fixture by requiring
        # direct witnessed path events supplied below. This is event availability, not semantic exclusion.
    return rows,witnesses


def construct_compositions(witnesses, min_unique_support=2):
    groups=defaultdict(list)
    for w in witnesses:
        if w.composed_end != w.direct_end:
            continue
        groups[(w.first_action,w.second_action,w.direct_action)].append(w)
    out=[]
    for key, ws in sorted(groups.items()):
        unique={w.evidence_id:w for w in ws}
        if len(unique) < min_unique_support:
            continue
        a,b,c=key
        payload={'a':a,'b':b,'c':c,'support':len(unique)}
        out.append(CompositionAlternative('COMP-'+digest(payload)[:20],a,b,c,len(unique),tuple(sorted(unique))))
    return out


def exact_lookup(rows):
    return {(r.start,r.action):r.end for r in rows}


def compose_predict(start, candidate, lookup):
    m=lookup.get((start,candidate.first_action))
    if m is None: return None
    return lookup.get((m,candidate.second_action))


def predict_unique(start,direct_action,candidates,lookup):
    preds={compose_predict(start,c,lookup) for c in candidates if c.direct_action==direct_action}
    preds.discard(None)
    if len(preds)==1:
        return next(iter(preds)), 'YES_UNIQUE_RELATIONAL_PREDICTION'
    if len(preds)>1:
        return None, 'UNKNOWN_COMPETING_RELATIONAL_PREDICTIONS'
    return None, 'UNKNOWN_NO_RELATIONAL_PREDICTION'


def gauge_rename(rows,witnesses,seed=1653):
    rng=random.Random(seed)
    state_tokens=sorted({r.start for r in rows}|{r.end for r in rows}|{w.middle for w in witnesses}|{w.composed_end for w in witnesses}|{w.direct_end for w in witnesses})
    action_tokens=sorted({r.action for r in rows}|{w.first_action for w in witnesses}|{w.second_action for w in witnesses}|{w.direct_action for w in witnesses})
    ss=[f'OPAQUE-E-{i}-{digest((seed,i))[:6]}' for i in range(len(state_tokens))]; rng.shuffle(ss)
    aa=[f'OPAQUE-A-{i}-{digest((seed,"a",i))[:6]}' for i in range(len(action_tokens))]; rng.shuffle(aa)
    sm=dict(zip(state_tokens,ss)); am=dict(zip(action_tokens,aa))
    rr=[Transition(digest(('R',r.evidence_id)),sm[r.start],am[r.action],sm[r.end]) for r in rows]
    ww=[CompositionWitness(digest(('RW',w.evidence_id)),sm[w.start],am[w.first_action],am[w.second_action],sm[w.middle],sm[w.composed_end],am[w.direct_action],sm[w.direct_end]) for w in witnesses]
    return rr,ww,sm,am


def nonidentifiable_fixture():
    # Two opaque path grammars fit C on the witnessed starts but disagree on unseen S2.
    # The constructor is given only actual witnessed endpoint equivalences.
    rows,wits=make_training()
    lookup=exact_lookup(rows)
    # Add opaque D/E transitions engineered evaluator-side. D∘E matches C on S0,S1 but not S2/S3.
    mappingD={'S0':'X0','S1':'X1','S2':'X2','S3':'X3'}
    mappingE={'X0':'S2','X1':'S3','X2':'S1','X3':'S0'}  # diverges from C on S2,S3
    for s,m in mappingD.items(): rows.append(Transition(digest(('D',s,m)),s,'D',m))
    for m,e in mappingE.items(): rows.append(Transition(digest(('E',m,e)),m,'E',e))
    for s in ('S0','S1'):
        wits.append(CompositionWitness(digest(('W2',s)),s,'D','E',mappingD[s],mappingE[mappingD[s]],'C',lookup[(s,'C')]))
    return rows,wits


def main():
    rows,witnesses=make_training(); lookup=exact_lookup(rows)
    candidates=construct_compositions(witnesses)
    holdout=[('S2','C','S0'),('S3','C','S1')]
    baseline=[]; relational=[]
    for s,a,y in holdout:
        bp=lookup.get((s,a)); rp,status=predict_unique(s,a,candidates,lookup)
        baseline.append(bp==y); relational.append(rp==y)
    # Gauge rename and compare after inverse mapping.
    rr,ww,sm,am=gauge_rename(rows,witnesses)
    rc=construct_compositions(ww); rl=exact_lookup(rr)
    gauge=[]
    for s,a,y in holdout:
        rp,status=predict_unique(sm[s],am[a],rc,rl)
        gauge.append(rp==sm[y])

    nrows,nwits=nonidentifiable_fixture(); nc=construct_compositions(nwits); nl=exact_lookup(nrows)
    npred,nstatus=predict_unique('S2','C',nc,nl)

    result={
      'milestone':'MS1653','pass':1,
      'campaign':'PRELINGUAL_ENDOGENOUS_EXPERIENCE_FRAME_RELATIONAL_ALGEBRA_CONSTRUCTION',
      'fixture_assistance':[
        'STABLE_OPAQUE_EVENT_IDENTITY','STABLE_OPAQUE_ACTION_IDENTITY','STABLE_OPAQUE_EFFECT_IDENTITY','EPISODE_ORDER_AND_ACTION_OUTCOME_BINDING'
      ],
      'explicitly_absent':['COORDINATE_SEMANTICS','VECTOR_VALUES','DISTANCE','DIRECTION','AXIS_LABELS','HIDDEN_STATE_LABELS','EXECUTION_AUTHORITY_FROM_CONSTRUCTOR'],
      'candidates':[asdict(c) for c in candidates],
      'holdout':{'rows':holdout,'exact_lookup_accuracy':sum(baseline)/len(baseline),'relational_composition_accuracy':sum(relational)/len(relational)},
      'gauge_renaming':{'renamed_predictions_equivalent':all(gauge),'state_map':sm,'action_map':am},
      'nonidentifiable':{'candidate_count':len(nc),'candidate_paths':[(c.first_action,c.second_action,c.direct_action) for c in nc],'prediction':npred,'status':nstatus},
      'checks':{
        'opaque_composition_candidate_constructed':len(candidates)==1,
        'heldout_lift_over_equality_lookup':sum(relational)>sum(baseline),
        'heldout_relational_accuracy_is_one':all(relational),
        'gauge_equivalent_under_injective_renaming':all(gauge),
        'nonidentifiable_case_preserves_multiple_candidates':len(nc)>=2,
        'nonidentifiable_case_returns_unknown':npred is None and nstatus.startswith('UNKNOWN'),
        'proposal_has_zero_truth_execution_authority':all(c.truth_authority=='NONE' and c.execution_authority=='NONE' for c in candidates+nc),
      },
      'interpretation':{
        'surviving_claim':'Exact recurrent endpoint equivalence can nominate an opaque action-composition relation that generalizes to held-out direct-action outcomes without coordinate semantics.',
        'nonclaim':'This does not prove the discovered composition is globally true, uniquely meaningful, physically complete, or executable beyond already observed actions.',
        'pal43_pressure':'Representable relational structure must remain UNKNOWN when competing equivalence classes survive; symbolic structure cannot manufacture an actuator.'
      }
    }
    result['pass']=all(result['checks'].values())
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True))
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__': main()
