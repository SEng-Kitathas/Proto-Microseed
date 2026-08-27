from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path
from research.run_ms1539_pass12_r2_regulatory_consequence_projection import VALUES, collect


def mode(c):
    if not c: return None
    return sorted(c.items(),key=lambda kv:(-kv[1],kv[0]))[0][0]


def evaluate_position(channel: str, pos: int):
    train=[r for seed in range(200,208) for r in collect(seed,channel)]
    val=[r for seed in range(208,212) for r in collect(seed,channel)]
    action_tab=defaultdict(Counter)
    state_tab=defaultdict(Counter)
    state_action_tab=defaultdict(Counter)
    global_tab=Counter()
    for r in train:
        k=r.raw_tokens[pos]
        action_tab[r.action_token][r.effect_token]+=1
        state_tab[k][r.effect_token]+=1
        state_action_tab[(k,r.action_token)][r.effect_token]+=1
        global_tab[r.effect_token]+=1
    def acc(predict):
        return sum(predict(r)==r.effect_token for r in val)/max(len(val),1)
    global_mode=mode(global_tab)
    return {
        'rows':len(val),
        'global_label_baseline':acc(lambda r:global_mode),
        'action_only_baseline':acc(lambda r:mode(action_tab[r.action_token])),
        'state_only_baseline':acc(lambda r:mode(state_tab[r.raw_tokens[pos]])),
        'state_action_accuracy':acc(lambda r:mode(state_action_tab[(r.raw_tokens[pos],r.action_token)])),
    }


def main():
    positions={'ENERGY':0,'THERMAL':1,'INTEGRITY':2}
    channels={}
    for ch,pos in positions.items():
        row=evaluate_position(ch,pos)
        row['position']=pos
        row['state_action_increment_over_state_only']=row['state_action_accuracy']-row['state_only_baseline']
        row['state_action_increment_over_action_only']=row['state_action_accuracy']-row['action_only_baseline']
        channels[ch]=row
    out={
        'schema':'microseed.ms1539.pass12.antiflattery.state-vs-action.v1',
        'question':'DOES_THE_REGULATORY_TARGET_CARRY_ACTION_SPECIFIC_CONSEQUENCE_SIGNAL_BEYOND_CURRENT_STATE',
        'channels':channels,
        'disposition':'ACTION_SPECIFIC_SIGNAL_PRESENT' if any(v['state_action_increment_over_state_only']>=.05 for v in channels.values()) else 'STATE_ONLY_EXPLAINS_FLATTERING_SIGNAL',
        'nonclaims':['NO_MODEL_ADMISSION','NO_MAINDEV_MUTATION'],
    }
    p=Path(__file__).with_name('MS1539_PASS12_ANTIFLATTERY_STATE_VS_ACTION.json')
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
