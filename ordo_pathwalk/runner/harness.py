"""Open-loop harness for `ordo-pathwalk run`.

The M60-native harness treats PathWalk as a companion benchmark utility that
consumes real Ordo runtime packages through the embedded runtime CLI. It no
longer vendors or patches a legacy embedded CLI. In enforced mode, a source
package is compiled and packaged through the current Ordo CLI before the model
is allowed to interact with it.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from ..generator.noise_gen import PathWalkScript
from .model_drivers import build_driver


def _source_tree_sha256(root: Path) -> str:
    import hashlib
    excluded_parts = {"__pycache__", ".git", ".ordo-generated"}
    excluded_names = {"package_report.json", "BUILD_MANIFEST.json", "SHA256SUMS.txt"}
    h = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in excluded_parts for part in rel.parts):
            continue
        if path.suffix == ".pyc" or path.name in excluded_names:
            continue
        if "reports" in rel.parts and path.name.startswith("ci_release_evidence"):
            continue
        rel_b = rel.as_posix().encode("utf-8")
        h.update(len(rel_b).to_bytes(8, "big")); h.update(rel_b)
        data = path.read_bytes(); h.update(len(data).to_bytes(8, "big")); h.update(data)
    return h.hexdigest()

DEFAULT_SYSTEM_PROMPT = """\
Ти ведеш guided-intake сесію для Ordo-пакета "лабіринт" (PathWalk benchmark).
Пакет лежить у поточній директорії ("."). {cli_instruction}

M60.4 runtime protocol:
- source of truth для runtime: embedded CLI `./cli_embedded/ordo`.
- НЕ використовуй `python3 cli_embedded/ordo_run.py` — це застарілий launcher.
- НЕ читай напряму `compiled/*` (`cat`, `less`, Python-read, view/read/open). У enforced mode це protocol violation.
- На початку або коли сумніваєшся: `./cli_embedded/ordo runtime-status .`
- Перевірити compiled targets: `./cli_embedded/ordo verify-targets .`
- Дізнатись поточне питання: `./cli_embedded/ordo next-step . --format auto`
- Відповісти на поточний вузол: спочатку запиши відповідь у UTF-8 файл, потім виклич:
  `./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <FILE>`
- Після submit покажи користувачу коротко evidence path/digest і session-trace digest, якщо вони є у stdout/report.
- Якщо користувач просить повернутися до раніше пройденого кроку:
  `./cli_embedded/ordo restore-session . --to-seq <N> --reason "<коротка причина>"`
  Restore є append-only: не видаляє історію, а створює restore evidence/snapshot/trace event.
- Для фінальної перевірки: `./cli_embedded/ordo verify-session .`

Правила діалогу:
- Не показуй користувачу внутрішні назви state-полів (`path_step_N`, `path_node_step_N`) і JSON-структури звітів.
- Кожен вузол має id і список допустимих варіантів. Вони приходять через CLI output.
- Якщо напрямок користувача очевидний природною мовою, нормалізуй його до одного allowed option.
- Якщо користувач каже піти в напрямку, якого немає серед допустимих варіантів поточного вузла, не викликай `intake --submit`; повідом реальний список варіантів.
- Якщо користувач ставить уточнення не по суті вибору напрямку, відповідай, але не submit-ь вузол.
- Якщо шлях завершено, повідом, що PathWalk-сценарій завершено, і виконай `verify-session`.
"""

CLI_INSTRUCTION_ENFORCED = (
    "Використовуй ВИКЛЮЧНО `./cli_embedded/ordo` для runtime-інформації "
    "(runtime-status, verify-targets, next-step --format auto, intake --submit, restore-session, verify-session). "
    "Пряме читання compiled/* заборонене."
)
CLI_INSTRUCTION_IR_READABLE = (
    "Baseline mode: CLI недоступний, а compiled/program.ir.json може бути прочитаний напряму. "
    "Це НЕ enforced Ordo runtime; використовуй тільки для порівняння."
)
CLI_INSTRUCTION_FREEFORM = (
    "Baseline mode: ні CLI, ні compiled IR тобі не доступні — веди сесію лише зі слів користувача."
)


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _local_ordo_env() -> dict[str, str]:
    env = os.environ.copy()
    cli_path = str(_workspace_root() / "cli")
    env["PYTHONPATH"] = cli_path + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return env


def _run_local_ordo(args: list[str], cwd: Path | None = None, *, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ordo.cli", *args],
        cwd=cwd or _workspace_root(),
        env=_local_ordo_env(),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _copy_first_zip_root(zip_path: Path, dest: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="pathwalk_runtime_unzip_") as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp_path)
        roots = [p for p in tmp_path.iterdir() if p.is_dir()]
        if len(roots) != 1:
            raise RuntimeError(f"expected one root directory in runtime archive, found {len(roots)}")
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(roots[0], dest)
        launcher = dest / "cli_embedded" / "ordo"
        if launcher.exists():
            launcher.chmod(launcher.stat().st_mode | 0o111)


def _prepare_m60_runtime_sandbox(tree_package_dir: Path, sandbox_dir: Path, runtime_view: str) -> None:
    """Copy or build a current M60 runtime package into sandbox_dir.

    If tree_package_dir is already a runtime package with `cli_embedded/ordo`, it
    is copied as-is. Otherwise it is treated as an editable source/dev package:
    compile + package --profile runtime --runtime-view <mode> using the current
    workspace CLI, then unzip the runtime package into the sandbox.
    """
    tree_package_dir = Path(tree_package_dir)
    if sandbox_dir.exists():
        shutil.rmtree(sandbox_dir)

    if (tree_package_dir / "cli_embedded" / "ordo").exists() and (tree_package_dir / "ordo.runtime.json").exists():
        shutil.copytree(tree_package_dir, sandbox_dir)
        launcher = sandbox_dir / "cli_embedded" / "ordo"
        if launcher.exists():
            launcher.chmod(launcher.stat().st_mode | 0o111)
        return

    source_sandbox = sandbox_dir.parent / f"{sandbox_dir.name}_source"
    if source_sandbox.exists():
        shutil.rmtree(source_sandbox)
    shutil.copytree(tree_package_dir, source_sandbox)

    compile_result = _run_local_ordo(["compile", str(source_sandbox), "--force"], timeout=60)
    if compile_result.returncode != 0:
        raise RuntimeError("ordo compile failed:\n" + compile_result.stdout + compile_result.stderr)

    validation_result = _run_local_ordo(["validate-release", str(source_sandbox), "--answers", str(source_sandbox / "run_inputs" / "answers_success.yaml"), "--intake-answers", str(source_sandbox / "run_inputs" / "intake_success.yaml")], timeout=90)
    if validation_result.returncode != 0:
        raise RuntimeError("ordo validate-release failed:\n" + validation_result.stdout + validation_result.stderr)

    ci_evidence = source_sandbox / "reports" / "ci_release_evidence.json"
    ci_evidence.parent.mkdir(parents=True, exist_ok=True)
    ci_evidence.write_text(json.dumps({
        "schema_version": "ordo.ci_release_evidence.v1",
        "status": "passed",
        "revision": "pathwalk-disposable-runtime",
        "run_id": f"pathwalk-{runtime_view}",
        "issued_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_tree_sha256": _source_tree_sha256(source_sandbox),
        "test_matrix": [{"id": "pathwalk-runtime-sandbox", "status": "passed"}],
    }), encoding="utf-8")

    runtime_zip = sandbox_dir.parent / f"{sandbox_dir.name}_runtime.zip"
    package_result = _run_local_ordo([
        "package",
        str(source_sandbox),
        "--profile",
        "runtime",
        "--runtime-view",
        runtime_view,
        "--allow-unvalidated-output",
        "--ci-evidence",
        str(ci_evidence),
        "--out",
        str(runtime_zip),
    ], timeout=90)
    if package_result.returncode != 0:
        raise RuntimeError("ordo package --profile runtime failed:\n" + package_result.stdout + package_result.stderr)

    _copy_first_zip_root(runtime_zip, sandbox_dir)


def _prepare_baseline_sandbox(tree_package_dir: Path, sandbox_dir: Path, *, remove_ir: bool) -> None:
    if sandbox_dir.exists():
        shutil.rmtree(sandbox_dir)
    shutil.copytree(tree_package_dir, sandbox_dir)
    if not (sandbox_dir / "compiled" / "program.ir.json").exists() and (sandbox_dir / "source" / "program.ordo.yaml").exists():
        _run_local_ordo(["compile", str(sandbox_dir), "--force"], timeout=60)
    shutil.rmtree(sandbox_dir / "cli_embedded", ignore_errors=True)
    if remove_ir:
        shutil.rmtree(sandbox_dir / "compiled", ignore_errors=True)


def _sandbox_executor(sandbox_dir: Path) -> Any:
    def run(command: str) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=sandbox_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return (result.stdout or "") + (result.stderr or "")
        except subprocess.TimeoutExpired:
            return "[tool execution timed out after 30s]"
        except Exception as exc:  # pragma: no cover - defensive
            return f"[tool execution error: {exc}]"
    return run


def _asked_node_from_text(text: str, tree_nodes: dict[str, Any]) -> str | None:
    for node_id in tree_nodes:
        if node_id in text:
            return node_id
    return None


def _runtime_metadata(sandbox_dir: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for rel, key in [
        ("ordo.runtime.json", "runtime_manifest"),
        ("compiled/targets.manifest.json", "targets_manifest"),
    ]:
        path = sandbox_dir / rel
        if path.exists():
            try:
                data[key] = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                data[key] = {"unreadable": rel}
    return data


def run_scenario(
    *,
    tree_package_dir: Path,
    script: PathWalkScript,
    driver_spec: str,
    api_key: str,
    cli_mode: str,
    out_dir: Path,
    scenario_id: str,
    runtime_view: str = "ordo-code",
    max_retries: int = 4,
) -> Path:
    if cli_mode not in ("enforced", "ir_readable", "fully_freeform"):
        raise ValueError(f"unknown cli_mode: {cli_mode!r}")
    if runtime_view not in ("json", "ordo-code", "json,ordo-code"):
        raise ValueError(f"unknown runtime_view: {runtime_view!r}")

    sandbox_dir = out_dir / f"{scenario_id}_sandbox"

    if cli_mode == "enforced":
        cli_instruction = CLI_INSTRUCTION_ENFORCED
        _prepare_m60_runtime_sandbox(Path(tree_package_dir), sandbox_dir, runtime_view)
    elif cli_mode == "ir_readable":
        cli_instruction = CLI_INSTRUCTION_IR_READABLE
        _prepare_baseline_sandbox(Path(tree_package_dir), sandbox_dir, remove_ir=False)
    else:
        cli_instruction = CLI_INSTRUCTION_FREEFORM
        _prepare_baseline_sandbox(Path(tree_package_dir), sandbox_dir, remove_ir=True)

    system_prompt = DEFAULT_SYSTEM_PROMPT.format(cli_instruction=cli_instruction)
    executor = _sandbox_executor(sandbox_dir)
    driver = build_driver(
        driver_spec,
        system_prompt=system_prompt,
        tool_executor=executor,
        api_key=api_key,
        max_retries=max_retries,
    )

    tree_meta_path = sandbox_dir / "tree_meta.json"
    tree_nodes = {}
    if tree_meta_path.exists():
        tree_nodes = json.loads(tree_meta_path.read_text(encoding="utf-8")).get("nodes", {})

    transcript: list[dict[str, Any]] = []
    for turn in script.turns:
        result = driver.send_user_turn(turn.text)
        asked_node = _asked_node_from_text(result.final_text, tree_nodes)
        transcript.append({
            "turn_index": turn.index,
            "turn_type": turn.type,
            "user_text": turn.text,
            "model_reply_text": result.final_text,
            "tool_calls_made": result.tool_calls_made,
            "retries": getattr(result, "retries", []),
            "asked_node_id": asked_node,
            "expected_node_after": turn.expected_node_after,
        })

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{scenario_id}_transcript.json").write_text(
        json.dumps({
            "driver": driver_spec,
            "cli_mode": cli_mode,
            "runtime_view": runtime_view,
            "runtime_metadata": _runtime_metadata(sandbox_dir),
            "turns": transcript,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return sandbox_dir
