
from __future__ import annotations

import itertools
import random
import tempfile
from pathlib import Path

from microseed import (
    Authority, Microseed, OperationalFrameContract,
    ProjectionDiscoveryConfig, ProjectionSample, QualificationState,
)

FAMILIES=(
    ('BINARY_PARITY',2,lambda x,y:(x+y)%2),
    ('TERNARY_MODULAR',3,lambda x,y:(x+2*y)%3),
    ('QUATERNARY_MODULAR',4,lambda x,y:(3*x+y)%4),
)


def _new_ms(td):
    ms=Microseed(Path(td.name))
    ms.register_operational_frame(OperationalFrameContract(
        'F','hardening-sh5-frame','5'*64,Authority.DERIVED_READ_ONLY,('MS_SUBSTRATE_HARDENING_V1:SH5',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
    ))
    return ms


def _token_maps(n:int,seed:int):
    rng=random.Random(seed)
    base=[f'v{i}' for i in range(n)]
    ax=base[:];ay=base[:];az=base[:];eff=[f'e{i}' for i in range(n)]
    rng.shuffle(ax);rng.shuffle(ay);rng.shuffle(az);rng.shuffle(eff)
    return {i:'X-'+ax[i] for i in range(n)},{i:'Y-'+ay[i] for i in range(n)},{i:'Z-'+az[i] for i in range(n)},{i:'R-'+eff[i] for i in range(n)}


def _underlying(name,n,fn,repeats=10):
    rows=[];idx=0
    for r in range(repeats):
        combos=list(itertools.product(range(n),repeat=3));random.Random(50000+n*100+r).shuffle(combos)
        for x,y,z in combos:
            rows.append({'id':f'{name}-{idx}','x':x,'y':y,'z':z,'effect':fn(x,y)});idx+=1
    return rows


def _samples(rows,*,n,terrain,seed=0):
    mx,my,mz,me=_token_maps(n,seed)
    out=[]
    for row in rows:
        if terrain=='GOOD_XY': raw=(mx[row['x']],my[row['y']])
        elif terrain=='GOOD_YX': raw=(my[row['y']],mx[row['x']])
        elif terrain=='BAD_XZ': raw=(mx[row['x']],mz[row['z']])
        elif terrain=='BAD_ZY': raw=(mz[row['z']],my[row['y']])
        else: raise ValueError(terrain)
        out.append(ProjectionSample(row['id'],raw,'ACT-Q',me[row['effect']],'S','F',0))
    return tuple(out)


def _discover(rows):
    td=tempfile.TemporaryDirectory(prefix='hardening-sh5-');ms=_new_ms(td)
    try:
        cut=max(48,int(len(rows)*0.70))
        found=ms.discover_epistemic_projection_candidates(
            rows[:cut],rows[cut:],ProjectionDiscoveryConfig(
                max_subset=2,min_train_support=48,min_key_action_support=4,
                min_validation_accuracy=.98,min_lift_over_action_baseline=.35,
                min_scope_accuracy=.98,max_candidates=8,
            )
        )
        cs=[ms.epistemic_projection_candidates[x['candidate_id']] for x in found]
        return [(c.input_positions,c.validation_accuracy,c.lift,len(set(b for _,b in c.key_to_bucket))) for c in cs]
    finally:
        ms.biography.close();ms.evidence.conn.close();ms.store.conn.close();td.cleanup()


def test_relational_covizibility_effect_generalizes_across_binary_ternary_and_quaternary_causal_algebras():
    for name,n,fn in FAMILIES:
        underlying=_underlying(name,n,fn)
        good=_discover(_samples(underlying,n=n,terrain='GOOD_XY',seed=11+n))
        bad_xz=_discover(_samples(underlying,n=n,terrain='BAD_XZ',seed=11+n))
        bad_zy=_discover(_samples(underlying,n=n,terrain='BAD_ZY',seed=11+n))
        exact=[x for x in good if x[0]==(0,1)]
        assert exact,name
        assert exact[0][1]>=.98 and exact[0][2]>=.35
        assert exact[0][3]==n
        assert bad_xz==[],(name,bad_xz)
        assert bad_zy==[],(name,bad_zy)


def test_terrain_effect_survives_coordinate_order_row_order_and_opaque_alphabet_permutation():
    for name,n,fn in FAMILIES:
        underlying=_underlying(name,n,fn)
        base=_samples(underlying,n=n,terrain='GOOD_XY',seed=100+n)
        swapped=_samples(underlying,n=n,terrain='GOOD_YX',seed=100+n)
        opaque_permuted=_samples(underlying,n=n,terrain='GOOD_XY',seed=900+n)
        # Preserve the exact train/validation evidence sets while perturbing only insertion order.
        cut=max(48,int(len(opaque_permuted)*0.70))
        tr=list(opaque_permuted[:cut]);va=list(opaque_permuted[cut:])
        random.Random(777+n).shuffle(tr);random.Random(1777+n).shuffle(va)
        shuffled=tuple(tr+va)
        a=_discover(base);b=_discover(swapped);c=_discover(shuffled)
        ea=next(x for x in a if x[0]==(0,1));eb=next(x for x in b if x[0]==(0,1));ec=next(x for x in c if x[0]==(0,1))
        assert ea[1:]==eb[1:]==ec[1:],(name,ea,eb,ec)


def test_current_microseed_still_has_no_internal_terrain_owner_after_generalization():
    td=tempfile.TemporaryDirectory(prefix='hardening-sh5-owner-');ms=_new_ms(td)
    try:
        for name in ('developmental_geometry','terrain_topology','relational_visibility_graph','cfe_field','environmental_field_authority'):
            assert not hasattr(ms,name)
    finally:
        ms.biography.close();ms.evidence.conn.close();ms.store.conn.close();td.cleanup()
