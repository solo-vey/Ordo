# alpha.20.0.108-dev

- The Execute Playbook “working” scroll control now uses a more oval pill shape instead of an almost perfect circle.
- Show Tree graph nodes/gates now surface top-right reference badges when their source record mentions package files.
- Badge families currently distinguish: Python, YAML, Markdown, JSON, and Other file references.
- Each badge exposes a tooltip summarizing how many references of that type were found and listing the matched paths.
- This is purely visual/read-only metadata: it does not change playbook semantics or execution behavior.
