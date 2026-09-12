from microseed import Microseed, Veya, CURRENT_ORGANISM_IDENTITY, HISTORICAL_LINEAGE_NAME, current_identity


def test_veya_is_compatibility_identity_alias_not_new_runtime_class():
    assert Veya is Microseed
    assert CURRENT_ORGANISM_IDENTITY == "Veya"
    assert HISTORICAL_LINEAGE_NAME == "Microseed"


def test_identity_metadata_preserves_continuity_and_grants_no_authority():
    x=current_identity()
    assert x["current_organism_identity"]=="Veya"
    assert x["historical_lineage_name"]=="Microseed"
    assert x["migration_kind"]=="CONTINUOUS_IDENTITY_LAYER_MIGRATION"
    assert x["capability_gain"]=="NONE"
    assert x["personality_authority"]=="NONE"
    assert x["value_authority"]=="NONE"
    assert "VEYA != NEW_ORGANISM" in x["identity_laws"]
    assert "MICROSEED_LINEAGE_CONTINUES_THROUGH_VEYA_IDENTITY" in x["identity_laws"]
