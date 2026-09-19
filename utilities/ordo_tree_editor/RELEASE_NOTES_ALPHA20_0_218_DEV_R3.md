# Ordo Tree Editor 0.2.0-alpha.20.0.218-dev

- Binds explicitly to the configured host (`127.0.0.1` by default and
  `0.0.0.0` for the Docker Compose deployment).
- Exposes `/healthz`, allowing the container healthcheck to verify a running
  editor instance.
- Removes the unsupported `--host` argument from the container command now
  that the service owns the bind-host configuration.

This is a deployment/runtime refresh. It does not change canonical Ordo
language or playbook semantics.
