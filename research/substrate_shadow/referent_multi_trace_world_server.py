from __future__ import annotations

import json
import os
import sys

MAP = (0, 0, 1, 1)
OFFSETS = (7, 31, 79, 127)
TRACE_OFFSETS = {
    "A1": (211, 307, 0, 0),
    "A2": (401, 503, 0, 0),
    "B_NOISE": (0, 0, 601, 709),
}


def render(latent: list[int], traces: dict[str, bool]) -> list[int]:
    out: list[int] = []
    for i, src in enumerate(MAP):
        state = latent[src]
        trace_term = sum(offsets[i] for name, offsets in TRACE_OFFSETS.items() if traces[name])
        out.append((state * state * (i + 5) + state * 17 + OFFSETS[i] + trace_term) % 10007)
    return out


def main() -> None:
    latent = [0, 0]
    traces = {name: False for name in TRACE_OFFSETS}
    generations = [0, 0]
    visible = True
    for raw in sys.stdin:
        try:
            msg = json.loads(raw)
            op = str(msg.get("op", ""))
            if op == "reset":
                latent = [0, 0]
                traces = {name: False for name in TRACE_OFFSETS}
                generations = [0, 0]
                visible = True
                result = {"status": "OK"}
            elif op == "act":
                aid = str(msg.get("action_id", ""))
                if aid == "FX-A":
                    latent[0] += 1
                elif aid == "FX-B":
                    latent[1] += 1
                elif aid == "FX-G":
                    latent[0] += 1
                    latent[1] += 1
                elif aid == "FX-MARK-A1":
                    traces["A1"] = True
                elif aid == "FX-MARK-A2":
                    traces["A2"] = True
                elif aid == "FX-MARK-B-NOISE":
                    traces["B_NOISE"] = True
                else:
                    raise ValueError("BAD_ACTION")
                result = {"status": "OK", "action_id": aid}
            elif op == "gap":
                visible = False
                result = {"status": "OK"}
            elif op == "reappear":
                variant = str(msg.get("variant", "PERSIST"))
                if variant == "PERSIST":
                    pass
                elif variant == "REPLACE_UNMARKED":
                    generations[0] += 1
                    traces["A1"] = False
                    traces["A2"] = False
                elif variant == "REPLACE_PARTIAL_A1":
                    generations[0] += 1
                    traces["A1"] = True
                    traces["A2"] = False
                elif variant == "REPLACE_PERFECT_COPY":
                    generations[0] += 1
                    traces["A1"] = True
                    traces["A2"] = True
                elif variant == "REPLACE_NUISANCE_ONLY":
                    generations[0] += 1
                    traces["A1"] = False
                    traces["A2"] = False
                    traces["B_NOISE"] = True
                elif variant == "PERSIST_NUISANCE_B":
                    traces["B_NOISE"] = True
                else:
                    raise ValueError("BAD_VARIANT")
                visible = True
                result = {"status": "OK", "variant": variant}
            elif op == "observe":
                result = {
                    "status": "OK",
                    "channels": render(latent, traces) if visible else [],
                    "visible": visible,
                    "pid": os.getpid(),
                }
            elif op == "evaluator_identity":
                result = {
                    "status": "OK",
                    "generations": list(generations),
                    "traces": dict(traces),
                    "latent": list(latent),
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
