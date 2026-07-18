# M74.5 — APF modularization requirements and semantic equivalence

Status: implemented

APF decomposition must be performed in the APF project, not by editing the embedded consumer copy.

Required module boundaries:

1. program metadata and imports;
2. entry and project contract;
3. process design rail;
4. playbook architecture;
5. conversation policy and CSG bindings;
6. package generation;
7. validation and release;
8. assertions and status semantics.

The exact filenames may differ, but responsibilities must not overlap silently. Includes must pin versions and use explicit namespaces.

The modular candidate cannot replace the monolith unless all gates pass:

- lint and compile pass for both versions;
- normalized Semantic JSON IR is equivalent;
- node, gate, assertion, output, contract and artifact sets are unchanged;
- pathwalk regression passes;
- no implicit override or namespace collision exists;
- generated artifact contracts remain unchanged.

`tools/apf_semantic_equivalence.py` compares two compiled IR files. It removes compilation timestamps and canary secrets, sorts operations by opcode and ID, computes canonical SHA-256 digests, and reports added, removed or changed operations.

This stage prepares the language/tooling. It does not yet decompose APF; that is M74.6.
