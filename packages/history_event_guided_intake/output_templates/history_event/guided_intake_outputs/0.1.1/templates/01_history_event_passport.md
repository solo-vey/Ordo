# History Event Passport — {{ state.event_alias }}

> Generated from Ordo template `HISTORY_EVENT_PASSPORT`.

## Summary

| Field | Value |
|---|---|
| Alias | `{{ state.event_alias }}` |
| UA name | {{ state.display_name_uk }} |
| EN name | {{ state.display_name_en }} |
| Path | `{{ state.selected_path }}` |
| Source field | `{{ state.source_field }}` |
| Test coverage level | {{ state.test_coverage_level }} |

## Business goal

{{ state.event_goal }}

## Value semantics contract

{{ state.value_semantics | bullets }}

## QA scope contract

{{ state.qa_scope | bullets }}

## Test strategy contract

### Manual QA coverage

{{ state.manual_qa_coverage | bullets }}

### Functional test coverage

{{ state.functional_test_coverage | bullets }}

### Unit test coverage

{{ state.unit_test_coverage | bullets }}

### Corner cases / normalization / grouping

{{ state.test_strategy_contract | bullets }}

### Rollback policy

- Rollback is used only for technical restoration of current state and must not be treated as a separate business verification scenario.

### Test documentation requirement

- {{ state.test_documentation_requirement }}

## Output and approval state

```yaml
approval_received: {{ state.approval_received | bool_lower }}
output_allowed: {{ state.output_allowed | bool_lower }}
final_package_created: {{ state.final_package_created | bool_lower }}
test_propagation_required: {{ state.test_propagation_required | bool_lower }}
```

## Template metadata

```yaml
package: {{ package.name }}
package_version: {{ package.version }}
ordo_version: {{ package.ordo_version }}
generated_at: {{ generated_at }}
```
