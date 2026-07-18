# Chapter 25. Ordo Libraries: include, import, and Reusing Ready-Made Solutions

## Why This Is Needed

When an Ordo program grows beyond a few simple steps, repetition appears very quickly. The same contract checks, the same gates before the final result, similar approval rules, identical trace requirements, similar output templates, and recurring test, regression, and coverage rules appear again and again.

Traditional programming languages have long used libraries to solve this problem. A programmer does not write everything from scratch each time. They connect a ready-made module, function, package, or framework. If they need dates, HTTP requests, JSON, or testing, they use an existing library.

Ordo needs a similar mechanism, adapted not to classic code but to controlling AI-model behavior. An Ordo library is not merely a file of functions. It is a ready-made package of Ordo constructs that can be connected to the current Ordo program: gates, nodes, status semantics, output templates, approval chains, test patterns, debug rules, domain vocabulary, and reusable flows.

Without libraries, every large playbook begins to turn into an isolated all-in-one document. It accumulates its own copies of rules, wording, exceptions, and variants of the same checks. Over time, such documents become difficult to maintain: changing one basic rule requires finding it in dozens of places.

Libraries move recurring solutions into separate reusable packages and connect them explicitly.

![Nebu — idea: a library as an explicit package of behavior](../assets/mascots/64x64/Nebu_idea_64x64.png)

## Simple Explanation

At its simplest, an Ordo Library is a ready-made set of rules and constructs that an Ordo program can be told to use.

For example:

```yaml
include:
  - library: "ordo.validation.contract_first"
    version: "0.1"
    as: "contract_first"
```

This means: include the `ordo.validation.contract_first` library, use exactly version `0.1`, and give it the local name `contract_first`.

The Ordo program can then use its parts:

```yaml
use:
  - contract_first.gates
  - contract_first.assertions
  - contract_first.approval_rules
```

Instead of describing basic contract-first execution rules again in every playbook, we include a ready-made library and use its exports.

## How a Library Differs from Core, Profile, and Domain Pack

Libraries must not be confused with other Ordo layers.

`Ordo Core` is the base language. It defines fundamental constructs: intent, contract, state, node, gate, output, status, trace, and assertion.

`Ordo Profile` is a specialized operating mode or style of using Ordo. Examples include profiles for documentation, QA, approval, artifact generation, and rendered validation.

`Domain Pack` is a package of knowledge and rules for a specific subject domain, such as a History Event Domain Pack or Monitoring Event Domain Pack.

`Ordo Library` is a reusable package that may contain pieces of Core logic, profile bindings, domain blocks, or execution patterns, but does not have to be a complete Domain Pack or Profile.

A library may be small: only a set of standard gates for pre-final validation.

It may be medium-sized: a ready-made guided-intake pattern.

It may be large: a complete reusable package for manual QA runbook generation.

The defining feature of a library is reuse.

## What an Ordo Library May Contain

An Ordo library may contain:

```text
- ready-made NODE.DEF constructs;
- ready-made GATE.DEF constructs;
- ready-made ASSERT.NOT constructs;
- ready-made STATUS.SEMANTICS;
- ready-made TEMPLATE.BIND constructs;
- ready-made OUTPUT.DEF constructs;
- ready-made RENDER.VALIDATE rules;
- ready-made EVIDENCE.MATRIX schemas;
- ready-made APPROVAL.REQUIRE chains;
- ready-made DEBUG.MODE profiles;
- ready-made TEST.DEF templates;
- ready-made REGRESSION.SUITE patterns;
- ready-made FREEFORM.COVERAGE rules;
- ready-made execution patterns;
- ready-made document templates;
- ready-made domain-specific rule sets.
```

An Ordo library is therefore a package of behavior, not merely a package of text.

## Basic Language Constructs

Ordo needs the following constructs for libraries:

```text
LIB.DEF
INCLUDE
IMPORT
USE
EXPORT
NAMESPACE
ALIAS
VERSION.REQUIRE
COMPAT.CHECK
CONFLICT.DETECT
CONFLICT.RESOLVE
OVERRIDE.ALLOW
OVERRIDE.DENY
TRUST.LEVEL
```

This is the minimum set needed to keep libraries from becoming dangerous.

## LIB.DEF

`LIB.DEF` describes the library itself.

For example:

```yaml
library:
  id: "ordo.validation.contract_first"
  version: "0.1"
  name: "Contract-first validation library"

exports:
  gates:
    - "G_CONTRACT_CONFIRMED"
    - "G_NO_FINAL_OUTPUT_WITHOUT_APPROVAL"

  assertions:
    - "ASSERT_NOT_FINAL_BEFORE_CONTRACT"

requires:
  ordo_version: ">=0.11"
```

This description tells the Ordo compiler what the library contains, what it exports, and which Ordo version it is compatible with.

## INCLUDE

`INCLUDE` means physically or logically connecting a library to an Ordo program.

```yaml
include:
  - library: "ordo.validation.contract_first"
    version: "0.1"
    as: "contract_first"
```

Ordo rule: libraries must not be included implicitly. If a playbook uses a library, this must be visible in source and compiled IR.

Bad:

```text
the model guessed that contract-first rules should be applied
```

Good:

```yaml
include:
  - library: "ordo.validation.contract_first"
    version: "0.1"
```

## IMPORT and USE

`IMPORT` and `USE` may have different semantics.

`IMPORT` means: make specific library exports available to the current Ordo program.

`USE` means: actually apply included constructs at a specific execution location.

For example:

```yaml
import:
  - from: "contract_first"
    items:
      - "G_CONTRACT_CONFIRMED"
      - "ASSERT_NOT_FINAL_BEFORE_CONTRACT"

use:
  - gate: "contract_first.G_CONTRACT_CONFIRMED"
    at: "before_output_generation"
```

This distinction matters. A library may be included without every part of it being used.

![Nebu — thinking: include does not mean automatic use of everything](../assets/mascots/64x64/Nebu_thinking_64x64.png)

## EXPORT

`EXPORT` defines what a library allows external programs to use.

For example:

```yaml
exports:
  gates:
    - id: "G_CONTRACT_CONFIRMED"
      visibility: "public"

  internal_rules:
    - id: "R_CONTRACT_PARSE_HELPER"
      visibility: "private"
```

Not everything inside a library must be externally accessible. Some rules may be internal implementation details of the library itself.

## NAMESPACE and ALIAS

A namespace prevents naming conflicts.

Without namespaces, two libraries may contain a gate with the same name:

```text
G_APPROVAL_REQUIRED
```

But those gates may represent different rules.

The correct reference should therefore be fully qualified:

```text
contract_first.G_APPROVAL_REQUIRED
artifact_validation.G_APPROVAL_REQUIRED
```

An alias shortens long names:

```yaml
include:
  - library: "ordo.artifact.render_validation"
    version: "0.1"
    as: "render_validation"
```

Then the program can write:

```yaml
use:
  - render_validation.G_RENDERED_ARTIFACT_CHECK
```

## Version Pinning

Libraries must be included with a version.

Bad:

```yaml
include:
  - library: "ordo.qa.manual_runbook"
```

Good:

```yaml
include:
  - library: "ordo.qa.manual_runbook"
    version: "0.1"
```

The reason is simple: if the library changes, the playbook may begin to behave differently. This is critical in Ordo because we control model behavior, not merely text.

The version must be part of the execution contract.

## Compatibility Check

The Ordo compiler must check library compatibility with the current language, Profile, Domain Pack, and runtime.

For example:

```yaml
compatibility:
  requires_ordo: ">=0.11"
  requires_profiles:
    - "documentation_runtime"
    - "debug_test_improvement"
  incompatible_with:
    - "legacy_all_in_one_mode"
```

In compiled IR, this may become a separate op:

```json
{
  "op": "LIB.COMPAT.CHECK",
  "library": "ordo.qa.manual_runbook",
  "version": "0.1",
  "requires_ordo": ">=0.11"
}
```

If the compatibility check fails, Ordo must not silently continue execution.

## Conflict Detection

Conflicts between libraries must be explicit.

For example, one library says:

```text
ready_for_first_run = execution may begin
```

Another says:

```text
ready_for_first_run = manual confirmation is still required
```

Ordo must not decide silently which one is correct.

There must be a conflict record:

```yaml
conflict:
  type: "status_semantics_conflict"
  key: "ready_for_first_run"
  sources:
    - "library_a"
    - "library_b"
  resolution: "required"
```

Possible next actions include:

```text
- ask a human;
- apply an explicitly defined priority;
- block compilation;
- allow an override only with a reason.
```

## Override Rules

Override is one of the most dangerous parts of libraries.

If an included library can silently rewrite a gate, status, or assertion, Ordo's reliability collapses.

The rule is therefore:

```text
Every override must be explicit.
```

For example:

```yaml
override:
  allow:
    - target: "contract_first.G_NO_FINAL_OUTPUT_WITHOUT_APPROVAL"
      by: "history_event.G_PRE_ARCHIVE_APPROVAL"
      reason: "domain pack has stricter equivalent gate"
```

Without such a record, the override must be denied.

![Nebu — attention: an override must be explicit](../assets/mascots/64x64/Nebu_attention_64x64.png)

## Trust Level

Not all libraries are equally reliable. Ordo should therefore support trust levels.

For example:

```yaml
library:
  id: "ordo.validation.contract_first"
  version: "0.1"
  trust_level: "official"
```

Possible levels include:

```text
official
verified
project_local
experimental
untrusted
```

Production workflows should normally reject `experimental` or `untrusted` libraries without separate approval.

## Libraries and the Debug/Test/Improvement Layer

Libraries must be visible to debug, testing, and improvement.

If a gate came from a library, the trace should show that:

```yaml
trace_source: "model_self_report"
gate_report:
  - gate_id: "contract_first.G_CONTRACT_CONFIRMED"
    source:
      kind: "library"
      id: "ordo.validation.contract_first"
      version: "0.1"
    status: "passed"
```

If a user identifies a problem, the improvement record must be able to bind it to the library:

```yaml
affected_unit:
  kind: "library"
  id: "ordo.validation.contract_first"
  version: "0.1"
  export: "G_CONTRACT_CONFIRMED"
```

This makes it possible to improve not only one playbook but also the reusable solution.

## Libraries and FREEFORM

A library may contain FREEFORM, but it must be controlled FREEFORM.

Bad:

```yaml
freeform:
  text: "there are many rules here; the model will figure them out"
```

Good:

```yaml
freeform:
  id: "FF_CONTRACT_EDGE_CASES"
  binding:
    used_by:
      - "G_CONTRACT_CONFIRMED"
    reason: "domain examples are too nuanced for full formalization"
  coverage:
    required: true
```

If library FREEFORM repeatedly causes errors, the improvement loop should propose formalizing part of it.

## Types of Libraries

In practice, Ordo libraries can be divided into several types.

### Core Utility Libraries

Contain universal small constructs: standard assertions, common gates, and status helpers.

### Profile Libraries

Contain ready-made blocks for documentation, QA, approval, validation, and rendered artifact checks.

### Domain Libraries

Contain reusable parts for a specific domain: History Event, Monitoring Event, or Legal Review.

### Pattern Libraries

Contain execution patterns: guided intake, contract-first flow, pre-archive approval, or self-check before handoff.

### Template Libraries

Contain document templates, output structures, and package layouts.

### Connector/Tool Libraries

Contain rules for working with external tools, APIs, files, and runners.

## Small Example

Imagine an Ordo program that must create an analytical package.

Without libraries, it may contain dozens of local rules:

```text
- confirm the contract first;
- do not create the final package before approval;
- validate rendered artifacts;
- generate a validation report;
- generate a consistency report;
- capture improvement feedback;
- run regression tests.
```

With libraries, this can be written as:

```yaml
include:
  - library: "ordo.validation.contract_first"
    version: "0.1"
    as: "contract_first"

  - library: "ordo.artifact.render_validation"
    version: "0.1"
    as: "render_validation"

  - library: "ordo.debug_test.basic_regression"
    version: "0.1"
    as: "regression"

use:
  - contract_first.required_contract_gates
  - render_validation.pre_handoff_checks
  - regression.minimum_suite
```

This is shorter, cleaner, and safer when each library has a version, namespace, compatibility check, and tests.

## Typical Mistakes

The first mistake is treating a library as a piece of text. In Ordo, a library must be a structured package that the compiler can validate.

The second mistake is including libraries without versions. This makes behavior unstable.

The third mistake is allowing implicit imports. If the model “guessed” that it should use a library, this is not Ordo execution.

The fourth mistake is failing to record conflicts. Conflicting status semantics or gates must not be resolved silently.

The fifth mistake is allowing hidden overrides. A library must not silently change the behavior of the main playbook.

The sixth mistake is failing to test libraries. If a reusable package has no tests or coverage, it merely spreads defects from one playbook to many playbooks.

## Mini-Exercise

Take any large prompt or playbook and find recurring parts.

Write down:

```text
- which gates repeat;
- which output templates repeat;
- which approval rules repeat;
- which checks could move into a reusable library;
- which parts should be exported;
- which parts should remain private;
- which versions and compatibility rules are needed.
```

Then try to name one library that could exist separately.

For example:

```text
ordo.validation.contract_first
ordo.artifact.pre_handoff_validation
ordo.qa.manual_runbook
ordo.debug_test.basic_regression
```

## Short Summary

Ordo libraries exist so that the same rules do not have to be rewritten in every playbook.

An Ordo Library is a reusable package of Ordo constructs: gates, nodes, assertions, status semantics, templates, tests, debug rules, domain rules, or execution patterns.

Libraries must be included explicitly through include/import/use and must have a namespace, alias, version pinning, compatibility checks, conflict detection, explicit override rules, and a trust level.

Well-designed libraries make Ordo programs shorter, more stable, and easier to evolve.

Poorly designed libraries create hidden dependencies, conflicts, and uncontrolled changes in model behavior.

The main rule is:

```text
In Ordo, a library is not a hidden text fragment but an explicit, versioned, and verifiable package of behavior.
```

---

<!-- REVIEWED: chapter 25; Nebu markers checked -->
