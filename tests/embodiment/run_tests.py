from __future__ import annotations
import importlib.util, inspect, pathlib, sys, traceback

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).parent

failed = []
passed = []
for path in sorted(HERE.glob("test_*.py")):
    spec = importlib.util.spec_from_file_location(f"tests_embodiment_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    for name, fn in inspect.getmembers(module, inspect.isfunction):
        if not name.startswith("test_"):
            continue
        label = f"{path.stem}::{name}"
        try:
            fn()
            passed.append(label)
        except Exception:
            failed.append((label, traceback.format_exc()))

print(f"passed={len(passed)} failed={len(failed)}")
for n in passed:
    print("PASS", n)
for n, t in failed:
    print("FAIL", n, "\n", t)
raise SystemExit(1 if failed else 0)
