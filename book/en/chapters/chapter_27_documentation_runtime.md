# Chapter 27. Documentation Runtime

## Why This Is Needed

In the previous chapter, we examined why the `all-in-one` format stops being the primary format when an instruction grows into a large playbook. One large file is convenient to give to a model, but inconvenient to maintain, validate, update, and debug.

A new question immediately appears: if documentation is split into dozens of separate files, how should the model know which ones are needed for the current step?

A person can open the table of contents, scan titles, recall the context, and choose the right section. A model can also do this, but if selection is left entirely to its judgment, we return to the ordinary prompt problem: it may open the wrong file, miss an important section, or use an outdated part of the documentation.

This is why Ordo needs `Documentation Runtime`.

`Documentation Runtime` is a language mechanism that controls how an Ordo program works with a large set of documents: which documents exist, when they must be read, which sections are the source of truth, which documents are supporting material, and which must not be used for decisions.

In other words, this is not merely “a folder of instructions.” It is a controlled knowledge-access layer.

## Simple Explanation

Imagine that an Ordo program is a cook and the documentation is a large culinary library.

If the cook is simply given the whole library and told “cook,” they may open an old recipe, confuse a dessert with a main course, or treat a note as a mandatory rule.

Documentation Runtime acts as a catalog and dispatcher:

```text
only these documents are needed for this step;
this document is authoritative;
this document only explains examples;
this file is deprecated;
this template may be used only after an approval gate;
this rendered artifact must be validated separately.
```

Documentation Runtime does not write business logic instead of a Domain Pack. It ensures that the model uses the correct instructions at the correct moment.

## How Documentation Runtime Differs from Ordinary Documentation

Ordinary documentation describes knowledge.

Documentation Runtime controls the use of knowledge.

Ordinary documentation may say:

```text
QA rules are described in file 05_QA_PACKAGE.
```

Documentation Runtime should be more precise:

```text
NODE package_generation may read 05_QA_PACKAGE_TEMPLATE.
Before creating the QA file, G_QA_SCOPE_CONFIRMED must be checked.
The final rendered QA file must pass RENDER.VALIDATE.
If fixture or source lookup is not confirmed, the QA file cannot be marked ready.
```

This is no longer merely a description. It is runtime behavior.

## Main Responsibilities of Documentation Runtime

In Ordo, Documentation Runtime should solve several tasks.

The first is document cataloging.

Ordo should know which documents belong to the package:

```text
README.md
execution contract
core binding
profile binding
domain pack
compiled IR
freeform ledger
validation report
source virtual docs
templates
examples
```

The second task is selecting the documents needed for the current node.

The model should not reread everything every time. Each `NODE` may define the documents that are allowed or required.

The third task is identifying the source of truth.

If split files and an all-in-one version both exist, it must be explicit that split files are edited and the all-in-one is a built artifact. Otherwise, a change may be made in the wrong place.

The fourth task is controlling rendered artifacts.

A template does not mean the final file is correct. Ordo must distinguish a template from the actually generated document.

The fifth task is traceability.

When the model creates a result, it should be possible to see which documents it relied on.

## Ordo Constructs

Documentation Runtime requires the following language constructs:

```text
DOC.CATALOG
DOC.DEF
DOC.ROLE
DOC.SOURCE_OF_TRUTH
DOC.SELECT
DOC.BIND
DOC.READ
DOC.RENDER
DOC.SPLIT
DOC.MERGE
DOC.VERSION
DOC.DEPRECATE
DOC.TRACE
RENDER.VALIDATE
```

In simple terms:

`DOC.CATALOG` describes the list of documents in a package.

`DOC.DEF` describes a specific document.

`DOC.ROLE` identifies a document's role: contract, template, example, source, generated artifact, or validation report.

`DOC.SOURCE_OF_TRUTH` identifies the authoritative file for changing a particular rule.

`DOC.SELECT` says which documents are needed for the current node.

`DOC.BIND` binds a document to a node, gate, output, or library.

`DOC.TRACE` records which documents were actually used during a run.

`RENDER.VALIDATE` validates the generated final artifact rather than the template.

## Small Example

Suppose we have an Ordo program for creating an analytical package.

In Source format, Documentation Runtime may look like this:

```yaml
doc_catalog:
  id: "history_event_docs"

  documents:
    - id: "execution_contract"
      path: "00_ORDO_EXECUTION_CONTRACT.md"
      role: "contract"
      source_of_truth: true

    - id: "domain_pack"
      path: "04_HISTORY_EVENT_DOMAIN_PACK.md"
      role: "domain_rules"
      source_of_truth: true

    - id: "qa_template"
      path: "05_QA_PACKAGE_TEMPLATE.md"
      role: "template"

    - id: "qa_output"
      path: "05_QA_PACKAGE_<ALIAS>.md"
      role: "rendered_artifact"
      generated: true

doc_select:
  node: "generate_qa_package"
  required:
    - "execution_contract"
    - "domain_pack"
    - "qa_template"
  forbidden:
    - "deprecated_all_in_one"

render_validate:
  output: "qa_output"
  rules:
    - "must_not_contain_unresolved_placeholders"
    - "must_include_manual_test_table"
    - "must_match_confirmed_contract"
```

The important point is that the model does not merely “know about the documents.” It receives rules defining which documents to use, which not to use, and how to validate the result.

## Documentation Runtime and All-in-One

Documentation Runtime does not prohibit all-in-one. It changes its role.

All-in-one may be:

```text
- a convenient read-only snapshot;
- an artifact for transfer to a model;
- an assembled representation of split documents;
- a control view of the complete package.
```

But it should not automatically be the source of truth.

If sectional files are the source of truth, Documentation Runtime should state this explicitly:

```yaml
source_of_truth:
  rules:
    - target: "playbook_logic"
      document: "source_virtual_docs/"
    - target: "rendered_snapshot"
      document: "999_ALL_IN_ONE.md"
      editable: false
```

This protects against a common mistake: the model edits the large all-in-one file while the actual sectional documents remain outdated.

## Documentation Runtime and Trace

When an Ordo program works with documents, the trace should show:

```text
which documents were selected;
why they were selected;
which documents were rejected;
which sections were used;
which outputs were generated from them;
whether rendered artifacts passed validation.
```

For example:

```yaml
trace_source: "model_self_report"
doc_trace:
  node: "generate_qa_package"

  selected:
    - id: "execution_contract"
      reason: "required for confirmed scope"
    - id: "domain_pack"
      reason: "required for domain rules"
    - id: "qa_template"
      reason: "required for output structure"

  rejected:
    - id: "deprecated_all_in_one"
      reason: "not source of truth for editing"

  rendered_outputs:
    - id: "qa_output"
      validation: "passed"
```

This trace is especially important in debug mode. If the result is wrong, we can see whether the problem lies in the logic or whether the model simply used the wrong document.

## Documentation Runtime and Libraries

After Ordo Libraries appear, Documentation Runtime becomes even more important.

A library may include its own documents:

```text
- descriptions of exported gates;
- templates;
- examples;
- compatibility rules;
- changelog;
- tests;
- coverage report.
```

Ordo should know that these documents belong to the library rather than the main playbook.

For example:

```yaml
library_docs:
  library: "ordo.validation.contract_first"
  version: "0.1"

  documents:
    - id: "contract_gates"
      path: "docs/gates.md"
      role: "library_rule_reference"

    - id: "contract_tests"
      path: "tests/contract_first_tests.yaml"
      role: "test_suite"
```

If a problem originates from a library rule, `DOC.TRACE` and `IMPROVEMENT.RECORD` should show exactly that.

## Documentation Runtime and FREEFORM

FREEFORM often contains explanations, examples, or exceptions. Documentation Runtime should help preserve control over these blocks.

For every FREEFORM block, it is useful to know:

```text
which document contains it;
which node/gate/rule it is bound to;
whether it is normative, an example, or a note;
whether the model may make decisions based on it;
whether coverage exists for it.
```

For example:

```yaml
freeform_doc_binding:
  freeform_id: "FF_EDGE_CASES"
  document: "04_HISTORY_EVENT_DOMAIN_PACK.md"
  section: "Edge cases"
  binding:
    node: "select_path"
    role: "controlled_explanation"
  decision_allowed: true
```

Without such binding, the model may treat any example as a rule or any note as permission to act.

## Typical Mistakes

The first mistake is assuming that a file list is already a runtime.

A file list is only a catalog. Runtime begins when selection rules, roles, gates, and trace exist.

The second mistake is failing to define the source of truth.

If two documents contain similar content, the model must know which one is authoritative.

The third mistake is validating the template instead of the final document.

The template may be correct while the generated artifact contains empty sections, unresolved placeholders, or data that did not come from the confirmed contract.

The fourth mistake is allowing the model to decide by itself which documents “seem relevant.”

For a simple question, that may be acceptable. For a production playbook, it is not. There should be `DOC.SELECT`.

The fifth mistake is failing to trace document usage.

Without `DOC.TRACE`, after an error it will be unclear whether the problem was in a rule or in the wrong document being used.

## Mini-Exercise

Take any large instruction set you have worked with.

Try to answer:

```text
1. Which documents belong to the package?
2. Which document is the source of truth?
3. Which documents are only examples?
4. Which documents are templates?
5. Which documents are rendered artifacts?
6. Which document is needed for each step?
7. Which documents must not be used for decisions?
8. How can you verify that the final document matches the template and contract?
9. How can the trace show which documents were used?
```

If these questions have no clear answers, you do not yet have Documentation Runtime. You only have a folder of documents.

## Short Summary

Documentation Runtime is the Ordo layer that controls work with a large set of documents.

It defines:

```text
- which documents exist;
- the role of each document;
- which document is the source of truth;
- which documents are needed for a specific node;
- which documents are forbidden or deprecated;
- how rendered artifacts are validated;
- how documentation usage is traced;
- how documents are linked to libraries, FREEFORM, and improvement records.
```

The main idea is simple:

```text
a large playbook should not merely be read;
it should be executed through a controlled documentation runtime.
```

Without Documentation Runtime, the model works with documentation as a large pile of text.

With Documentation Runtime, documentation becomes part of the executable Ordo program.

---
