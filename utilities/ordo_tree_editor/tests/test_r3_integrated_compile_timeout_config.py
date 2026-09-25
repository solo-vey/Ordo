import importlib.util
from pathlib import Path

SERVICE = Path(__file__).resolve().parents[1] / "editor_service.py"
spec = importlib.util.spec_from_file_location("editor_service_timeout", SERVICE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_timeout_defaults_and_env_override(monkeypatch):
    monkeypatch.delenv("ORDO_COMPILE_TIMEOUT_SECONDS", raising=False)
    assert mod._env_timeout_seconds("ORDO_COMPILE_TIMEOUT_SECONDS", 900) == 900
    monkeypatch.setenv("ORDO_COMPILE_TIMEOUT_SECONDS", "1234")
    assert mod._env_timeout_seconds("ORDO_COMPILE_TIMEOUT_SECONDS", 900) == 1234
    monkeypatch.setenv("ORDO_COMPILE_TIMEOUT_SECONDS", "bad")
    assert mod._env_timeout_seconds("ORDO_COMPILE_TIMEOUT_SECONDS", 900) == 900
