from __future__ import annotations
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib,json,random
from pathlib import Path

OUT=Path(__file__).with_name('MS1654_PASS02_ENDPOINT_EQUIVALENCE_BREADTH.json')

def H(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()

@dataclass(frozen=True)
class Transition:
    evidence_id:str; origin_id:str; start:str; action:str; end:str

@dataclass(frozen=True)
class CompositionCandidate:
    direct_action:str; first_action:str; second_action:str; support_origins:tuple[str,...]; proposal_authority:str='NONE'; truth_authority:str='NONE'; execution_authority:str='NONE'


def derive(rows,min_support=2):
    # Derive endpoint-equivalence witnesses automatically from actual transition records.
    by={(r.start,r.action):r for r in rows}
    states=sorted({r.start for r in rows}|{r.end for r in rows}); actions=sorted({r.action for r in rows})
    groups=defaultdict(set)
    for s in states:
      for c in actions:
        direct=by.get((s,c))
        if not direct: continue
        for a in actions:
          r1=by.get((s,a))
          if not r1: continue
          for b in actions:
            r2=by.get((r1.end,b))
            if not r2 or r2.end!=direct.end: continue
            # Support identity is physical relation block: direct origin + both path origins.
            origin_sig=H(tuple(sorted({direct.origin_id,r1.origin_id,r2.origin_id})))
            groups[(c,a,b)].add(origin_sig)
    out=[]
    for (c,a,b),origins in sorted(groups.items()):
      if len(origins)>=min_support:
        out.append(CompositionCandidate(c,a,b,tuple(sorted(origins))))
    return out


def predict(start,direct,cands,rows):
    by={(r.start,r.action):r.end for r in rows}
    preds=set()
    expr=[]
    for c in cands:
      if c.direct_action!=direct: continue
      m=by.get((start,c.first_action)); e=None if m is None else by.get((m,c.second_action))
      if e is not None:
        preds.add(e); expr.append((c.first_action,c.second_action,e))
    if len(preds)==1:return next(iter(preds)),'YES_ALL_LIVE_RELATIONS_AGREE',expr
    if len(preds)>1:return None,'UNKNOWN_LIVE_RELATIONS_DISAGREE',expr
    return None,'UNKNOWN_NO_RELATION_APPLIES',expr


def world(seed,n=7,ambiguous=False):
    rng=random.Random(seed)
    states=[f'Q{seed}-{i}' for i in range(n)]; rng.shuffle(states)
    actions=[f'ACT-{seed}-{x}' for x in 'ABCD']; rng.shuffle(actions)
    A,B,C,D=actions
    # Evaluator semantics: A=+1, B=+2, C=A then B (=+3), D=-1.
    shift={A:1,B:2,C:3,D:-1}
    rows=[]
    def add(s,a,e,tag): rows.append(Transition(H((seed,tag,s,a,e)),H((seed,'origin',tag,s,a,e)),s,a,e))
    # Components available across all states; direct C only first 3 training starts.
    for i,s in enumerate(states):
      for a in (A,B,D): add(s,a,states[(i+shift[a])%n],'component')
    train_starts=states[:3]
    for s in train_starts:
      i=states.index(s); add(s,C,states[(i+3)%n],'direct-train')
    if ambiguous:
      # Add X/Y opaque actions whose two-step path agrees with C on train starts but diverges elsewhere.
      X=f'ACT-{seed}-X';Y=f'ACT-{seed}-Y'; mids=[f'M{seed}-{i}' for i in range(n)]
      for i,s in enumerate(states): add(s,X,mids[i],'amb-x')
      for i,m in enumerate(mids):
        out=states[(i+3)%n] if i<3 else states[(i+4)%n]
        add(m,Y,out,'amb-y')
      # actions list is implicit from rows
    return states,actions,C,rows


def duplicate_rows(rows):
    # Event replay/new event IDs with SAME physical origin must not increase independent support.
    dup=[]
    for r in rows:
      dup.append(r)
      if int(r.evidence_id[0],16)%3==0:
        dup.append(Transition(H(('replay',r.evidence_id)),r.origin_id,r.start,r.action,r.end))
    return dup


def run_family(seed,ambiguous=False):
    states,actions,C,rows=world(seed,7,ambiguous)
    train_direct={r.start for r in rows if r.action==C}
    hold=[s for s in states if s not in train_direct]
    cands=derive(rows,2); cands_dup=derive(duplicate_rows(rows),2)
    exact={(r.start,r.action):r.end for r in rows}
    ok=0; unknown=0
    for s in hold:
      truth=states[(states.index(s)+3)%len(states)]
      p,status,_=predict(s,C,cands,rows)
      if p==truth: ok+=1
      if status.startswith('UNKNOWN'): unknown+=1
    baseline=sum(exact.get((s,C))==states[(states.index(s)+3)%len(states)] for s in hold)
    # Compare candidate support sets under replay; identities may change only if origin handling is wrong.
    sig=lambda cs:sorted((c.direct_action,c.first_action,c.second_action,c.support_origins) for c in cs)
    return {
      'seed':seed,'ambiguous':ambiguous,'holdout_n':len(hold),'baseline_correct':baseline,'relational_correct':ok,'unknown':unknown,
      'replay_invariant':sig(cands)==sig(cands_dup),'candidate_count':len(cands),
      'zero_authority':all(c.truth_authority=='NONE' and c.execution_authority=='NONE' for c in cands)
    }


def main():
    identifiable=[run_family(165400+i,False) for i in range(32)]
    ambiguous=[run_family(165500+i,True) for i in range(32)]
    checks={
      'identifiable_lift_all':all(x['relational_correct']>x['baseline_correct'] for x in identifiable),
      'identifiable_perfect_holdout_all':all(x['relational_correct']==x['holdout_n'] for x in identifiable),
      'origin_replay_does_not_change_candidates':all(x['replay_invariant'] for x in identifiable+ambiguous),
      'proposal_only_all':all(x['zero_authority'] for x in identifiable+ambiguous),
      # Ambiguous injected path must prevent forced success on at least some holdout states.
      'ambiguous_cases_expose_unknown':all(x['unknown']>0 for x in ambiguous),
    }
    result={'milestone':'MS1654','pass':2,'identifiable':identifiable,'ambiguous':ambiguous,'checks':checks,'pass_all':all(checks.values()),
      'scar_candidates':['EVENT_REPLAY_NE_PHYSICAL_RELATIONAL_SUPPORT','MULTIPLE_RELATIONAL_EXPRESSIONS_NE_MULTIPLE_HIDDEN_ENTITIES','CURRENT_REPERTOIRE_AGREEMENT_NE_GLOBAL_IDENTIFIABILITY'],
      'disposition':'SURVIVED_BOUNDED_ENDPOINT_EQUIVALENCE__AMBIGUITY_PRESERVED' if all(checks.values()) else 'NARROW_OR_REJECT'}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)); print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
