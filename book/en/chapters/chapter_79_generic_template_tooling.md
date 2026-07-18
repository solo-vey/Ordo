# Chapter 79. Generic Template Tooling

M79 moves template handling from playbook-specific solutions into a generic tooling layer.

This is a separate Python utility in the package, similar in role to Visual Graph Generator or PathWalk. It is not runtime core.

## Template Registry

Every managed template receives a registry record:

```text
template id
version
format
render mode
input contract
output contract
owner
compatibility metadata
```

A consistency gate checks that template references and the registry do not drift apart.

## Generic renderer

The renderer has one interface independent of a specific playbook.

It receives:

```text
template reference
confirmed input/state
render context
output destination
```

and returns an output plus rendering evidence.

The renderer must not invent missing business values.

## Generic review engine

The review engine checks a generated artifact against the template contract and creates an evidence format suitable for machine and human review.

Checks include:

```text
required sections
unresolved placeholders
confirmed-state consistency
format validity
TBD policy
```

## Version diff and breaking-change gate

Template version diff identifies changes between versions. The breaking-change gate blocks an incompatible change unless it has an explicit migration decision.

## Real playbooks

M79 validates the tooling against at least two real playbooks. This matters: generic tooling is not considered generic merely because its interface is named that way.

The main M79 rule is:

```text
registry identifies;
renderer produces;
review engine verifies;
version diff protects compatibility.
```
