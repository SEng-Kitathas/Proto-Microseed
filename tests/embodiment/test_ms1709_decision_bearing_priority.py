from pathlib import Path
import tempfile
from microseed import Authority, EpistemicStatus, FeasibilityState, Microseed, QualificationState, ValueVariableContract
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.development.epistemic_priority import derive_regulatory_decision_bearing_commitment
from microseed.development.recruitment import RecruitmentOption
from microseed.development.rehearsal import RehearsalTransitionRelation
from microseed.runtime.commitment import TernaryCommitment

def rel(cap,effect): return RehearsalTransitionRelation('s0',cap,'n'+cap,effect,8,1.0,(f'E-{cap}-{effect}',),0,('F',0),('EP',0))
def fixture(value=-1.0):
 td=tempfile.TemporaryDirectory();m=Microseed(Path(td.name));m.register_value_variable(ValueVariableContract('V','reg',0,10,'v'*64,Authority.REFERENCE_ONLY,('T',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED));m.observe_value_state('V',value);m.append_evidence('E-U',{'u':1},EpistemicStatus.UNKNOWN_INCOMPLETE);m.record_action_limited_unknown(deficit_id='D',question_key='Q',hypothesis_digest_sha256='a'*64,unknown_evidence_id='E-U',missing_discriminator_signature_sha256='d'*64,premise_anchors=(EpistemicCurrentnessAnchor('VALUE','V',0),));return td,m

def derive(m,sets,opts): return derive_regulatory_decision_bearing_commitment(deficit=m.epistemic_deficits.records['D'],values=m.values,relation_sets=sets,options=opts,start_state_id='s0',current_capability_epochs={'A':0,'B':0},current_frame_epochs={'F':0},current_episode_epochs={'EP':0})

def test_different_executable_actions_under_live_alternatives_is_decision_bearing_yes():
 td,m=fixture();opts=(RecruitmentOption('A',FeasibilityState.FEASIBLE),RecruitmentOption('B',FeasibilityState.FEASIBLE));h1={('s0','A'):rel('A',2),('s0','B'):rel('B',0)};h2={('s0','A'):rel('A',0),('s0','B'):rel('B',2)}
 try: assert derive(m,(h1,h2),opts).licenses_yes()
 finally:td.cleanup()

def test_same_current_action_under_all_alternatives_is_not_priority():
 td,m=fixture();opts=(RecruitmentOption('A',FeasibilityState.FEASIBLE),RecruitmentOption('B',FeasibilityState.FEASIBLE));h={('s0','A'):rel('A',2),('s0','B'):rel('B',0)}
 try: assert derive(m,(h,h),opts).licenses_no()
 finally:td.cleanup()

def test_zero_current_regulatory_pressure_is_not_priority():
 td,m=fixture(5);opts=(RecruitmentOption('A',FeasibilityState.FEASIBLE),RecruitmentOption('B',FeasibilityState.FEASIBLE));h1={('s0','A'):rel('A',2),('s0','B'):rel('B',0)};h2={('s0','A'):rel('A',0),('s0','B'):rel('B',2)}
 try: assert derive(m,(h1,h2),opts).licenses_no()
 finally:td.cleanup()

def test_stale_relational_frame_returns_unknown_not_priority():
 td,m=fixture();opts=(RecruitmentOption('A',FeasibilityState.FEASIBLE),RecruitmentOption('B',FeasibilityState.FEASIBLE));h1={('s0','A'):rel('A',2),('s0','B'):rel('B',0)};h2={('s0','A'):rel('A',0),('s0','B'):rel('B',2)}
 try:
  r=derive_regulatory_decision_bearing_commitment(deficit=m.epistemic_deficits.records['D'],values=m.values,relation_sets=(h1,h2),options=opts,start_state_id='s0',current_capability_epochs={'A':0,'B':0},current_frame_epochs={'F':1},current_episode_epochs={'EP':0});assert r.commitment==TernaryCommitment.UNKNOWN
 finally:td.cleanup()

def test_unknown_feasibility_can_remove_decision_divergence_without_becoming_priority():
 td,m=fixture();opts=(RecruitmentOption('A',FeasibilityState.FEASIBLE),RecruitmentOption('B',FeasibilityState.UNKNOWN));h1={('s0','A'):rel('A',2),('s0','B'):rel('B',0)};h2={('s0','A'):rel('A',0),('s0','B'):rel('B',2)}
 try: assert not derive(m,(h1,h2),opts).licenses_yes()
 finally:td.cleanup()
