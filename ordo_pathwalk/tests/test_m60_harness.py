from pathlib import Path
import subprocess

from ordo_pathwalk.generator.maze_gen import generate_tree
from ordo_pathwalk.generator.emit_ordo_package import emit_package
from ordo_pathwalk.runner.harness import _prepare_m60_runtime_sandbox


def test_prepare_m60_runtime_sandbox_builds_current_embedded_cli(tmp_path: Path):
    source = tmp_path / "tree"
    tree = generate_tree(seed=99, depth=2, branching_range=(2, 2))
    emit_package(tree, source, "pathwalk.test", force=True)
    sandbox = tmp_path / "runtime"
    _prepare_m60_runtime_sandbox(source, sandbox, "ordo-code")
    launcher = sandbox / "cli_embedded" / "ordo"
    assert launcher.exists()
    assert (sandbox / "compiled" / "targets.manifest.json").exists()
    assert (sandbox / "runtime" / "session.ordo.trace").exists()
    res = subprocess.run([str(launcher), "next-step", str(sandbox), "--format", "auto"], capture_output=True, text=True, timeout=30)
    assert res.returncode == 0
    assert "current_contract:" in res.stdout
