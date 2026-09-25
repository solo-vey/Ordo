# Ordo Tree Editor 0.2.0-alpha.20.0.223-dev

## Fixed

- Restored the `/healthz` endpoint required by the Docker image healthcheck.
- Made the HTTP server respect `ORDO_EDITOR_HOST`, allowing the container to bind
  to `0.0.0.0` while retaining a local-browser URL in startup output.
