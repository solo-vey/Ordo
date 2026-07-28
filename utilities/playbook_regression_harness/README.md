# Playbook Regression Harness

The Playbook Regression Harness (PRH) is an optional, versioned companion utility for comparing two playbook packages. It performs canonicalization, deterministic checks, semantic projection, differential comparison, stability analysis, and preparation of chat-native or provider-API execution packages.

The current imported candidate is [`1.7.0`](versions/1.7.0/README.md). It is not part of Ordo runtime semantics and does not silently modify a playbook. The standalone directory is the editable source of truth; a PRP package may carry an expanded dependency snapshot.

PRH does not claim provider-level provenance for chat-native runs and does not issue production `GO` without the required evidence.
