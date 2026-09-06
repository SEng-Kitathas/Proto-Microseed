from __future__ import annotations

from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "developmental_positive_path_mutants"
if REPORT.exists():
    shutil.rmtree(REPORT)
REPORT.mkdir(parents=True, exist_ok=True)

# These mutants intentionally disable already-earned positive paths.  They are the
# mirror image of the historical guard-loosening source mutants: a surviving
# mutant means the selected regression surface can become more abstention-prone
# without noticing the loss of an earned behavior.
MUTANTS = {
    "SUPPRESS_EARNED_BOUNDED_ACTION_YES": {
        "target": "microseed/runtime/entity.py",
        "test": "tests/embodiment/test_ms1402_integration.py",
        "old": "        elif residual < current:\n            stance=TernaryCommitment.YES; reason=\"BOUNDED_REHEARSAL_PREDICTS_LOWER_REGULATORY_PRESSURE\"\n",
        "new": "        elif False and residual < current:\n            stance=TernaryCommitment.YES; reason=\"BOUNDED_REHEARSAL_PREDICTS_LOWER_REGULATORY_PRESSURE\"\n",
        "loss_class": "LAWFUL_ACTION_COMMITMENT_SUPPRESSED",
    },
    "SUPPRESS_EARNED_ENDOGENOUS_EPISTEMIC_INTENT": {
        "target": "microseed/runtime/entity.py",
        "test": "tests/embodiment/test_ms1710_endogenous_epistemic_initiation.py",
        "old": "        return {\"status\":\"ACTION_INTENT_NOMINATED\",\"intent\":packet,\"priority\":priority.serializable(),\"information\":information.serializable(),\"commitment\":cmt.serializable(),\"feasibility_basis\":feasibility_basis,\"execution_authority\":\"NONE\",\"research_basis\":\"ENDOGENOUS_EPISTEMIC_PROGRAM_STEP\"}\n",
        "new": "        return {\"status\":\"ABSTAIN\",\"reason\":\"MUTANT_SUPPRESSED_EARNED_ENDOGENOUS_INTENT\",\"priority\":priority.serializable(),\"information\":information.serializable(),\"commitment\":cmt.serializable(),\"feasibility_basis\":feasibility_basis,\"execution_authority\":\"NONE\",\"research_basis\":\"ENDOGENOUS_EPISTEMIC_PROGRAM_STEP\"}\n",
        "loss_class": "ENDOGENOUS_EXPERIMENT_INITIATION_SUPPRESSED",
    },
    "SUPPRESS_OWNED_THREE_LOCUS_PROGRAM_GENERATION": {
        "target": "microseed/runtime/entity.py",
        "test": "tests/embodiment/test_ms1820_pass13_owned_three_locus_surface_generates_program.py",
        "old": "        decision_context = EpistemicDecisionBearingContext(tuple(surface[\"relation_sets\"]), ())\n        result = dict(derive_current_generated_epistemic_program_candidates(\n            decision_context=decision_context,\n            start_state_id=self.action_closure.current_state.state_id,\n            capabilities=self.capabilities,\n            obligation=obligation,\n            max_nodes=max_nodes,\n        ))\n",
        "new": "        decision_context = EpistemicDecisionBearingContext(tuple(surface[\"relation_sets\"]), ())\n        result = {\"status\": \"ABSTAIN\", \"reason\": \"MUTANT_SUPPRESSED_OWNED_PROGRAM_GENERATION\", \"candidates\": ()}\n",
        "loss_class": "GROUNDED_PROGRAM_GENERATION_SUPPRESSED",
    },
    "SUPPRESS_C08A_FRESH_REVALIDATION_TO_CURRENT": {
        "target": "microseed/development/evidence_relation.py",
        "test": "tests/embodiment/test_lang_c08_native_evidence_association_currentness.py",
        "old": "        if record.state == OpaqueEvidenceAssociationState.REVALIDATION_REQUIRED:\n            record.state = OpaqueEvidenceAssociationState.CURRENT\n",
        "new": "        if record.state == OpaqueEvidenceAssociationState.REVALIDATION_REQUIRED:\n            record.state = OpaqueEvidenceAssociationState.REVALIDATION_REQUIRED\n",
        "loss_class": "FRESH_CURRENTNESS_REVALIDATION_SUPPRESSED",
    },
    "SUPPRESS_C08C_OWNED_DIRECTIONAL_RELATION_DERIVATION": {
        "target": "microseed/runtime/entity.py",
        "test": "tests/embodiment/test_lang_c08c_native_owned_affordance_relation.py",
        "old": "        passive=self.derive_current_owned_passive_raw_transition(max_events=max_events)\n        if passive.get(\"status\")!=\"CURRENT_OWNED_PASSIVE_RAW_TRANSITION\":\n",
        "new": "        return {**base,\"status\":\"DEFER_UNKNOWN\",\"reason\":\"MUTANT_SUPPRESSED_OWNED_DIRECTIONAL_RELATION_DERIVATION\"}\n        passive=self.derive_current_owned_passive_raw_transition(max_events=max_events)\n        if passive.get(\"status\")!=\"CURRENT_OWNED_PASSIVE_RAW_TRANSITION\":\n",
        "loss_class": "OWNED_DIRECTIONAL_RELATION_GENERATION_SUPPRESSED",
    },
    "SUPPRESS_C08D_CURRENT_RUNTIME_FRESHNESS_PATH": {
        "target": "microseed/runtime/entity.py",
        "test": "tests/embodiment/test_lang_c08d_postrestart_native_relation_rederivation.py",
        "old": "        return max(boots) if boots else -1\n",
        "new": "        return (max(boots) + 1000000000000) if boots else -1\n",
        "loss_class": "POST_RESTART_FRESH_EVIDENCE_REDERIVATION_SUPPRESSED",
    },
    "SUPPRESS_C08E_NATIVE_TOKEN_RELATION_RESOLUTION": {
        "target": "scratch/lang_c08e_native_token_relation_binding.py",
        "test": "tests/embodiment/test_lang_c08e_native_token_relation_binding.py",
        "old": "        \"status\": \"OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_RELATION\",\n",
        "new": "        \"status\": \"DEFER_UNKNOWN\",\n",
        "loss_class": "NATIVE_OPAQUE_TOKEN_RELATION_RESOLUTION_SUPPRESSED",
    },
    "SUPPRESS_C08F_NATIVE_TOKEN_REFERENT_RESOLUTION": {
        "target": "scratch/lang_c08f_native_token_referent_binding.py",
        "test": "tests/embodiment/test_lang_c08f_native_token_referent_binding.py",
        "old": "    return {**NONE, \"status\": \"OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_OPERATIONAL_REFERENT\", \"opaque_token\": str(opaque_token), ",
        "new": "    return {**NONE, \"status\": \"DEFER_UNKNOWN\", \"opaque_token\": str(opaque_token), ",
        "loss_class": "NATIVE_OPAQUE_TOKEN_REFERENT_RESOLUTION_SUPPRESSED",
    },
    "SUPPRESS_C08G_NATIVE_B2_ORDERED_COMPOSITION": {
        "target": "scratch/lang_c08g_native_b2_ordered_composition.py",
        "test": "tests/embodiment/test_lang_c08g_native_b2_ordered_composition.py",
        "old": "        \"status\": \"CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED\",\n",
        "new": "        \"status\": \"DEFER_UNKNOWN\",\n",
        "loss_class": "NATIVE_B2_ORDERED_COMPOSITION_SUPPRESSED",
    },
}


def ignore(_path: str, names: list[str]) -> set[str]:
    return {name for name in names if name in {".git", "reports", ".pytest_cache", "__pycache__", ".pcmmad_sync_runs"}}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def apply_mutation(root: Path, name: str, spec: dict[str, str]) -> tuple[str, str]:
    path = root / spec["target"]
    raw = path.read_text(encoding="utf-8")
    old = spec["old"]
    if raw.count(old) != 1:
        raise RuntimeError(f"MUTATION_PATTERN_COUNT:{name}:{raw.count(old)}")
    mutated = raw.replace(old, spec["new"], 1)
    path.write_text(mutated, encoding="utf-8")
    return sha_text(raw), sha_text(mutated)


def run_one(name: str, spec: dict[str, str]) -> dict[str, object]:
    started = time.time()
    with tempfile.TemporaryDirectory(prefix=f"positive_path_{name}_") as td:
        dst = Path(td) / "repo"
        shutil.copytree(ROOT, dst, ignore=ignore)
        clean_sha, mutant_sha = apply_mutation(dst, name, spec)
        cmd = [sys.executable, "tools/run_pytest_cleanup_neutral.py", "-q", spec["test"]]
        try:
            proc = subprocess.run(cmd, cwd=dst, capture_output=True, text=True, timeout=90)
            code = proc.returncode
            out = proc.stdout
            err = proc.stderr
            completion = "COMPLETE"
            # For a loss-of-function mutant, nonzero means the existing test killed it.
            status = "KILLED" if code != 0 else "SURVIVED_UNDER_ACTION_BLIND_SPOT"
        except subprocess.TimeoutExpired as exc:
            code = None
            out = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            completion = "INCOMPLETE"
            status = "UNKNOWN_INCOMPLETE_TIMEOUT"
        stdout_path = REPORT / f"{name}.stdout.log"
        stderr_path = REPORT / f"{name}.stderr.log"
        stdout_path.write_text(out, encoding="utf-8")
        stderr_path.write_text(err, encoding="utf-8")
        return {
            "mutant": name,
            "loss_class": spec["loss_class"],
            "target": spec["target"],
            "test": spec["test"],
            "status": status,
            "exit_code": code,
            "completion_marker": completion,
            "duration_seconds": round(time.time() - started, 6),
            "clean_source_sha256": clean_sha,
            "mutant_source_sha256": mutant_sha,
            "stdout_path": str(stdout_path.relative_to(ROOT)),
            "stderr_path": str(stderr_path.relative_to(ROOT)),
            "stdout_tail": "\n".join(out.splitlines()[-20:]),
            "stderr_tail": "\n".join(err.splitlines()[-12:]),
        }


def main() -> int:
    started = time.time()
    results = [run_one(name, spec) for name, spec in MUTANTS.items()]
    killed = [r["mutant"] for r in results if r["status"] == "KILLED"]
    survived = [r["mutant"] for r in results if str(r["status"]).startswith("SURVIVED")]
    unknown = [r["mutant"] for r in results if str(r["status"]).startswith("UNKNOWN")]
    receipt = {
        "schema": "microseed.developmental-positive-path-mutants.v1",
        "purpose": "MEASURE_UNDER_ACTION_BLIND_SPOT_ON_ALREADY_EARNED_POSITIVE_PATHS",
        "interpretation_law": "CORRECT_ABSTENTION != DEMONSTRATED_COMPETENCE",
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": results,
        "killed": killed,
        "survived_under_action_blind_spot": survived,
        "unknown": unknown,
        "completion_marker": "COMPLETE" if all(r["completion_marker"] == "COMPLETE" for r in results) else "INCOMPLETE",
        "scientific_authority": "DIAGNOSTIC_ONLY",
        "capability_authority": "NONE",
        "semantic_authority": "NONE",
    }
    receipt_path = REPORT / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps({
        "receipt": str(receipt_path.relative_to(ROOT)),
        "killed": killed,
        "survived_under_action_blind_spot": survived,
        "unknown": unknown,
        "completion_marker": receipt["completion_marker"],
    }, indent=2))
    return 0 if receipt["completion_marker"] == "COMPLETE" and not unknown else 2


if __name__ == "__main__":
    raise SystemExit(main())
