from __future__ import annotations
import hashlib, json, tempfile, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from microseed import (
    Microseed, Authority, CapabilityContract, CapabilityCandidate,
    EpisodeSchemaContract, ExternalCapabilityQualifier, EpistemicStatus,
    QualificationState, ValueVariableContract,
)


def value_contract():
    return ValueVariableContract(
        value_id='V', purpose='opaque-regulatory-variable', viable_low=.4, viable_high=.8,
        signature_sha256=hashlib.sha256(b'V:.4:.8').hexdigest(),
        authority=Authority.DERIVED_READ_ONLY, lineage=('MS953-977',), currentness='CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL'),
        invariants=('NO_SEMANTIC_GOAL_AUTHORITY','NO_SELF_MODIFIABLE_VALUE_AUTHORITY'),
    )


def q(cid,deps=()):
    return CapabilityContract(
        cid,'opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS953-977-REPLAY',),'CURRENT',{},
        dependencies=tuple(deps), qualification=QualificationState.SHADOW_QUALIFIED,
    )


def main():
    with tempfile.TemporaryDirectory(prefix='ms953-977-replay-') as td:
        ms=Microseed(Path(td)); ms.register_value_variable(value_contract())
        before=ms.value_pressure('V')
        ms.observe_value_state('V',.2); low=ms.value_pressure('V')
        ms.observe_value_state('V',1.0); high=ms.value_pressure('V')
        ms.observe_value_state('V',.6); inside=ms.value_pressure('V')

        ep=EpisodeSchemaContract(
            schema_id='EPV', purpose='opaque-regulatory-relative-grouping',
            signature_sha256=hashlib.sha256(b'epv').hexdigest(), authority=Authority.DERIVED_READ_ONLY,
            lineage=('MS953-977',), currentness='CURRENT', qualification=QualificationState.SHADOW_QUALIFIED,
            assistance_ancestry=('EXTERNAL_EPISODE_SCHEMA_QUALIFICATION',), frame_epochs=(),
            value_epochs=(('V',0),), invariants=('NO_SEMANTIC_GOAL_AUTHORITY',),
        )
        ms.register_episode_schema(ep)
        ms.register_capability(q('M'),value_dependencies=(('V',0),))
        ms.register_capability(q('N',('M',)))

        # Pending candidate binds to the same constitutional value epoch.
        prop=ms.append_evidence('MS977-REPLAY-PROP',{'candidate':'CV'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MICROSEED_PROPOSAL')
        proposed=CapabilityContract('CV','opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS953-977',),'CANDIDATE',{},qualification=QualificationState.CANDIDATE)
        cand=CapabilityCandidate(
            candidate_id='CV', proposed_contract=proposed, evidence=(prop,),
            assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL'),
            nomination_basis='VALUE_RELEVANT_OPERATIONAL_COMPOSITION', operational_signature={'value_epochs':(('V',0),)},
        )
        ms.nominate_capability_candidate(cand)
        ext=ms.append_evidence('HSP-MS977-REPLAY',{'heldout':1.0},EpistemicStatus.PROVED,source='HSP_EXTERNAL')
        ticket=ExternalCapabilityQualifier(ms.evidence,qualifier_id='HSP-MS977-REPLAY').qualify(cand,qualification_evidence=(ext,))

        stale=ms.change_value_variable('V',reason='MS977_REPLAY_VALUE_CONTRACT_DRIFT')
        after=ms.value_pressure('V')
        pending_rejected=False; pending_reason=None
        try: ms.admit_capability_candidate(ticket)
        except ValueError as exc: pending_rejected=True; pending_reason=str(exc)

        status=ms.status()
        checks={
            'pressure_requires_current_observation': before['status']=='UNKNOWN_INCOMPLETE',
            'signed_bipolar_pressure': low['signed_pressure']>0 and high['signed_pressure']<0 and inside['signed_pressure']==0.0,
            'pressure_has_no_semantic_goal_authority': low['authority']=='DERIVED_REGULATORY_PRESSURE_ONLY' and low['semantic_goal_authority']=='NONE',
            'constitutional_prior_explicit': low['constitutional_prior_origin']=='SUPPLIED_AND_PROVENANCED',
            'value_drift_makes_pressure_unknown': after['status']=='UNKNOWN_INCOMPLETE',
            'value_drift_stales_direct_capability': 'M' in stale and ms.capabilities.contracts['M'].qualification==QualificationState.STALE,
            'value_drift_stales_second_order': 'N' in stale and ms.capabilities.contracts['N'].qualification==QualificationState.STALE,
            'value_drift_stales_episode_schema': not ms.episodes.is_current('EPV'),
            'pending_candidate_value_drift_rejected': pending_rejected and 'CANDIDATE_VALUE_EPOCH_DRIFT:V' in (pending_reason or ''),
            'pressure_path_cannot_rewrite_constitution': not hasattr(ms,'set_value_viable_interval') and not hasattr(ms,'rewrite_constitutional_value'),
            'goal_formation_not_promoted': status['goal_formation']=='NOT_QUALIFIED',
            'persistent_selfhood_not_promoted': status['identity_claim']=='NOT_QUALIFIED',
            'prelingual_hard_stop': status['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE' and status['next_ms']>=1203 and status.get(f"ms{status['next_ms']}_started") is False,
            'selected_cross_family_frontier': status['research_terminal_ms']>=1252 and status['frontier'].startswith('ATTN-MS'),
        }
        out={
            'schema':'microseed.ms953-977-maindev-replay.v0.7',
            'before_observation':before,'low_pressure':low,'high_pressure':high,'inside_pressure':inside,
            'after_value_drift':after,'stale_capabilities':sorted(stale),
            'pending_drift_rejected':pending_rejected,'pending_drift_reason':pending_reason,
            'status':status,'checks':checks,'all_pass':all(checks.values()),
        }
        print(json.dumps(out,indent=2,sort_keys=True))
        return 0 if out['all_pass'] else 1

if __name__=='__main__': raise SystemExit(main())
