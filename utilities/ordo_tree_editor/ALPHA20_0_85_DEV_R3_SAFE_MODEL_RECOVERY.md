# alpha.20.0.85-dev — Safe Model Recovery

Generic bounded semantic fallback for runtime constructs not yet supported by deterministic executors.

Order:
1. deterministic executor;
2. safe model recovery only for unsupported/unresolved semantic capability;
3. runtime contract validation;
4. commit or fail closed.

Policies:
- Automatic safe fallback (default)
- Ask before fallback
- Disabled

Never eligible for fallback:
- deterministic validator FAIL;
- package-tool execution errors;
- missing package resources;
- permission/security errors;
- authority-contract violations;
- malformed/invalid StatePatch.

Recovery model output is structured and mechanically constrained to allowed state writes and allowed graph targets.
