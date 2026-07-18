# Start Prompt — APF rc.7 CLI integration contracts

Continue from `APF_TRANSFER_PACKAGE_CURRENT_STATE_RC7_CLI_INTEGRATION_CONTRACTS.zip`.

Important boundary: work only on APF package/playbook creation process. Do not modify the Ordo language package, compiler, runtime core, language primitives, or CLI implementation.

Current version: `v0.1.0-rc.7-cli-integration-contracts`.

Latest patch: `APF_CLI_INTEGRATION_CONTRACTS`.

Key rule: APF consumes external Ordo CLI checks as evidence. If a required CLI check is unavailable, APF records `pending-language-tooling` / `not-run`; it does not simulate a passed result.
