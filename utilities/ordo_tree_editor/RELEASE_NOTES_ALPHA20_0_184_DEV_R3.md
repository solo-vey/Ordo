# Ordo Tree Editor 0.2.0-alpha.20.0.184-dev

- Fixed Source Data Flow viewport interaction so native scrolling/panning never clears the selected/focused entity; focus is cleared only by the explicit `Clear focus` control.
- Replaced the single shared Data Flow Assistant transcript with persistent per-entity conversation threads keyed by source entity id.
- Switching between tree nodes or Variable Passports now restores each entity's prior assistant conversation instead of deleting it.
- `Clear focus`, Data Flow filtering, and navigation no longer delete stored entity conversations; loading a different playbook package resets the thread store.
- In-flight model responses remain bound to the entity that initiated the request, even if the analyst switches selection before the response arrives.
- Added regression coverage for viewport/focus persistence and per-entity assistant history.
- No canonical Ordo, compiler, or runtime execution semantics changed.
