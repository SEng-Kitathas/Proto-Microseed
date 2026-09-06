from __future__ import annotations

import json
import tempfile
from pathlib import Path

from scratch.lang_c02_multi_token_restart_revalidation import build_two_relations
from scratch.lang_c06_grounded_directional_relation import external_direction_episode


def _evidence_rows(ms):
    count = ms.evidence.count()
    return count, (ms.evidence.recent(count) if count else [])


def run_boundary() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="lang-c08b-owned-relation-boundary-") as td:
        ms, world, rx, ry = build_two_relations(Path(td))
        try:
            before_count, before_rows = _evidence_rows(ms)
            episode = external_direction_episode(ms, world, "A", 900, "PQ")
            after_count, after_rows = _evidence_rows(ms)

            native_relation_rows = []
            for row in after_rows:
                payload = row.get("payload") or {}
                kind = str(payload.get("kind", ""))
                if (
                    kind in {"BOUNDED_RAW_OBSERVATION_COORDINATES", "OPERATIONAL_REFERENT_SIGNATURE_WITNESS"}
                    or "RELATION" in kind
                ):
                    native_relation_rows.append(
                        {
                            "evidence_id": str(row.get("evidence_id", "")),
                            "kind": kind,
                            "sha256": str(row.get("sha256", "")),
                        }
                    )

            b1_keys = {
                "SIG-X": sorted((rx.get("relation") or {}).keys()),
                "SIG-Y": sorted((ry.get("relation") or {}).keys()),
            }
            required_native_ancestry = {
                "raw_evidence_refs",
                "action_response_rows",
                "source_evidence_refs",
            }
            present = set(b1_keys["SIG-X"]) | set(b1_keys["SIG-Y"])
            missing = sorted(required_native_ancestry - present)

            later_native_surfaces = {
                "bounded_raw_observation_owner": hasattr(ms, "record_bounded_raw_observation_coordinates"),
                "owned_probe_prefix": hasattr(ms, "derive_current_owned_opaque_probe_prefix"),
                "raw_trace_referent_derivation": hasattr(ms, "derive_operational_referent_signatures_from_raw_trace"),
                "referent_signature_witness_owner": hasattr(ms, "record_operational_referent_signature"),
                "owned_observable_contrast": hasattr(ms, "_current_owned_referent_program_observable_contrast"),
            }

            assert episode.get("status") == "CURRENT_GROUNDED_EXTERNAL_DIRECTIONAL_EVENT_EPISODE", episode
            assert before_count == 0, before_rows
            assert after_count == 0, after_rows
            assert not native_relation_rows, native_relation_rows
            assert missing == sorted(required_native_ancestry), (present, missing)
            assert all(later_native_surfaces.values()), later_native_surfaces

            return {
                "status": "STOP_C08B_EXISTING_LANGUAGE_LINEAGE_HAS_NO_ORGANISM_OWNED_C06_RELATION_EVIDENCE",
                "evidence_count_before_c06_episode": before_count,
                "evidence_count_after_c06_episode": after_count,
                "evidence_delta": after_count - before_count,
                "native_relation_evidence_rows": native_relation_rows,
                "c06_episode_status": episode["status"],
                "c06_episode_payload_location": "HARNESS_LOCAL_RETURN_VALUE",
                "c06_episode_sha256_present": bool(episode.get("episode_sha256")),
                "b1_relation_keys": b1_keys,
                "missing_native_b1_ancestry_fields": missing,
                "later_native_surfaces_already_present": later_native_surfaces,
                "missing_owner": "C01_C06_LANGUAGE_LINEAGE_BRIDGE_TO_EXISTING_OWNED_RAW_ACTION_REFERENT_EVIDENCE",
                "next": "RE_EMBODY_B1_C06_CURRENTNESS_ON_EXISTING_NATIVE_RAW_ACTION_EVIDENCE_BEFORE_FURTHER_LANGUAGE_CURRENTNESS",
                "truth_authority": "NONE",
                "semantic_authority": "NONE",
                "execution_authority": "NONE",
                "language_authority": "NONE",
            }
        finally:
            ms.biography.close()
            ms.evidence.conn.close()
            ms.store.conn.close()


if __name__ == "__main__":
    print(json.dumps(run_boundary(), indent=2, sort_keys=True))
