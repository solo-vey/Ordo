# Ordo Tree Editor 0.2.0-alpha.20.0.181-dev

## Data Flow — semantic data classes

- Added canonical variable metadata contract `program_model.state.variable_metadata.<path>.data_class`.
- Supported semantic classes: `business`, `technical`, `control`, `metadata`.
- Missing or unsupported values are shown as `unclassified`; the Editor never guesses a class.
- `Show Data Flow` now has a dynamic Data filter: All plus only classes actually present (and Unclassified when applicable).
- Class-specific views retain matching variables plus their directly connected producer/consumer operations and related gates/artifacts, while hiding variables from other data streams.
- Variable Passports and the Inspector expose the effective data class.
- The feature is an Editor authoring/UI projection only and does not alter Ordo compiler/runtime semantics.
- Added regression coverage for Data Layer metadata projection and Data Flow class filtering.
