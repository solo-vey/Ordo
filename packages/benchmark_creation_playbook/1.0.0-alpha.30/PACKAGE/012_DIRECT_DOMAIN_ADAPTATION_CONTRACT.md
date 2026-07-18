# 012. Direct Domain Adaptation Contract

**Backlog:** BL-BENCH-012  
**Output variant:** `PV-DIRECT`

## Experimental purpose

`PV-DIRECT` measures how an almost-original instruction corpus performs after direct adaptation to the benchmark domain, without importing the structural and semantic improvements developed in the YAML branch.

## Authoritative source boundary

Allowed sources:

- one explicitly selected original all-in-one corpus and its declared supporting files;
- the common benchmark test-case source package;
- a versioned terminology/domain mapping table;
- explicit owner decisions required to resolve unavoidable domain substitutions.

Forbidden sources:

- canonical YAML playbook;
- YAML-compiled structured instructions;
- YAML-derived historical compiler output;
- validators, prompts or templates created specifically to improve those variants;
- previous benchmark outputs, scores or diagnostics;
- undocumented memory of improvements learned from another variant.

## Allowed adaptations

- rename domain entities, artifact names and identifiers;
- replace original domain examples with benchmark-domain examples;
- bind common benchmark input/output document names;
- remove source-domain material that is structurally impossible in the target domain, with explicit deviation record;
- add only the minimum bridge text required to keep the original mechanism coherent.

## Forbidden adaptations

- converting the corpus into a step graph;
- adding YAML-specific gates or correction machinery;
- importing missing rules because another variant has them;
- rewriting the corpus to match expected evaluator criteria;
- silently changing the original decision model;
- optimizing based on prior run performance.

## Required adaptation record

For every changed section record:

- source section identifier;
- change type: rename / domain substitution / removal / minimal bridge;
- before summary;
- after summary;
- reason;
- evidence source;
- confirmation that no YAML-derived rule was imported.

## Required outputs

- adapted all-in-one corpus;
- source-to-adapted mapping;
- adaptation decision log;
- contamination declaration;
- validation report;
- source hash and checksums.

## Acceptance gates

- original mechanism remains recognizable and traceable;
- all target-domain names are consistent;
- benchmark source facts are bound correctly;
- no YAML-derived contamination is detected;
- every non-editorial change is logged;
- known gaps remain visible rather than being repaired from other variants.

## Current implementation status

The adaptation contract is defined. A production adaptation pipeline is not yet implemented.
