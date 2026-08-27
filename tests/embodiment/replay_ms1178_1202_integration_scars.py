from __future__ import annotations
import hashlib, json, tempfile
from pathlib import Path
from microseed import Microseed, EpistemicStatus, EpistemicContrastBinding, EpistemicContrastRow

def H(x): return hashlib.sha256(x.encode()).hexdigest()
def main():
  with tempfile.TemporaryDirectory(prefix='ms1178-1202-replay-') as td:
    m=Microseed(Path(td))
    m.register_epistemic_projection('P',H('projection:P'),assistance_ancestry=('SUPPLIED_OPAQUE_PROJECTION',))
    m.append_evidence('U',{'ambiguous':True},EpistemicStatus.UNKNOWN_INCOMPLETE,source='REPLAY')
    d=m.record_action_limited_unknown(deficit_id='D',question_key='opaque',hypothesis_digest_sha256=H('HSET'),unknown_evidence_id='U',missing_discriminator_signature_sha256=H('missing'))
    b=EpistemicContrastBinding(binding_id='B',deficit_id='D',hypothesis_digest_sha256=d.hypothesis_digest_sha256,rows=(EpistemicContrastRow('P',0,(('h0',H('A')),('h1',H('B'))),None),),assistance_ancestry=('SUPPLIED_OPAQUE_CONTRAST',))
    m.register_epistemic_contrast(b)
    m.append_evidence('E-CONS',{'epistemic_projection':{'projection_id':'P','projection_epoch':0,'outcome_digest_sha256':H('A')}},EpistemicStatus.PRESSURE_SUPPORTED,source='REPLAY')
    # discriminating profile means A is still discriminating because h0 != h1
    r=m.assess_epistemic_evidence_bearing('D','B','E-CONS')
    witness=m.epistemic_bearing_witnesses('D')[0]
    s=m.status()
    checks={
      'bounded_bearing_recognized':r['bearing_kind']=='DISCRIMINATES_LIVE_SET' and r['bearing'] is True,
      'bearing_only_requests_revisit':m.epistemic_deficit_status('D')['state']=='REVISIT_REQUIRED',
      'bearing_no_truth':witness['truth_authority']=='NONE' and witness['answer_authority']=='NONE',
      'bearing_no_semantics':witness['semantic_question_authority']=='NONE',
      'raw_projection_discovery_absent':not hasattr(m,'discover_epistemic_projection'),
      'scheduler_absent':not hasattr(m,'schedule_question_revisits'),
      'current_frontier':s['research_terminal_ms']>=1252 and s['frontier'].startswith('ATTN-MS'),
      'hard_stop':s['next_ms']>=1203 and s.get(f"ms{s['next_ms']}_started") is False,
      'prelingual':s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE',
      'numerical_selfhood_unqualified':s['identity_claim']=='NOT_QUALIFIED',
    }
    out={'schema':'microseed.ms1178-1202.maindev-replay.v1','checks':checks,'passed':sum(checks.values()),'total':len(checks),'all_pass':all(checks.values()),'status':s}
    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out['all_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
