# alpha.20.0.147-dev

## Generic Model Chat generated-file surfacing fix

Full Model Chat turns that created workspace files could fail after the agent completed because generated-file metadata called an undefined `_guess_media_type` helper.

The generated-file metadata path now uses Python `mimetypes.guess_type(...)` with a generic `application/octet-stream` fallback, matching the binary workspace download endpoint.

No playbook source, validator, template, binding, registry, compiled semantic plan, package manifest, or domain semantics are changed.

## Regression

`tests/test_r3_model_chat_generated_file_metadata.py` exercises a complete `_model_chat()` turn that creates both YAML and ZIP workspace outputs, then verifies that both outputs are surfaced with media types and binary download URLs.
