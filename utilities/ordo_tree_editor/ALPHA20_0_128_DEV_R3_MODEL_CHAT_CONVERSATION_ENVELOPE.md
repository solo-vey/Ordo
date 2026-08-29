# alpha.20.0.128-dev

Model Chat unwraps structured conversation envelopes such as `conversation`, `messages`, `history`, and nested `final` objects. The last assistant/model/ai message is rendered instead of the raw JSON envelope. Serialized JSON inside `answer_markdown` is unwrapped defensively in both backend and frontend.
