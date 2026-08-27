from __future__ import annotations
from dataclasses import dataclass, asdict
from itertools import product
import json, math, random, statistics
from pathlib import Path

HABITAT_ID = 'HABITAT-R2-MS1528-ABSTENTION-COMPLETE-2026-08-24'
TICKS = 320
DRIFT_TICKS = (100, 200)
RESTART_TICKS = (80, 180, 260)
ACTIONS = ('HARVEST','COOL','REPAIR','REST')
EVALUATOR_ACTIONS = ACTIONS + ('NO_ACTION',)
BANDS = {
    'ENERGY': (4.0, 8.0),
    'THERMAL': (3.0, 7.0),
    'INTEGRITY': (5.0, 9.0),
}
CATASTROPHE = {
    'ENERGY': (1.0, 9.8),
    'THERMAL': (0.5, 9.5),
    'INTEGRITY': (1.5, 9.8),
}
ACTION_COST = {'HARVEST': 2.4, 'COOL': 1.9, 'REPAIR': 2.2, 'REST': 0.35, 'NO_ACTION': 0.0}

@dataclass
class State:
    energy: float
    thermal: float
    integrity: float

    def clamp(self) -> 'State':
        return State(*(max(0.0,min(10.0,v)) for v in (self.energy,self.thermal,self.integrity)))


def regime(t: int) -> int:
    return 0 if t < 100 else (1 if t < 200 else 2)


def deterministic_step(s: State, action: str, t: int) -> State:
    r = regime(t)
    # persistent exogenous pressure, deliberately coupled
    de = -0.30 - (0.10 if r == 2 else 0.0)
    dt = +0.18 + (0.17 if r == 1 else 0.0)
    di = -0.06 - (0.08 if r == 2 else 0.0)
    if s.thermal > 7.0:
        di -= 0.09 * (s.thermal - 7.0)
    if s.energy < 4.0:
        di -= 0.07 * (4.0 - s.energy)
    if s.integrity < 5.0:
        de -= 0.05 * (5.0 - s.integrity)

    ae = at = ai = 0.0
    if action == 'HARVEST':
        ae = 1.75 if r != 2 else 1.25
        at = 0.62 if r != 1 else 0.90
        ai = -0.18
    elif action == 'COOL':
        ae = -0.30
        at = -1.55 if r != 2 else -1.20
        ai = +0.02
    elif action == 'REPAIR':
        ae = -0.62
        at = +0.15
        ai = 1.35 if r != 2 else 0.95
    elif action == 'REST':
        ae = +0.35
        at = -0.32
        ai = +0.30
    elif action == 'NO_ACTION':
        pass
    else:
        raise ValueError(action)
    return State(s.energy+de+ae, s.thermal+dt+at, s.integrity+di+ai).clamp()


def stochastic_step(s: State, action: str, t: int, rng: random.Random) -> State:
    n = deterministic_step(s, action, t)
    # process noise exists independently of observation noise
    return State(
        n.energy + rng.gauss(0,0.08),
        n.thermal + rng.gauss(0,0.07),
        n.integrity + rng.gauss(0,0.06),
    ).clamp()


def observe(s: State, rng: random.Random):
    out={}
    for k,v in [('ENERGY',s.energy),('THERMAL',s.thermal),('INTEGRITY',s.integrity)]:
        if rng.random() < 0.12:
            out[k] = None
        else:
            out[k] = max(0.0,min(10.0,v+rng.gauss(0,0.28)))
    return out


def violation(s: State) -> float:
    vals={'ENERGY':s.energy,'THERMAL':s.thermal,'INTEGRITY':s.integrity}
    total=0.0
    for k,v in vals.items():
        lo,hi=BANDS[k]
        width=hi-lo
        if v<lo: total += (lo-v)/width
        elif v>hi: total += (v-hi)/width
    return total


def whole_viable(s: State) -> bool:
    vals={'ENERGY':s.energy,'THERMAL':s.thermal,'INTEGRITY':s.integrity}
    return all(BANDS[k][0] <= v <= BANDS[k][1] for k,v in vals.items())


def catastrophic_count(s: State) -> int:
    vals={'ENERGY':s.energy,'THERMAL':s.thermal,'INTEGRITY':s.integrity}
    return sum(not (CATASTROPHE[k][0] <= v <= CATASTROPHE[k][1]) for k,v in vals.items())


def oracle_score(s: State, total_cost: float) -> tuple:
    # evaluator-only lexicographic safety objective; hidden truth allowed here only
    return (catastrophic_count(s), violation(s), 0 if whole_viable(s) else 1, total_cost)


def oracle_action(s: State, t: int) -> str:
    # short-horizon hidden-state/model-aware evaluator ceiling; not an organism policy
    best=None
    for seq in product(EVALUATOR_ACTIONS, repeat=3):
        x=s
        cost=0.0
        worst_cat=0
        accum_violation=0.0
        viable_misses=0
        for h,a in enumerate(seq):
            x=deterministic_step(x,a,t+h)
            cost += ACTION_COST[a]
            worst_cat += catastrophic_count(x)
            accum_violation += violation(x)
            viable_misses += 0 if whole_viable(x) else 1
        score=(worst_cat, accum_violation, viable_misses, cost)
        if best is None or score < best[0]: best=(score,seq[0])
    return best[1]


def fixed_action(t:int, local_tick:int)->str:
    return ACTIONS[local_tick % len(ACTIONS)]


def run(policy: str, seed: int) -> dict:
    process_rng=random.Random(seed*1009+17)
    obs_rng=random.Random(seed*1009+23)
    policy_rng=random.Random(seed*1009+31)
    s=State(5.3,6.4,6.0)
    viable=0; viol=[]; cats=0; cost=0.0; missing=0
    local_tick=0
    for t in range(TICKS):
        if t in RESTART_TICKS:
            local_tick=0  # controller-local clock resets; world does not
            policy_rng=random.Random(seed*1009+31+t)  # local stochastic policy state also restarts
        o=observe(s,obs_rng)
        missing += sum(v is None for v in o.values())
        if policy=='ORACLE_EVALUATOR_CEILING': a=oracle_action(s,t)
        elif policy=='FIXED_CYCLE': a=fixed_action(t,local_tick)
        elif policy=='RANDOM': a=policy_rng.choice(ACTIONS)
        elif policy=='PASSIVE_NO_ACTION': a='NO_ACTION'
        else: raise ValueError(policy)
        cost += ACTION_COST[a]
        s=stochastic_step(s,a,t,process_rng)
        viable += int(whole_viable(s))
        viol.append(violation(s))
        cats += catastrophic_count(s)
        local_tick += 1
    return {
        'seed':seed,
        'whole_viability': viable/TICKS,
        'mean_violation': statistics.fmean(viol),
        'catastrophic_coordinate_ticks': cats,
        'resource_spend': cost,
        'missing_observations': missing,
        'final_state': asdict(s),
    }


def aggregate(rows):
    return {
        'whole_viability': statistics.fmean(r['whole_viability'] for r in rows),
        'mean_violation': statistics.fmean(r['mean_violation'] for r in rows),
        'catastrophic_coordinate_ticks': statistics.fmean(r['catastrophic_coordinate_ticks'] for r in rows),
        'resource_spend': statistics.fmean(r['resource_spend'] for r in rows),
    }

def dominates(a,b):
    return (a['whole_viability']>b['whole_viability'] and
            a['mean_violation']<b['mean_violation'] and
            a['catastrophic_coordinate_ticks']<b['catastrophic_coordinate_ticks'] and
            a['resource_spend']<b['resource_spend'])

def main():
    seeds=list(range(100,112))
    policies=['ORACLE_EVALUATOR_CEILING','FIXED_CYCLE','RANDOM','PASSIVE_NO_ACTION']
    rows={p:[run(p,s) for s in seeds] for p in policies}
    ag={p:aggregate(v) for p,v in rows.items()}
    per_seed={q:sum(dominates(rows['ORACLE_EVALUATOR_CEILING'][i],rows[q][i]) for i in range(len(seeds))) for q in ('FIXED_CYCLE','RANDOM')}
    passive_safety=(ag['ORACLE_EVALUATOR_CEILING']['whole_viability']>ag['PASSIVE_NO_ACTION']['whole_viability'] and ag['ORACLE_EVALUATOR_CEILING']['mean_violation']<ag['PASSIVE_NO_ACTION']['mean_violation'] and ag['ORACLE_EVALUATOR_CEILING']['catastrophic_coordinate_ticks']<ag['PASSIVE_NO_ACTION']['catastrophic_coordinate_ticks'])
    admission = dominates(ag['ORACLE_EVALUATOR_CEILING'],ag['FIXED_CYCLE']) and dominates(ag['ORACLE_EVALUATOR_CEILING'],ag['RANDOM']) and passive_safety
    out={
      'schema':'microseed.ms1528.replacement-habitat-r1-admission.v1',
      'habitat_id':HABITAT_ID,
      'new_identity':True,
      'supersedes_habitat_r1_for_organism_testing':True,
      'abstention_semantics':'NO_ACTION = exogenous/process dynamics continue; zero actuator effect and zero actuator cost',
      'not_original_step71_habitat':True,
      'parent_evidence':'Step74 states original Pass1 harness unrecoverable',
      'microseed_mutation':'NONE',
      'microseed_competence_credit':'NONE',
      'ticks':TICKS,'drift_ticks':DRIFT_TICKS,'restart_ticks':RESTART_TICKS,
      'observation_missing_probability':0.12,'observation_noise_sigma':0.28,
      'process_noise_sigma':{'energy':0.08,'thermal':0.07,'integrity':0.06},
      'bands':BANDS,'catastrophe_bounds':CATASTROPHE,'action_cost':ACTION_COST,
      'seeds':seeds,'aggregate':ag,'per_seed_strict_dominance_counts':per_seed,
      'admission_rule':'evaluator strictly Pareto-dominates forced-action RANDOM/FIXED on viability(+), violation(-), catastrophe(-), spend(-); evaluator also strictly dominates PASSIVE_NO_ACTION on the three safety dimensions while passive necessarily spends zero actuator resource',
      'admitted':admission,
      'rows':rows,
      'nonclaims':['not original Step71 habitat','not Microseed competence evidence','oracle is evaluator-only','no general ecology claim'],
    }
    p=Path('/mnt/data/ms1528_1552_campaign_work/REPLACEMENT_HABITAT_R2_ADMISSION.json')
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'admitted':admission,'aggregate':ag,'per_seed':per_seed},indent=2))

if __name__=='__main__': main()
