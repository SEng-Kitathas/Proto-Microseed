from __future__ import annotations
import json,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from microseed import Microseed
from microseed.persistence.biography import DevelopmentalBiography
from microseed.persistence.identity import continuity_witness_from_exports


def main():
    out={}
    with tempfile.TemporaryDirectory(prefix='ms1028-1052-replay-') as td:
        ms=Microseed(Path(td))
        source=ms.biography_witness()
        same=ms.developmental_continuity_witness(source)
        out['same_graph_relation']=same['relation']
        out['same_graph_copy_ambiguity']=same['copy_ambiguity']
        out['same_graph_numerical_identity_authority']=same['numerical_identity_authority']
        ms.path.append('STRUCTURAL_REWRITE_REPLAY',{'topology_delta':'opaque'})
        desc=ms.developmental_continuity_witness(source)
        out['rewrite_relation']=desc['relation']
        out['rewrite_branch_semantics']=desc['branch_semantics']
        out['rewrite_selfhood_claim']=desc['selfhood_claim']
        status=ms.status()
        out['status_identity_claim']=status['identity_claim']
        out['exclusive_successor_authority']=status['exclusive_successor_authority']
        out['language']=status['language']
        out['next_ms']=status['next_ms']
        out['next_started']=status.get(f"ms{status['next_ms']}_started")
        out['frontier']=status['frontier']
        out['internal_unique_successor_api_absent']=not any(hasattr(ms,n) for n in ('claim_unique_identity','select_original_copy','grant_exclusive_successor_authority'))

    with tempfile.TemporaryDirectory(prefix='ms1052-a-') as ad, tempfile.TemporaryDirectory(prefix='ms1052-b-') as bd:
        anchor={'shared':'replay-anchor','historical_biography_before_v0_6':'UNKNOWN_INCOMPLETE'}
        a=DevelopmentalBiography(Path(ad)/'b.sqlite3',legacy_anchor=anchor)
        b=DevelopmentalBiography(Path(bd)/'b.sqlite3',legacy_anchor=anchor)
        identical=DevelopmentalBiography.relation(a.export(),b.export())
        out['perfect_copy_graph_relation']=identical
        a.append('BRANCH_LOCAL',{'v':'A'});b.append('BRANCH_LOCAL',{'v':'B'})
        rel=DevelopmentalBiography.relation(a.export(),b.export())
        w=continuity_witness_from_exports(a.export(),b.export(),relation=rel).serializable()
        out['post_divergence_relation']=rel
        out['post_divergence_semantics']=w['branch_semantics']
        out['post_divergence_numerical_identity_authority']=w['numerical_identity_authority']
        a.close();b.close()

    checks={
      'structural_rewrite_is_descendant':out['rewrite_relation']=='DESCENDANT_CONTINUATION',
      'same_biography_graph_is_copy_ambiguous':out['same_graph_relation']=='SAME_BIOGRAPHY_STATE' and out['same_graph_copy_ambiguity'] is True,
      'same_graph_grants_no_numerical_identity':out['same_graph_numerical_identity_authority']=='NONE',
      'perfect_copy_graphs_are_not_disambiguated':out['perfect_copy_graph_relation']=='SAME_BIOGRAPHY_STATE',
      'divergence_produces_sibling_branch_relation':out['post_divergence_relation']=='COMMON_ANCESTRY_DIVERGED' and out['post_divergence_semantics']=='SIBLING_OR_DIVERGED_BRANCHES',
      'no_selfhood_promotion':out['rewrite_selfhood_claim']=='NOT_QUALIFIED' and out['status_identity_claim']=='NOT_QUALIFIED',
      'exclusive_successor_not_internal':out['exclusive_successor_authority']=='NOT_ESTABLISHED_BY_INTERNAL_BIOGRAPHY' and out['internal_unique_successor_api_absent'],
      'prelingual_hard_stop':out['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE' and out['next_ms']>=1203 and out['next_started'] is False,
      'selected_frontier':out.get('research_terminal_ms',1252)>=1252 and out['frontier'].startswith('ATTN-MS'),
    }
    doc={'schema':'microseed.ms1028-1052.maindev-replay.v1','observations':out,'checks':checks,'all_pass':all(checks.values())}
    print(json.dumps(doc,indent=2,sort_keys=True)); return 0 if doc['all_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
