# alpha.20.0.112-dev

- The complete workspace navigation is always visible, including before a playbook source is loaded.
- Model Chat is a normal workspace tab immediately before Help.
- Source-dependent views remain visibly present but disabled until a playbook is loaded.
- Model Chat final-response classification now accepts common provider aliases (`message`, `final_response`, `answer`, `content`, `text`, `response`) and nested `final` payloads.
- Plain-text provider responses are accepted as normal final chat answers.
- Empty final wrappers fail with an explicit provider-contract diagnostic instead of silently creating an empty assistant turn.
