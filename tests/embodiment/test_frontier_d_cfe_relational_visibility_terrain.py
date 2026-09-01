
from __future__ import annotations

import itertools
import random
import tempfile
from pathlib import Path

from microseed import Authority, Microseed, OperationalFrameContract, ProjectionDiscoveryConfig, ProjectionSample, QualificationState


def _underlying_rows(repeats: int = 24):
    # Same underlying developmental episodes for every condition. Effect depends
    # on the relational XOR of x,y; z is balanced nuisance. Event order is fixed.
    rows=[]
    idx=0
    for r in range(repeats):
        combos=list(itertools.product(('0','1'), repeat=3))
        random.Random(7300+r).shuffle(combos)
        for x,y,z in combos:
            effect='E1' if x != y else 'E0'
            rows.append({'id':f'ROW-{idx}','x':x,'y':y,'z':z,'action':'B','effect':effect})
            idx+=1
    return rows


def _terrain_samples(rows, terrain: str):
    out=[]
    for row in rows:
        if terrain=='GOOD_XY': raw=(row['x'],row['y'])
        elif terrain=='GOOD_YX': raw=(row['y'],row['x'])
        elif terrain=='BAD_XZ': raw=(row['x'],row['z'])
        elif terrain=='BAD_ZY': raw=(row['z'],row['y'])
        else: raise ValueError(terrain)
        out.append(ProjectionSample(row['id'],raw,row['action'],row['effect'],'S','F',0))
    return out


def _new_ms(td):
    ms=Microseed(Path(td.name))
    ms.register_operational_frame(OperationalFrameContract('F','frontier-d-cfe-frame','f'*64,Authority.DERIVED_READ_ONLY,('MS_FRONTIER_HELIX_V1:D_CFE',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    return ms

def _discover(ms: Microseed, rows):
    # Fixed search budget and thresholds in every condition.
    train=tuple(rows[:128]); validation=tuple(rows[128:])
    cfg=ProjectionDiscoveryConfig(
        max_subset=2,min_train_support=96,min_key_action_support=8,
        min_validation_accuracy=.95,min_lift_over_action_baseline=.35,
        min_scope_accuracy=.95,max_candidates=4,
    )
    found=ms.discover_epistemic_projection_candidates(train,validation,cfg)
    return [ms.epistemic_projection_candidates[x['candidate_id']] for x in found]


def _marginal_counts(samples):
    cols=[{},{}]
    for s in samples:
        for i,v in enumerate(s.raw_tokens):
            cols[i][v]=cols[i].get(v,0)+1
    return cols


def test_external_relational_covizibility_changes_discovery_with_matched_episodes_and_search_budget():
    td=tempfile.TemporaryDirectory(prefix='frontier-d-cfe-')
    ms=_new_ms(td)
    try:
        underlying=_underlying_rows()
        good=_terrain_samples(underlying,'GOOD_XY')
        bad=_terrain_samples(underlying,'BAD_XZ')
        assert len(good)==len(bad)==len(underlying)
        # Same event IDs/order, action stream, and outcome stream.
        assert [s.sample_id for s in good]==[s.sample_id for s in bad]
        assert [s.action_token for s in good]==[s.action_token for s in bad]
        assert [s.effect_token for s in good]==[s.effect_token for s in bad]
        # Same per-coordinate opaque marginal exposure counts; only which relation
        # is jointly visible changes.
        assert _marginal_counts(good)==_marginal_counts(bad)==[{'0':96,'1':96},{'0':96,'1':96}]

        good_candidates=_discover(ms,good)
        bad_candidates=_discover(ms,bad)
        exact=[c for c in good_candidates if c.input_positions==(0,1)]
        assert exact and exact[0].validation_accuracy==1.0
        assert exact[0].lift>=.49
        assert bad_candidates==[]
    finally:
        try: ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
        finally: td.cleanup()


def test_coordinate_permutation_does_not_create_the_effect_and_geometry_reversion_restores_discovery():
    rows=_underlying_rows()
    results={}
    for terrain in ('GOOD_XY','GOOD_YX','BAD_XZ','BAD_ZY','GOOD_XY'):
        td=tempfile.TemporaryDirectory(prefix='frontier-d-cfe-')
        ms=_new_ms(td)
        try:
            cs=_discover(ms,_terrain_samples(rows,terrain))
            results.setdefault(terrain,[]).append([(c.input_positions,c.validation_accuracy,round(c.lift,6)) for c in cs])
        finally:
            try: ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
            finally: td.cleanup()
    # Pure coordinate order is irrelevant: both causal topologies work.
    assert results['GOOD_XY'][0] == results['GOOD_YX'][0]
    # Both matched nuisance topologies fail to expose a predictive pair.
    assert results['BAD_XZ'][0] == []
    assert results['BAD_ZY'][0] == []
    # Removing then restoring relational visibility restores discovery without any
    # organism mutation or extra experience budget.
    assert results['GOOD_XY'][0] == results['GOOD_XY'][1]


def test_current_microseed_has_no_owned_terrain_topology_surface():
    td=tempfile.TemporaryDirectory(prefix='frontier-d-cfe-')
    ms=_new_ms(td)
    try:
        # This is the transfer boundary: terrain is presently an external evidence
        # access condition, not an organism-owned semantic/authority/currentness owner.
        for forbidden in ('developmental_geometry','terrain_topology','relational_visibility_graph','cfe_field'):
            assert not hasattr(ms,forbidden)
    finally:
        try: ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
        finally: td.cleanup()
