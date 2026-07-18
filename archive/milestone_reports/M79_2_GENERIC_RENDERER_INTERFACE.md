# M79.2 — Generic Renderer Interface

Status: implemented.

The CLI now provides one render command across deterministic, model-rendered, and hybrid templates. Model work is always represented as an explicit job artifact; the renderer never performs a hidden model call. All modes emit provenance-bearing render evidence.
