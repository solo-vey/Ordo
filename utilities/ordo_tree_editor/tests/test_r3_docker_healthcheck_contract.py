from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICE = (ROOT / "editor_service.py").read_text(encoding="utf-8")
DOCKERFILE = (ROOT / "Dockerfile").read_text(encoding="utf-8")


def test_health_endpoint_matches_the_docker_healthcheck() -> None:
    assert 'if path == "/healthz":' in SERVICE
    assert '"service": "ordo-tree-editor"' in SERVICE
    assert "http://127.0.0.1:8765/healthz" in DOCKERFILE


def test_server_uses_the_container_bind_host() -> None:
    assert 'os.environ.get("ORDO_EDITOR_HOST")' in SERVICE
    assert "ThreadingHTTPServer((bind_host, port), EditorHandler)" in SERVICE
