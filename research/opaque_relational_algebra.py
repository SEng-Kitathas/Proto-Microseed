from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
import hashlib, json
from typing import Iterable

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()

@dataclass(frozen=True)
class Transition:
    evidence_id:str
    origin_id:str
    start:str
    action:str
    end:str

@dataclass(frozen=True)
class CompositionRelation:
    relation_id:str
    direct_action:str
    first_action:str
    second_action:str
    positive_support:int
    negative_support:int
    support_origin_signatures:tuple[str,...]
    counterexample_origin_signatures:tuple[str,...]
    proposal_authority:str='NONE'
    truth_authority:str='NONE'
    execution_authority:str='NONE'
    scope_authority:str='NONE'

    def expression(self): return (self.first_action,self.second_action,self.direct_action)

@dataclass(frozen=True)
class IdentityRelation:
    action:str
    positive_support:int
    negative_support:int
    proposal_authority:str='NONE'

@dataclass(frozen=True)
class InverseRelation:
    first_action:str
    second_action:str
    positive_support:int
    negative_support:int
    proposal_authority:str='NONE'


def _by(rows):
    # Multiple exact records may exist; require endpoint agreement for a key or treat it unavailable.
    groups=defaultdict(list)
    for r in rows:groups[(r.start,r.action)].append(r)
    out={}
    for k,rs in groups.items():
        ends={r.end for r in rs}
        if len(ends)==1:out[k]=rs[0]
    return out


def composition_stats(rows:Iterable[Transition]):
    rows=tuple(rows); by=_by(rows); states=sorted({r.start for r in rows}|{r.end for r in rows}); actions=sorted({r.action for r in rows}); stats=defaultdict(lambda:{'yes':set(),'no':set(),'opportunities':0})
    for s in states:
      for c in actions:
        d=by.get((s,c))
        if not d:continue
        for a in actions:
          r1=by.get((s,a))
          if not r1:continue
          for b in actions:
            r2=by.get((r1.end,b))
            if not r2:continue
            sig=digest(tuple(sorted({d.origin_id,r1.origin_id,r2.origin_id})))
            x=stats[(c,a,b)];x['opportunities']+=1;x['yes' if r2.end==d.end else 'no'].add(sig)
    return stats


def construct_global_compositions(rows:Iterable[Transition],min_positive_support:int=2,allow_observed_counterexamples:bool=False):
    stats=composition_stats(rows);out=[]
    for (c,a,b),v in sorted(stats.items()):
        pos=len(v['yes']);neg=len(v['no'])
        if pos<min_positive_support:continue
        if neg and not allow_observed_counterexamples:continue
        payload=(c,a,b,pos,neg,tuple(sorted(v['yes'])),tuple(sorted(v['no'])))
        out.append(CompositionRelation('COMP-'+digest(payload)[:20],c,a,b,pos,neg,tuple(sorted(v['yes'])),tuple(sorted(v['no']))))
    return out


def construct_identity(rows:Iterable[Transition],min_positive_support=2):
    rows=tuple(rows);by=_by(rows);states=sorted({r.start for r in rows});actions=sorted({r.action for r in rows});out=[]
    for a in actions:
      yes=no=0
      for s in states:
        r=by.get((s,a))
        if not r:continue
        if r.end==s:yes+=1
        else:no+=1
      if yes>=min_positive_support and no==0:out.append(IdentityRelation(a,yes,no))
    return out


def construct_inverses(rows:Iterable[Transition],min_positive_support=2):
    rows=tuple(rows);by=_by(rows);states=sorted({r.start for r in rows});actions=sorted({r.action for r in rows});out=[]
    for a in actions:
      for b in actions:
        yes=no=0
        for s in states:
          r1=by.get((s,a))
          if not r1:continue
          r2=by.get((r1.end,b))
          if not r2:continue
          if r2.end==s:yes+=1
          else:no+=1
        if yes>=min_positive_support and no==0:out.append(InverseRelation(a,b,yes,no))
    return out


def direct_lookup(rows):
    groups=defaultdict(set)
    for r in rows:
        groups[(r.start,r.action)].add(r.end)
    return {k:next(iter(v)) for k,v in groups.items() if len(v)==1}

def predict_via_composition(start,direct_action,relations,rows):
    by=direct_lookup(rows); preds=[]
    for r in relations:
      if r.direct_action!=direct_action:continue
      m=by.get((start,r.first_action));e=None if m is None else by.get((m,r.second_action))
      if e is not None:preds.append((r.expression(),e))
    values={e for _,e in preds}
    if len(values)==1:return next(iter(values)),'YES_RELATIONAL_CONSENSUS',tuple(preds)
    if len(values)>1:return None,'UNKNOWN_RELATIONAL_DISAGREEMENT',tuple(preds)
    return None,'UNKNOWN_NO_RELATION',tuple(preds)
