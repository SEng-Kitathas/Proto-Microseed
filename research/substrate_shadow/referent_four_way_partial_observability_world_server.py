from __future__ import annotations

import json
import os
import sys

# Four latent evaluator-only sources, two visible channels each when fully exposed.
PHASES = {
    "PRE": {
        "mapping": (0, 0, 1, 1, 2, 2, 3, 3),
        "scales": (1, 1, 1, 1, 1, 1, 1, 1),
        "offsets": (7, 31, 79, 127, 181, 239, 307, 379),
    },
    "CROSS": {
        "mapping": (0, 2, 1, 3, 3, 1, 2, 0),
        "scales": (2, 3, 5, 7, 11, 13, 17, 19),
        "offsets": (401, 503, 607, 709, 811, 919, 1021, 1123),
    },
    "OCCLUDE_AC": {
        "mapping": (1, 3, 1, 3),
        "scales": (23, 29, 31, 37),
        "offsets": (1201, 1301, 1409, 1511),
    },
    "OCCLUDE_BD": {
        "mapping": (0, 2, 2, 0),
        "scales": (41, 43, 47, 53),
        "offsets": (1601, 1709, 1811, 1907),
    },
    "GAP": {"mapping": (), "scales": (), "offsets": ()},
    "POST": {
        "mapping": (3, 1, 0, 2, 2, 0, 1, 3),
        "scales": (59, 61, 67, 71, 73, 79, 83, 89),
        "offsets": (2003, 2111, 2203, 2309, 2411, 2503, 2609, 2707),
    },
}

MARK_OFFSETS = {
    0: (101, 131),
    1: (151, 181),
    2: (211, 241),
    3: (271, 307),
}

ACTIONS = {"FX-A": 0, "FX-B": 1, "FX-C": 2, "FX-D": 3}
MARK_ACTIONS = {"FX-MARK-A": 0, "FX-MARK-B": 1, "FX-MARK-C": 2, "FX-MARK-D": 3}


def _render_one(source: int, local_index: int, state: int, marked: bool, scale: int, offset: int) -> int:
    base = state * state * (source + 5) + state * (source + 17) + 3 * local_index
    mark = MARK_OFFSETS[source][local_index % 2] if marked else 0
    return scale * (base + mark) + offset


def render(phase: str, latent: list[int], marked: list[bool]) -> list[int]:
    cfg = PHASES[phase]
    counts = {0: 0, 1: 0, 2: 0, 3: 0}
    out: list[int] = []
    for i, source in enumerate(cfg["mapping"]):
        local_index = counts[source]
        counts[source] += 1
        out.append(_render_one(source, local_index, latent[source], marked[source], cfg["scales"][i], cfg["offsets"][i]))
    return out


def main() -> None:
    latent = [0, 0, 0, 0]
    marked = [False, False, False, False]
    generations = [0, 0, 0, 0]
    phase = "PRE"
    alias_cd = False

    for raw in sys.stdin:
        try:
            msg = json.loads(raw)
            op = str(msg.get("op", ""))
            if op == "reset":
                latent = [0, 0, 0, 0]
                marked = [False, False, False, False]
                generations = [0, 0, 0, 0]
                phase = "PRE"
                alias_cd = False
                result = {"status": "OK"}
            elif op == "phase":
                new_phase = str(msg.get("phase", ""))
                if new_phase not in PHASES:
                    raise ValueError("BAD_PHASE")
                phase = new_phase
                result = {"status": "OK", "phase": phase}
            elif op == "act":
                aid = str(msg.get("action_id", ""))
                if aid in ACTIONS:
                    source = ACTIONS[aid]
                    if alias_cd and source in (2, 3):
                        latent[2] += 1
                        latent[3] += 1
                    else:
                        latent[source] += 1
                elif aid == "FX-G":
                    for i in range(4):
                        latent[i] += 1
                elif aid in MARK_ACTIONS:
                    marked[MARK_ACTIONS[aid]] = True
                else:
                    raise ValueError("BAD_ACTION")
                result = {"status": "OK", "action_id": aid}
            elif op == "gap":
                phase = "GAP"
                result = {"status": "OK"}
            elif op == "reappear":
                variant = str(msg.get("variant", "PERSIST"))
                phase = "POST"
                alias_cd = False
                if variant == "PERSIST":
                    pass
                elif variant == "REPLACE_C_UNMARKED":
                    generations[2] += 1
                    marked[2] = False
                elif variant == "REPLACE_AC_UNMARKED":
                    for i in (0, 2):
                        generations[i] += 1
                        marked[i] = False
                elif variant == "REPLACE_ALL_PERFECT_COPY":
                    for i in range(4):
                        generations[i] += 1
                elif variant == "ALIAS_CD_POST":
                    alias_cd = True
                else:
                    raise ValueError("BAD_VARIANT")
                result = {"status": "OK", "variant": variant}
            elif op == "observe":
                result = {"status": "OK", "channels": render(phase, latent, marked), "phase": phase, "pid": os.getpid()}
            elif op == "evaluator_state":
                result = {"status": "OK", "phase": phase, "generations": list(generations), "marked": list(marked), "latent": list(latent), "mapping": list(PHASES[phase]["mapping"]), "alias_cd": alias_cd}
            elif op == "close":
                print(json.dumps({"status": "OK"}), flush=True)
                return
            else:
                raise ValueError(f"UNKNOWN_OP:{op}")
            print(json.dumps(result, separators=(",", ":")), flush=True)
        except Exception as exc:
            print(json.dumps({"status": "ERROR", "error": f"{type(exc).__name__}:{exc}"}, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()
