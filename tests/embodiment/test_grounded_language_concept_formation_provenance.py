from pathlib import Path
import copy
import tempfile

from scratch.ms2046_grounded_operational_token_referent_binding_quarry import _build
from scratch.grounded_language_concept_formation_prototype import (
    grounded_relation_sequence_episode,
    derive_owned_language_mediated_concepts,
    resolve_owned_concept,
    inspect_owned_concept_contents_without_language,
    revalidate_owned_concept_after_grounding_drift,
    predict_second_relation_from_concept,
    attempt_text_only_concept,
    _sha,
)


def _close(td,ms):
    ms.biography.close();ms.evidence.conn.close();ms.store.conn.close();td.cleanup()


def _dataset(ms,world,tokens=("steady","switch"),start=1000):
    stable,changing=tokens
    train=[];hold=[]
    # Both referents occupy both roles over the dataset; token groups a transform, not an object identity.
    specs=[]
    for i in range(6): specs.append((stable,"PQ" if i%2==0 else "QP","PQ" if i%2==0 else "QP"))
    for i in range(6): specs.append((changing,"PQ" if i%2==0 else "QP","QP" if i%2==0 else "PQ"))
    for i,(tok,a,b) in enumerate(specs): train.append(grounded_relation_sequence_episode(ms,world,surface_token=tok,first_mode=a,second_mode=b,index=start+i))
    hs=[]
    for i in range(3): hs.append((stable,"QP" if i%2==0 else "PQ","QP" if i%2==0 else "PQ"))
    for i in range(3): hs.append((changing,"QP" if i%2==0 else "PQ","PQ" if i%2==0 else "QP"))
    for i,(tok,a,b) in enumerate(hs): hold.append(grounded_relation_sequence_episode(ms,world,surface_token=tok,first_mode=a,second_mode=b,index=start+100+i))
    return train,hold


def _concept_map(cset):
    return {c["surface_token"]:c["concept_content_digest_sha256"] for c in cset["concepts"]}


def _content_map(cset):
    return {tuple(c["grounded_concept_content"]["relation_transform_permutation"]):c["concept_content_digest_sha256"] for c in cset["concepts"]}


def test_p03_language_grouping_forms_owned_grounded_concepts_and_predicts_heldout_relations():
    td=tempfile.TemporaryDirectory(prefix="veya-p03-concept-");ms,world=_build(Path(td.name))
    try:
        train,hold=_dataset(ms,world)
        cset=derive_owned_language_mediated_concepts(ms,train,hold)
        assert cset["status"]=="OWNED_GROUNDED_LANGUAGE_MEDIATED_CONCEPT_SET_RESEARCH_ONLY",cset
        assert len(cset["concepts"])==2
        stored=ms.evidence.get(cset["concept_evidence_id"])
        assert stored is not None and stored["sha256"]==cset["concept_evidence_sha256"]
        for row in hold:
            concept=resolve_owned_concept(ms,cset,row["payload"]["surface_token"])
            pred=predict_second_relation_from_concept(concept,row["first_episode"])
            assert pred["status"]=="OWNED_LANGUAGE_CONCEPT_CAUSAL_PREDICTION_RESEARCH_ONLY",pred
            assert pred["predicted_second_relation_order"]==row["payload"]["second_relation_order"]
            assert pred["external_oracle_authority"]==pred["language_authority"]=="NONE"
    finally:_close(td,ms)


def test_p03_surface_token_remapping_changes_lexical_binding_not_grounded_concept_content():
    td1=tempfile.TemporaryDirectory(prefix="veya-p03-map1-");m1,w1=_build(Path(td1.name))
    td2=tempfile.TemporaryDirectory(prefix="veya-p03-map2-");m2,w2=_build(Path(td2.name))
    try:
        tr1,h1=_dataset(m1,w1,("steady","switch"),2000);c1=derive_owned_language_mediated_concepts(m1,tr1,h1)
        tr2,h2=_dataset(m2,w2,("switch","steady"),3000);c2=derive_owned_language_mediated_concepts(m2,tr2,h2)
        assert c1["status"]==c2["status"]=="OWNED_GROUNDED_LANGUAGE_MEDIATED_CONCEPT_SET_RESEARCH_ONLY"
        # Grounded concept contents are identical although which word indexes which concept swaps.
        assert _content_map(c1)==_content_map(c2)
        assert _concept_map(c1)["steady"]!=_concept_map(c2)["steady"]
    finally:_close(td1,m1);_close(td2,m2)


def test_p03_text_or_personality_slogan_without_grounded_acquisition_cannot_create_concept():
    for text in ("everything called steady shares a deep essence","Veya is kind, therefore kind is a concept","the operator says switch means change"):
        out=attempt_text_only_concept(text)
        assert out["status"]=="DEFER_UNKNOWN"
        assert out["reason"]=="GROUNDED_LANGUAGE_GROUPED_ACQUISITION_HISTORY_REQUIRED"
        assert out["external_oracle_authority"]=="NONE"


def test_p03_inconsistent_language_grouping_fails_ambiguity_instead_of_forcing_a_concept():
    td=tempfile.TemporaryDirectory(prefix="veya-p03-ambig-");ms,world=_build(Path(td.name))
    try:
        train,hold=_dataset(ms,world,start=4000)
        # Corrupt one learned association so the same token spans two grounded transforms.
        bad=copy.deepcopy(train)
        bad[0]["payload"]["surface_token"]="switch"
        bad[0]["sequence_sha256"]=_sha(bad[0]["payload"])
        out=derive_owned_language_mediated_concepts(ms,bad,hold,evidence_id="E-P03-AMBIG")
        assert out["status"]=="DEFER_UNKNOWN",out
        assert "TOKEN_CONCEPT_ASSOCIATION_NOT_FUNCTIONAL" in out["reason"] or "ASSOCIATION" in out["reason"]
    finally:_close(td,ms)


def test_p03_owned_state_is_required_and_forged_or_unowned_concept_set_is_refused():
    td=tempfile.TemporaryDirectory(prefix="veya-p03-owned-");ms,world=_build(Path(td.name))
    try:
        train,hold=_dataset(ms,world,start=5000);c=derive_owned_language_mediated_concepts(ms,train,hold)
        forged=dict(c);forged["concept_evidence_sha256"]="0"*64
        out=resolve_owned_concept(ms,forged,"steady")
        assert out["status"]=="DEFER_UNKNOWN" and out["reason"]=="EXACT_OWNED_CONCEPT_EVIDENCE_REQUIRED"
    finally:_close(td,ms)


def test_p03_language_disabled_ablation_can_remove_lexical_retrieval_while_owned_concept_content_remains():
    td=tempfile.TemporaryDirectory(prefix="veya-p03-ablate-");ms,world=_build(Path(td.name))
    try:
        train,hold=_dataset(ms,world,start=6000);c=derive_owned_language_mediated_concepts(ms,train,hold)
        lexical=resolve_owned_concept(ms,c,"steady")
        no_language=inspect_owned_concept_contents_without_language(ms,c)
        assert lexical["status"]=="OWNED_LANGUAGE_CONCEPT_RESOLVED_RESEARCH_ONLY"
        assert no_language["status"]=="OWNED_CONCEPT_CONTENTS_AVAILABLE_WITHOUT_LANGUAGE_INDEX"
        assert no_language["lexical_retrieval_available"] is False
        digests={x["concept_content_digest_sha256"] for x in no_language["concept_contents"]}
        assert lexical["concept_content_digest_sha256"] in digests
    finally:_close(td,ms)


def test_p03_grounding_drift_blocks_new_grounded_concept_use_without_erasing_owned_history():
    td=tempfile.TemporaryDirectory(prefix="veya-p03-stale-");ms,world=_build(Path(td.name))
    try:
        train,hold=_dataset(ms,world,start=7000);c=derive_owned_language_mediated_concepts(ms,train,hold)
        before=inspect_owned_concept_contents_without_language(ms,c)
        ms.change_capability_dependency("SIG-X",reason="P03-GROUNDING-DRIFT")
        stale_resolve=resolve_owned_concept(ms,c,"steady")
        assert stale_resolve["status"]=="DEFER_UNKNOWN"
        assert stale_resolve["reason"]=="CONCEPT_GROUNDING_DEPENDENCY_DRIFT_REVALIDATION_REQUIRED"
        # Fresh grounding may legitimately recover after dependency change; concept use must revalidate against it.
        fresh=grounded_relation_sequence_episode(ms,world,surface_token="steady",first_mode="PQ",second_mode="PQ",index=7999)
        assert fresh["status"]=="CURRENT_GROUNDED_LANGUAGE_RELATION_SEQUENCE_EPISODE",fresh
        revalidated=revalidate_owned_concept_after_grounding_drift(ms,c,"steady",fresh)
        assert revalidated["status"]=="CURRENT_OWNED_LANGUAGE_CONCEPT_REVALIDATED_RESEARCH_ONLY",revalidated
        pred=predict_second_relation_from_concept(revalidated,fresh["first_episode"])
        assert pred["predicted_second_relation_order"]==fresh["payload"]["second_relation_order"]
        after=inspect_owned_concept_contents_without_language(ms,c)
        assert before["status"]==after["status"]=="OWNED_CONCEPT_CONTENTS_AVAILABLE_WITHOUT_LANGUAGE_INDEX"
    finally:_close(td,ms)


def test_p03_archetype_hostiles_wording_identity_and_scaffold_labels_have_no_concept_authority():
    # ADE-H02: moral/personality slogan is not concept evidence.
    assert attempt_text_only_concept("good agents are always helpful")["status"]=="DEFER_UNKNOWN"
    # ADE-H03: repeated identity/personality text does not install a concept.
    assert attempt_text_only_concept("Veya is Veya is curious is curious")["status"]=="DEFER_UNKNOWN"
    # ADE-H08: surface remapping is handled by the learned binding test above, not curator vocabulary.
