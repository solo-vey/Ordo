import importlib.util
import re
import sys
from pathlib import Path

COMPILER_DIR = Path(__file__).resolve().parents[1] / "integrated_compiler"
sys.path.insert(0, str(COMPILER_DIR))
COMPILER = COMPILER_DIR / "compile_runtime_semantic_plan_v7.py"
spec = importlib.util.spec_from_file_location("compiler_v7_perf", COMPILER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def reference(value, names):
    out=set()
    for _,x in mod.walk(value):
        if not isinstance(x,str):
            continue
        for name in names:
            if re.search(r'(?<![A-Za-z0-9_])'+re.escape(name)+r'(?![A-Za-z0-9_])',x):
                out.add(name)
    return out


def test_semantic_state_mentions_matches_reference_semantics():
    names={"state","state_detail","foo.bar","alpha","x_y","x"}
    samples=[
        {"text":"state state_detail foo.bar alpha x_y x"},
        {"nested":["prestate should not match state", "(state)", "foo.bar!", "x-y x_y"]},
        {"v":"alpha_beta alpha/beta alpha"},
    ]
    for sample in samples:
        assert mod.semantic_state_mentions(sample,names)==reference(sample,names)


def test_semantic_state_matcher_is_cached():
    names={f"field_{i}" for i in range(300)}
    first=mod._semantic_state_matcher(names)
    second=mod._semantic_state_matcher(set(names))
    assert first is second
