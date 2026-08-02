# Integration recommendation for the next ARF release

Add `IMPLEMENTATION_CHANGE_LIFECYCLE` as the third optional template in `ARF_STANDARD_TREE_MODULES`.

## Intended place in a host playbook

Factory guidance should describe this module as an application-code implementation continuation, not as a generic playbook-maintenance utility.

Recommended host sequence:

```text
analytical collection and approval
→ materialized analytical document/package
→ implementation prompt generation
→ IMPLEMENTATION_CHANGE_LIFECYCLE
→ changed application module or developer handoff
→ host continuation
```

Typical use cases include implementing a calculation, integration behavior, workflow rule, or another business capability in an existing application module.

## When factory guidance should recommend it

Recommend this module when the author is designing a subtree that contains all of the following intentions:

- an approved analytical artifact or requirements package exists;
- an implementation prompt already exists;
- a target application implementation module may be supplied as ZIP, Git reference, or another supported code location;
- the change scope must be assessed before execution;
- the analyst may choose between model-direct changes and developer handoff;
- a changed candidate requires tests and verification;
- the result returns to the host tree rather than terminating the whole process.

## Required host responsibilities

Before entry, the host should provide:

- the implementation prompt field;
- the confirmed analytical requirement fields;
- the entry node after prompt generation;
- the success exit node;
- repository/package access rules;
- domain-specific validation and test expectations.

Before instantiation, factory guidance should preview generated node IDs, state fields, supported baseline forms, the two execution branches, and the caller-provided entry/exit bindings.

The template must remain optional. It must not be presented as a template for changing the ARF framework or for generating the analytical document itself.
