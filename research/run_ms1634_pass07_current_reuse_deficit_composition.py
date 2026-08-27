from __future__ import annotations
import hashlib,json
from pathlib import Path
from microseed import Authority,CapabilityContract,EpistemicCurrentnessAnchor,EpistemicStatus,QualificationState
from research.run_ms1629_pass02_split_historical_admission_basis import established

def sha(s): return hashlib.sha256(s.encode()).hexdigest()

def main():
    td,m,c,rid=established()
    try:
        # Prospective mapping repair creates a fresh live-use epoch while old historical basis stays valid.
        m.capabilities.change_dependency('OBS',reason='PROSPECTIVE_MAPPING_CHANGE')
        oc=m.capabilities.contracts['OBS'];oc.qualification=QualificationState.SHADOW_QUALIFIED;oc.currentness='CURRENT'
        m.capabilities.change_dependency('LIVE-BASIS',reason='FRESH_LIVE_USE_BASIS_FOR_NEW_MAPPING')
        lc=m.capabilities.contracts['LIVE-BASIS'];lc.qualification=QualificationState.SHADOW_QUALIFIED;lc.currentness='CURRENT'
        m.register_capability(CapabilityContract('MAP-COMPAT-PROBE','bounded old/new mapping compatibility probe',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1634',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'result':'OPAQUE_COMPATIBILITY_EVIDENCE'}))
        u=m.append_evidence('MS1634-UNKNOWN',{'kind':'CURRENT_REUSE_UNKNOWN','historical_relation_id':rid,'old_admission_basis':['HIST-ADMIT',0],'new_live_basis':['LIVE-BASIS',m.capabilities.epochs['LIVE-BASIS']]},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH-FIXTURE')
        rec=m.record_action_limited_unknown(deficit_id='DEF-CURRENT-REUSE',question_key=f'reuse:{rid}:new-live-basis',hypothesis_digest_sha256=sha('reuse hypotheses'),unknown_evidence_id=u.evidence_id,missing_discriminator_signature_sha256=sha('mapping compatibility'),premise_anchors=(EpistemicCurrentnessAnchor('CAPABILITY_PREMISE','LIVE-BASIS',m.capabilities.epochs['LIVE-BASIS']),),assistance_ancestry=('BOUNDED_QUERY_SUPPLIED',))
        bound=m.bind_probe_capability('DEF-CURRENT-REUSE','MAP-COMPAT-PROBE')
        before=m.epistemic_deficit_status('DEF-CURRENT-REUSE')
        m.invalidate_capability('MAP-COMPAT-PROBE',reason='TEMPORARY_PROBE_ACCESS_LOSS')
        after_probe_loss=m.epistemic_deficit_status('DEF-CURRENT-REUSE')
        relation=m.action_outcome_predictive_relation_status(rid)
        out={'pass':'MS1634_PASS07','relation_historical_status':relation,'deficit_before_probe_loss':before,'deficit_after_probe_loss':after_probe_loss,
             'result':'EXISTING_EPISTEMIC_DEFICIT_LIFECYCLE_CAN_CARRY_CURRENT_REUSE_UNKNOWN_SEPARATELY_FROM_HISTORICAL_RELATION_VALIDITY','scar':'HISTORICAL_RELATION_VALID != CURRENT_MAPPING_COMPATIBILITY_PROVED','authority':'RESEARCH_ONLY','next':'VERIFY_NO_EXISTING_EXECUTION_OR_REHEARSAL_PATH_LAUNDERS_HISTORICAL_VALIDITY_INTO_CURRENT_USE'}
        Path('research/MS1634_PASS07_CURRENT_REUSE_DEFICIT_COMPOSITION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
    finally: td.cleanup()
if __name__=='__main__':main()
