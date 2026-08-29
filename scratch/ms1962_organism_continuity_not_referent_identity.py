from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed.persistence.biography import DevelopmentalBiography
from microseed.persistence.identity import continuity_witness_from_exports
from scratch.ms1961_joint_sensor_actuator_symmetry import run_joint_symmetry


def run_continuity_hostile():
    symmetry=run_joint_symmetry()
    assert symmetry['status']=='PASS'
    assert symmetry['session_a_alignment'] != symmetry['session_b_alignment_after_joint_alias_swap']

    td=tempfile.TemporaryDirectory(prefix='ms1962-bio-')
    bio=DevelopmentalBiography(Path(td.name)/'bio.sqlite3')
    try:
        e0=bio.append('PROTO_REFERENT_SESSION',{
            'session':'A',
            'local_signatures':sorted(symmetry['shared_local_signatures']),
            'identity_authority':'NONE',
        })
        source=bio.export()
        # Same organism branch continues and later observes an alias-swapped session.
        e1=bio.append('PROTO_REFERENT_SESSION',{
            'session':'B',
            'local_signatures':sorted(symmetry['shared_local_signatures']),
            'identity_authority':'NONE',
        },parents=(e0.event_id,))
        target=bio.export()
        relation=DevelopmentalBiography.relation(source,target)
        witness=continuity_witness_from_exports(source,target,relation=relation)
        assert relation=='DESCENDANT_CONTINUATION'
        assert witness.branch_semantics=='BRANCH_RELATIVE_DESCENDANT_CONTINUATION'
        assert witness.numerical_identity_authority=='NONE'

        # Yet the same two local signatures align to opposite external latent sources.
        # Organism developmental continuity is therefore compatible with both mappings.
        a=symmetry['session_a_alignment']
        b=symmetry['session_b_alignment_after_joint_alias_swap']
        assert set(a)==set(b)
        assert all(a[k]!=b[k] for k in a)

        return {
            'status':'PASS',
            'biography_relation':relation,
            'continuity_witness':witness.serializable(),
            'session_a_alignment':a,
            'session_b_alignment':b,
            'earned':'ORGANISM_DEVELOPMENTAL_CONTINUITY_DOES_NOT_BREAK_EXTERNAL_REFERENT_ALIAS_SYMMETRY',
            'identity_authority':'NONE',
            'required_breaker':'REFERENT_SPECIFIC_CAUSAL_CONTINUITY_OR_ASYMMETRIC_OVERLAP_EVIDENCE',
        }
    finally:
        bio.close(); td.cleanup()


def main(): print(json.dumps(run_continuity_hostile(),indent=2,sort_keys=True))
if __name__=='__main__': main()
