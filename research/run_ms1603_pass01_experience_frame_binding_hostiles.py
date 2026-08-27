from __future__ import annotations
import json
from pathlib import Path
from microseed import Microseed
from microseed.cognition.hypothesis import Hypothesis

PROBES=("PASSIVE","POST_PREDICTION_PERTURB")


def discriminate(observations):
    # Candidate frame roles are opaque handles. Their only operational content is
    # the bounded predicted post-prediction mediation pattern for this fixture.
    h_physical=Hypothesis("STREAM-PHYSICAL-ACTUAL", lambda p: "PHYSICAL_CHANGED+EFFECT_CHANGED" if p=="POST_PREDICTION_PERTURB" else "AMBIGUOUS_PASSIVE")
    h_pred=Hypothesis("STREAM-PREDICTED-ACTUAL", lambda p: "PREDICTED_CHANGED+EFFECT_CHANGED" if p=="POST_PREDICTION_PERTURB" else "AMBIGUOUS_PASSIVE")
    m=Microseed(Path('/tmp')/'ms1603-pass1-scratch')
    return m.active_discrimination([h_physical,h_pred],list(PROBES),observations)


def main():
    passive=discriminate([("PASSIVE","AMBIGUOUS_PASSIVE")])
    lawful_before=discriminate([("PASSIVE","AMBIGUOUS_PASSIVE")])
    lawful_probe=lawful_before["next_probe"]
    lawful_after=discriminate([
        ("PASSIVE","AMBIGUOUS_PASSIVE"),
        (lawful_probe,"PHYSICAL_CHANGED+EFFECT_CHANGED"),
    ])
    # PAL167 scar imported only as hostile pressure: wrong stream changes while an
    # unrelated disturbance changes the consequence. Existing bounded hypothesis
    # elimination cannot tell co-change from causal mediation.
    exogenous_after=discriminate([
        ("PASSIVE","AMBIGUOUS_PASSIVE"),
        ("POST_PREDICTION_PERTURB","PREDICTED_CHANGED+EFFECT_CHANGED"),
    ])
    cochange=discriminate([
        ("PASSIVE","AMBIGUOUS_PASSIVE"),
        ("POST_PREDICTION_PERTURB","AMBIGUOUS_PASSIVE"),
    ])
    no_effect=discriminate([
        ("PASSIVE","AMBIGUOUS_PASSIVE"),
        ("POST_PREDICTION_PERTURB","AMBIGUOUS_PASSIVE"),
    ])
    # Gauge attack: rename candidate streams; behavior should remain structurally identical.
    h_a=Hypothesis("A", lambda p: "A_CHANGED+EFFECT_CHANGED" if p=="POST_PREDICTION_PERTURB" else "AMBIG")
    h_b=Hypothesis("B", lambda p: "B_CHANGED+EFFECT_CHANGED" if p=="POST_PREDICTION_PERTURB" else "AMBIG")
    gm=Microseed(Path('/tmp')/'ms1603-pass1-gauge')
    gauge_before=gm.active_discrimination([h_a,h_b],["PASSIVE","POST_PREDICTION_PERTURB"],[("PASSIVE","AMBIG")])
    gauge_after=gm.active_discrimination([h_a,h_b],["PASSIVE","POST_PREDICTION_PERTURB"],[("PASSIVE","AMBIG"),("POST_PREDICTION_PERTURB","A_CHANGED+EFFECT_CHANGED")])
    out={
        "pass":"MS1603_PASS01",
        "discriminator":"Can existing Microseed discrimination identify actual-event stream role while refusing passive ambiguity and exogenous co-change?",
        "passive":passive,
        "lawful_causal_fixture":{"probe":lawful_probe,"after":lawful_after},
        "exogenous_covariation_hostile":exogenous_after,
        "multiple_or_nonunique_change":cochange,
        "no_downstream_effect_change":no_effect,
        "gauge_rename":{"before":gauge_before,"after":gauge_after},
        "result":"NARROWED__EXISTING_DISCRIMINATION_CAN_CONSUME_A_BOUNDED_CAUSAL_CONTRAST_BUT_CANNOT_DISTINGUISH_CAUSAL_MEDIATION_FROM_EXOGENOUS_COVARIATION",
        "scar":"INTERVENTION_EFFECT_COVARIATION != INTERVENTION_EFFECT_CAUSATION",
        "authority":"RESEARCH_ONLY",
    }
    Path('research/MS1603_PASS01_EXPERIENCE_FRAME_BINDING_HOSTILES.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
