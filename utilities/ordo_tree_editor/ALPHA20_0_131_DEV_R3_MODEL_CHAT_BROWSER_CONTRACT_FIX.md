# alpha.20.0.131-dev

Fixes a regression introduced in .130.

The browser Model Chat contract remains:
- session_id
- messages[]
- attachments[]

The backend again resolves credentials through the configured live Model Settings session (`_live_credentials(payload)`), extracts the latest user message as the current agent task, and passes earlier messages as history.

The persistent workspace and multi-iteration tool agent from .130 remain enabled.
