# alpha.20.0.134-dev

Fixes a generic Execute Playbook runtime crash in package-context discovery.

## Root cause

`_string_paths()` previously classified any string containing `/` as a path.
A long prompt/command could therefore reach:

`Path(prompt) -> resolve/stat/is_file()`

and fail on macOS with `OSError: [Errno 63] File name too long`.

## Fix

- added `_plausible_resource_path()`;
- rejects long prose, multiline text, shell-like command strings and oversized path components;
- package basename matching is guarded;
- runtime `resolve()/is_file()/read_text()` is fail-safe for `OSError`, `ValueError`, and `TypeError`;
- resource discovery remains best-effort context enrichment and can no longer abort playbook execution.

No playbook/domain source was changed.
