from __future__ import annotations

import json
import os
import sys

PHASES = {
    "PRE": {
        "mapping": (0, 0, 1, 1),
        "visible": (0, 1, 2, 3),
        "scales": (1, 1, 1, 1),
        "offsets": (7, 31, 79, 127),
    },
    "CROSS": {
        "mapping": (0, 1, 1, 0),
        "visible": (0, 1, 2, 3),
        "scales": (2, 3, 5, 7),
        "offsets": (211, 307, 401, 503),
    },
    "OCCLUDE_A": {
        "mapping": (1, 1),
        "visible": (0, 1),
        "scales": (11, 13),
        "offsets": (601, 709),
    },
    "GAP": {
        "mapping": (),
        "visible": (),
        "scales": (),
        "offsets": (),
    },
    "POST": {
        "mapping": (1, 1, 0, 0),
        "visible": (0, 1, 2, 3),
        "scales": (17, 19, 23, 29),
        "offsets": (809, 907, 1009, 1103),
    },
}

MARK_OFFSETS = {
    0: (131, 173),
    1: (197, 239),
}


def _render_one(source: int, local_index: int, state: int, marked: bool, scale: int, offset: int) -> int:
    base = state * state * (source + 5) + state * (source + 17) + 3 * local_index
    mark = MARK_OFFSETS[source][local_index % 2] if marked else 0
    return scale * (base + mark) + offset


def render(phase: str, latent: list[int], marked: list[bool]) -> list[int]:
    cfg = PHASES[phase]
    counts = {0: 0, 1: 0}
    out: list[int] = []
    for i, source in enumerate(cfg["mapping"]):
        local_index = counts[source]
        counts[source] += 1
        out.append(
            _render_one(
                source,
                local_index,
                latent[source],
                marked[source],
                cfg["scales"][i],
                cfg["offsets"][i],
            )
        )
    return out


def main() -> None:
    latent = [0, 0]
    marked = [False, False]
    generations = [0, 0]
    phase = "PRE"
    alias_actions = False

    for raw in sys.stdin:
        try:
            msg = json.loads(raw)
            op = str(msg.get("op", ""))
            if op == "reset":
                latent = [0, 0]
                marked = [False, False]
                generations = [0, 0]
                phase = "PRE"
                alias_actions = False
                result = {"status": "OK"}
            elif op == "phase":
                new_phase = str(msg.get("phase", ""))
                if new_phase not in PHASES:
                    raise ValueError("BAD_PHASE")
                phase = new_phase
                result = {"status": "OK", "phase": phase}
            elif op == "act":
                aid = str(msg.get("action_id", ""))
                if aid == "FX-A":
                    if alias_actions:
                        latent[0] += 1
                        latent[1] += 1
                    else:
                        latent[0] += 1
                elif aid == "FX-B":
                    if alias_actions:
                        latent[0] += 1
                        latent[1] += 1
                    else:
                        latent[1] += 1
                elif aid == "FX-G":
                    latent[0] += 1
                    latent[1] += 1
                elif aid == "FX-MARK-A":
                    marked[0] = True
                elif aid == "FX-MARK-B":
                    marked[1] = True
                else:
                    raise ValueError("BAD_ACTION")
                result = {"status": "OK", "action_id": aid}
            elif op == "gap":
                phase = "GAP"
                result = {"status": "OK"}
            elif op == "reappear":
                variant = str(msg.get("variant", "PERSIST"))
                phase = "POST"
                alias_actions = False
                if variant == "PERSIST":
                    pass
                elif variant == "REPLACE_A_UNMARKED":
                    generations[0] += 1
                    marked[0] = False
                elif variant == "REPLACE_B_UNMARKED":
                    generations[1] += 1
                    marked[1] = False
                elif variant == "REPLACE_BOTH_PERFECT_COPY":
                    generations[0] += 1
                    generations[1] += 1
                elif variant == "ALIASED_POST":
                    alias_actions = True
                else:
                    raise ValueError("BAD_VARIANT")
                result = {"status": "OK", "variant": variant}
            elif op == "observe":
                result = {
                    "status": "OK",
                    "channels": render(phase, latent, marked),
                    "phase": phase,
                    "pid": os.getpid(),
                }
            elif op == "evaluator_state":
                result = {
                    "status": "OK",
                    "phase": phase,
                    "generations": list(generations),
                    "marked": list(marked),
                    "latent": list(latent),
                    "mapping": list(PHASES[phase]["mapping"]),
                    "alias_actions": alias_actions,
                }
            elif op == "close":
                print(json.dumps({"status": "OK"}), flush=True)
                return
            else:
                raise ValueError(f"UNKNOWN_OP:{op}")
            print(json.dumps(result, separators=(",", ":")), flush=True)
        except Exception as exc:
            print(
                json.dumps(
                    {"status": "ERROR", "error": f"{type(exc).__name__}:{exc}"},
                    separators=(",", ":"),
                ),
                flush=True,
            )


if __name__ == "__main__":
    main()
