# Ordo Tree Editor 0.2.0-alpha.20.0.168-dev

## Local REST API reference and OpenAPI contract

No canonical Ordo language/runtime semantics changed in this release.

Added an official local REST API reference for the HTTP contract used by the Editor web UI and Python server:

- OpenAPI 3.1 specification covering all 38 implemented HTTP operations (33 POST, 5 GET);
- grouped API reference at `/api-docs/`;
- raw `/api-docs/openapi.yaml` and `/api-docs/openapi.json`;
- `/api-docs/swagger.yaml` compatibility alias;
- request parameter/body documentation and operation grouping;
- Help → REST API page linking to the reference and machine-readable files;
- release regression that compares EditorHandler routes with the OpenAPI method/path set and fails on drift.

The server remains local-by-default (`127.0.0.1`). Publishing the reference does not make the Editor an Internet-facing service and does not extend canonical Ordo semantics.
