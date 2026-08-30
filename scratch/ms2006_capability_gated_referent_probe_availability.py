from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from microseed.runtime.types import Authority, CapabilityContract, QualificationState, QueryObligation
from scratch.ms2005_bounded_referent_probe_reconstruction import (
    ACTIONS, UNIQUE_A, UNIQUE_B, _persist_context, _close,
    derive_informative_probe_candidates,
)


def derive_current_referent_probe_capability_availability(
    ms: Microseed, probe_result: dict[str,Any], obligation: QueryObligation,
) -> dict[str,Any]:
    base={
        "information_status":str(probe_result.get("status","UNKNOWN_INCOMPLETE")),
        "availability_authority":"NONE","selection_authority":"NONE",
        "execution_authority":"NONE","truth_authority":"NONE",
        "identity_authority":"NONE","semantic_reference_authority":"NONE",
    }
    if probe_result.get("status")!="CURRENT_UNIQUE_INFORMATIVE_REFERENT_PROBE":
        return {**base,"status":"REFERENT_PROBE_NOT_UNIQUELY_AVAILABLE","reason":"INFORMATIVE_PROBE_NOT_UNIQUE"}
    cid=str(probe_result.get("probe_action_id",""))
    if not cid:
        return {**base,"status":"REFERENT_PROBE_NOT_AVAILABLE","reason":"OPAQUE_PROBE_ACTION_ID_REQUIRED"}
    cap=ms.capabilities.contracts.get(cid)
    if cap is None:
        return {**base,"status":"REFERENT_PROBE_NOT_AVAILABLE","reason":"INFORMATIVE_PROBE_CAPABILITY_NOT_FOUND","probe_action_id":cid}
    if cap.authority!=Authority.EFFECT:
        return {**base,"status":"REFERENT_PROBE_NOT_AVAILABLE","reason":"INFORMATIVE_PROBE_CAPABILITY_NOT_EFFECT","probe_action_id":cid}
    closure=ms.capabilities.assess_dependency_closure(cid)
    if closure.get("status")!="CURRENT_DEPENDENCY_CLOSURE":
        return {**base,"status":"REFERENT_PROBE_NOT_AVAILABLE","reason":"INFORMATIVE_PROBE_CAPABILITY_NOT_CURRENT","probe_action_id":cid,"dependency_closure":closure}
    if cap.query_obligation_id and cap.query_obligation_id!=obligation.obligation_id:
        return {**base,"status":"REFERENT_PROBE_NOT_AVAILABLE","reason":"INFORMATIVE_PROBE_QUERY_OBLIGATION_MISMATCH","probe_action_id":cid}
    if cap.operational_scope_id and cap.operational_scope_id!=obligation.operational_scope_id:
        return {**base,"status":"REFERENT_PROBE_NOT_AVAILABLE","reason":"INFORMATIVE_PROBE_OPERATIONAL_SCOPE_MISMATCH","probe_action_id":cid}
    if cap.handler is None:
        return {**base,"status":"REFERENT_PROBE_NOT_AVAILABLE","reason":"INFORMATIVE_PROBE_HANDLER_MISSING","probe_action_id":cid}
    return {
        **base,"status":"CURRENT_UNIQUE_INFORMATIVE_REFERENT_PROBE_CAPABILITY_AVAILABLE",
        "probe_action_id":cid,"capability_id":cid,
        "capability_epoch":int(ms.capabilities.epochs[cid]),
        "capability_signature_sha256":cap.computed_signature_sha256(),
        "operational_scope_id":cap.operational_scope_id,
        "query_obligation_id":cap.query_obligation_id,
        "dependency_closure":closure,
        "invoked":"NO",
    }


def _information_fixture(ms: Microseed) -> dict[str,Any]:
    ca=_persist_context(ms,"MS2006-A",UNIQUE_A); cb=_persist_context(ms,"MS2006-B",UNIQUE_B)
    return derive_informative_probe_candidates(ms,(str(ca["projection_bucket_id"]),str(cb["projection_bucket_id"])),ACTIONS,max_records=128)


def _cap(cid:str, *, authority:Authority=Authority.EFFECT, scope:str|None="REF-SCOPE", handler=True) -> CapabilityContract:
    return CapabilityContract(
        cid,"opaque referent probe",{}, {},(),(),authority,("MS2006",),"CURRENT",{},
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=(lambda: {"opaque_probe_receipt":cid}) if handler else None,
        operational_scope_id=scope,
    )


def run_ms2006() -> dict[str,Any]:
    obligation=QueryObligation("Q-REF-PROBE","opaque referent information probe",Authority.NONE,operational_scope_id="REF-SCOPE")
    cases={}

    # No capability: information does not create availability.
    td=tempfile.TemporaryDirectory(prefix="ms2006-none-"); ms=Microseed(Path(td.name))
    try:
        info=_information_fixture(ms); assert info["probe_action_id"]=="P2",info
        cases["no_capability"]=derive_current_referent_probe_capability_availability(ms,info,obligation)
        assert cases["no_capability"]["reason"]=="INFORMATIVE_PROBE_CAPABILITY_NOT_FOUND"
    finally: _close(ms); td.cleanup()

    # Wrong authority.
    td=tempfile.TemporaryDirectory(prefix="ms2006-auth-"); ms=Microseed(Path(td.name))
    try:
        info=_information_fixture(ms); ms.register_capability(_cap("P2",authority=Authority.REFERENCE_ONLY))
        cases["wrong_authority"]=derive_current_referent_probe_capability_availability(ms,info,obligation)
        assert cases["wrong_authority"]["reason"]=="INFORMATIVE_PROBE_CAPABILITY_NOT_EFFECT"
    finally: _close(ms); td.cleanup()

    # Wrong scope.
    td=tempfile.TemporaryDirectory(prefix="ms2006-scope-"); ms=Microseed(Path(td.name))
    try:
        info=_information_fixture(ms); ms.register_capability(_cap("P2",scope="OTHER-SCOPE"))
        cases["wrong_scope"]=derive_current_referent_probe_capability_availability(ms,info,obligation)
        assert cases["wrong_scope"]["reason"]=="INFORMATIVE_PROBE_OPERATIONAL_SCOPE_MISMATCH"
    finally: _close(ms); td.cleanup()

    # Exact current capability becomes inertly available, then dependency drift removes availability.
    td=tempfile.TemporaryDirectory(prefix="ms2006-current-"); ms=Microseed(Path(td.name))
    try:
        info=_information_fixture(ms)
        ms.register_capability(_cap("P2"))
        # Similar unrelated capability cannot replace exact opaque action handle.
        ms.register_capability(_cap("P2-ALT"))
        before_calls=[]
        ms.capabilities.contracts["P2"].handler=lambda: before_calls.append("P2") or {"ok":True}
        current=derive_current_referent_probe_capability_availability(ms,info,obligation)
        assert current["status"]=="CURRENT_UNIQUE_INFORMATIVE_REFERENT_PROBE_CAPABILITY_AVAILABLE",current
        assert current["capability_id"]=="P2" and current["capability_epoch"]==0
        assert current["invoked"]=="NO" and before_calls==[]
        stale=ms.change_capability_dependency("P2",reason="MS2006_HOSTILE_PROBE_DRIFT")
        assert "P2" in stale
        after=derive_current_referent_probe_capability_availability(ms,info,obligation)
        assert after["reason"]=="INFORMATIVE_PROBE_CAPABILITY_NOT_CURRENT",after
        assert ms.capabilities.epochs["P2"]==1
        cases["current_available"]=current; cases["after_drift"]=after
        cases["unrelated_alias_present"]="P2-ALT"
        cases["handler_calls_during_availability"]=list(before_calls)
    finally: _close(ms); td.cleanup()

    return {
        "status":"PASS","cases":cases,
        "unique_probe_action_id":"P2",
        "availability_requires_exact_current_effect_capability":"YES",
        "availability_invokes_capability":"NO",
        "selection_authority":"NONE","execution_authority":"NONE","truth_authority":"NONE",
        "new_referent_executor_required":"NO","new_capability_registry_required":"NO",
    }


def main()->None:
    print(json.dumps(run_ms2006(),indent=2,sort_keys=True))

if __name__=="__main__": main()
