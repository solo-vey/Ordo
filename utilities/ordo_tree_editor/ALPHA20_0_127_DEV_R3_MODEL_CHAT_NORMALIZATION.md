# alpha.20.0.127-dev

Model Chat response normalization now accepts multiple OpenAI-compatible final-answer shapes:
- choices[].message.content string;
- choices[].message.content arrays of text parts;
- choices[].message.text / answer / final / output_text;
- choices[].text/content/answer/output_text;
- compatible top-level output_text/text/content/answer/message/response.

Reasoning-only fields are not exposed as final answers.
If normalization still fails, the diagnostic contains only response keys/types, not provider message contents.
