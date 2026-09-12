"""Current organism identity layered over the historical Microseed research lineage.

This module is deliberately small: identity naming does not grant capability,
personality, value, authority, or discontinuity from prior state.
"""

CURRENT_ORGANISM_IDENTITY = "Veya"
HISTORICAL_LINEAGE_NAME = "Microseed"
IDENTITY_MIGRATION_KIND = "CONTINUOUS_IDENTITY_LAYER_MIGRATION"

IDENTITY_LAWS = (
    "VEYA != NEW_ORGANISM",
    "MICROSEED_LINEAGE_CONTINUES_THROUGH_VEYA_IDENTITY",
    "NAME != CAPABILITY",
    "NAME != PERSONALITY",
    "NAME != VALUE_AUTHORITY",
)

def current_identity() -> dict[str, object]:
    return {
        "current_organism_identity": CURRENT_ORGANISM_IDENTITY,
        "historical_lineage_name": HISTORICAL_LINEAGE_NAME,
        "migration_kind": IDENTITY_MIGRATION_KIND,
        "identity_laws": IDENTITY_LAWS,
        "capability_gain": "NONE",
        "personality_authority": "NONE",
        "value_authority": "NONE",
    }
