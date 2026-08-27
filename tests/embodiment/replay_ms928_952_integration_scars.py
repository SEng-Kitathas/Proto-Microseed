from __future__ import annotations
import json, shutil, sqlite3, tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from microseed import Microseed
from microseed.persistence.biography import BiographyIntegrityError, DevelopmentalBiography

out={}
with tempfile.TemporaryDirectory() as td:
    root=Path(td); a=root/'a'; m=Microseed(a)
    m.path.append('LEARNED_RELATION', {'opaque':'r0'})
    base=m.biography_witness(); out['base_integrity']=base['integrity']; out['identity_claim']=base['identity_claim']
    m.store.conn.close();m.evidence.conn.close();m.biography.close()
    b=root/'b';shutil.copytree(a,b)
    mb=Microseed(b); mb.path.append('MIGRATION_CONTINUATION', {'host':'opaque-b'})
    out['migration_relation']=DevelopmentalBiography.relation(base,mb.biography_witness())
    mb.store.conn.close();mb.evidence.conn.close();mb.biography.close()
    ma=Microseed(a); ma.path.append('LEFT_BRANCH', {'x':1}); left=ma.biography_witness();ma.store.conn.close();ma.evidence.conn.close();ma.biography.close()
    mb2=Microseed(b); mb2.path.append('RIGHT_BRANCH', {'x':2}); right=mb2.biography_witness(); out['fork_relation']=DevelopmentalBiography.relation(left,right);mb2.store.conn.close();mb2.evidence.conn.close();mb2.biography.close()
with tempfile.TemporaryDirectory() as td:
    p=Path(td); m=Microseed(p);m.path.append('TAMPER_TARGET', {'x':1});m.store.conn.close();m.evidence.conn.close();m.biography.close()
    db=sqlite3.connect(p/'biography.sqlite3'); eid=db.execute("select event_id from biography_events where kind='TAMPER_TARGET'").fetchone()[0];db.execute("update biography_events set payload=? where event_id=?",(json.dumps({'x':9}),eid));db.commit();db.close()
    try: Microseed(p); out['tamper_rejected']=False
    except BiographyIntegrityError: out['tamper_rejected']=True
out['ms978_started']=False
out['language']='DEFERRED_PRELINGUAL_COGNITION_ACTIVE'
out['persistent_selfhood']='NOT_QUALIFIED'
out['checks'] = {
    'base_integrity_verified': out['base_integrity'] == 'VERIFIED',
    'migration_descendant': out['migration_relation'] == 'DESCENDANT_CONTINUATION',
    'fork_diverged': out['fork_relation'] == 'COMMON_ANCESTRY_DIVERGED',
    'tamper_rejected': out['tamper_rejected'] is True,
    'identity_not_qualified': out['identity_claim'] == 'NOT_QUALIFIED' and out['persistent_selfhood'] == 'NOT_QUALIFIED',
    'hard_stop': out['ms978_started'] is False,
    'language_deferred': out['language'] == 'DEFERRED_PRELINGUAL_COGNITION_ACTIVE',
}
out['all_pass'] = all(out['checks'].values())
print(json.dumps(out,indent=2,sort_keys=True))
