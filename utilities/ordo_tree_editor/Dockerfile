FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ORDO_EDITOR_HOST=0.0.0.0 \
    ORDO_EDITOR_PORT=8765

WORKDIR /app

RUN useradd --create-home --uid 10001 ordo

COPY utilities/ordo_tree_editor/requirements-runtime.txt /tmp/requirements-runtime.txt
RUN pip install --no-cache-dir --disable-pip-version-check -r /tmp/requirements-runtime.txt

COPY utilities/ordo_tree_editor /app/utilities/ordo_tree_editor
COPY cli/ordo /app/cli/ordo
COPY language /app/language
COPY packages/ordo_applied_project_factory/source/tree_module_library /app/packages/ordo_applied_project_factory/source/tree_module_library

RUN find /app -type d -name __pycache__ -prune -exec rm -rf {} + \
    && find /app -type d -name .pytest_cache -prune -exec rm -rf {} + \
    && chown -R ordo:ordo /app

USER ordo
EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/healthz', timeout=3)"

CMD ["python", "utilities/ordo_tree_editor/editor_service.py", "--port", "8765", "--no-browser"]
