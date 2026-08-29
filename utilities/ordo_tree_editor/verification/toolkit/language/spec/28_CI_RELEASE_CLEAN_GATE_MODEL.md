# 28. CI / Release Clean Gate Model

Status: `M69.0 accepted design / no runtime semantics`

This model defines how CI and release systems consume Ordo repository hygiene evidence.

It is a language-adjacent governance and tooling convention. It is not an opcode, runtime behavior, compiler rule, or package-local process.

## Source of truth

The source of truth remains:

```text
ordo clean-check <package>
ordo repo-check <repo> --clean
```

CI and release systems are orchestration layers only. They must not duplicate the clean-check decision model.

## Gate classes

The standard gate classes are:

- `pull_request`;
- `main_branch`;
- `release_candidate`;
- `release`;
- `manual_audit`.

Each gate declares a profile, warning policy, report path, and evidence-retention intent.

## Release strictness

Release-oriented gates should use `strict` and `fail_on_warning=true` unless an explicit project decision says otherwise.

## Delegation boundary

Applied packages remain delegated by default. A CI or release gate cannot silently convert delegated package roots into required roots.

## Evidence principle

A gate result is trustworthy only when the underlying CLI report is preserved and linked to the repository revision or release candidate being evaluated.

## Non-goals

This model does not define:

- CI provider syntax;
- GitHub Actions implementation;
- package mutation;
- automatic repair;
- release packaging;
- new IR or opcode semantics.
