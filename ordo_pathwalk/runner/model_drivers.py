"""Pluggable model drivers for the PathWalk `run --driver api:<provider>` mode.

Each driver owns its own conversation history and hides provider-specific
tool-calling wire format behind one common interface:

    driver.send_user_turn(text) -> DriverTurnResult

Internally, if the model wants to call a tool, the driver executes it via
the harness-supplied `tool_executor` callback (sandboxed bash in a copy of
the maze package directory) and loops until the model returns a plain text
reply with no pending tool calls - that is what "one turn" means here.

NEITHER of these has been run against a real API in this environment (no
credentials available in this sandbox) - the wire-format handling below is
written directly from each provider's documented tool-use contract, but is
unverified end-to-end. Treat as reviewed-not-tested until a real key is
supplied.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
import time
from typing import Any, Callable, Protocol

ToolExecutor = Callable[[str], str]  # shell command -> combined stdout+stderr


@dataclass
class DriverTurnResult:
    final_text: str
    tool_calls_made: list[dict[str, Any]] = field(default_factory=list)
    retries: list[dict[str, Any]] = field(default_factory=list)


BASH_TOOL_DESCRIPTION = (
    "Execute a shell command inside the current PathWalk package directory "
    "(e.g. `./cli_embedded/ordo next-step . --format auto`). "
    "In enforced mode this is the ONLY way to interact with the package runtime; "
    "directly reading compiled/* is a protocol violation."
)


def _is_retryable_exception(exc: BaseException) -> bool:
    name = exc.__class__.__name__.lower()
    text = str(exc).lower()
    return (
        "ratelimit" in name
        or "rate_limit" in name
        or "rate limit" in text
        or "timeout" in name
        or "timeout" in text
        or "temporarily unavailable" in text
    )


def _retry_after_seconds(exc: BaseException) -> float | None:
    for attr in ("response", "http_response"):
        resp = getattr(exc, attr, None)
        headers = getattr(resp, "headers", None) if resp is not None else None
        if headers:
            value = None
            try:
                value = headers.get("Retry-After") or headers.get("retry-after")
            except Exception:
                value = None
            if value is not None:
                try:
                    return max(0.0, float(value))
                except Exception:
                    return None
    return None


def _call_with_backoff(fn: Callable[[], Any], *, max_retries: int, retry_log: list[dict[str, Any]], sleep: Callable[[float], None] = time.sleep) -> Any:
    attempt = 0
    while True:
        try:
            return fn()
        except Exception as exc:
            if not _is_retryable_exception(exc) or attempt >= max_retries:
                raise
            delay = _retry_after_seconds(exc)
            if delay is None:
                delay = min(8.0, float(2 ** attempt))
            retry_log.append({
                "attempt": attempt + 1,
                "error_type": exc.__class__.__name__,
                "delay_seconds": delay,
            })
            sleep(delay)
            attempt += 1


class ModelDriver(Protocol):
    def send_user_turn(self, text: str) -> DriverTurnResult: ...


class AnthropicDriver:
    """Driver using the Anthropic Messages API (tool_use / tool_result blocks).

    Two cost/architecture optimizations, both motivated by a real finding:
    our own PathWalk sessions were resending 40KB+ of unchanged JSON report
    content on every single API call because message history accumulates
    forever by default and the API itself is stateless (it has no memory of
    prior calls - see design discussion). Since the actual session state
    always lives externally in the CLI (runtime/live_session_state.json,
    snapshots) rather than in the model's own memory, the model does not
    need byte-for-byte recall of old tool exchanges - only the most recent
    one, plus a short synopsis of what happened before. Both changes below
    are safe precisely because of that external-state property; they would
    NOT be safe for a general-purpose assistant that has no other memory.

    1. Prompt caching: system + tools are identical on every turn of a
       session, so they are marked cache_control="ephemeral". Anthropic
       charges a fraction of input-token price for a cache hit.
    2. History trimming: once a turn's tool exchange is resolved, its raw
       tool_use/tool_result content is replaced with a one-line synopsis in
       all FUTURE calls. Only the current turn's exchange is ever sent in
       full. This is a real trade-off (the model loses verbatim memory of
       old CLI output) that is safe here specifically because the CLI can
       always be re-queried for current truth - it would not be a safe
       default for a general assistant.
    """

    def __init__(self, *, api_key: str, model: str, system_prompt: str, tool_executor: ToolExecutor, max_tool_rounds: int = 10, keep_full_turns: int = 1, max_retries: int = 4):
        import anthropic  # local import: optional dependency, only needed for this driver

        self._client = anthropic.Anthropic(api_key=api_key, max_retries=0)
        self._model = model
        self._system_prompt = system_prompt
        self._tool_executor = tool_executor
        self._max_tool_rounds = max_tool_rounds
        self._keep_full_turns = keep_full_turns
        self._max_retries = max_retries
        self._messages: list[dict[str, Any]] = []
        self._turn_boundaries: list[int] = []  # message-list indices where each completed turn started
        self._tools = [{
            "name": "run_bash",
            "description": BASH_TOOL_DESCRIPTION,
            "input_schema": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
            "cache_control": {"type": "ephemeral"},
        }]

    def _system_blocks(self) -> list[dict[str, Any]]:
        return [{"type": "text", "text": self._system_prompt, "cache_control": {"type": "ephemeral"}}]

    def _trim_older_turns(self) -> None:
        """Replace completed turns older than the last `keep_full_turns` with
        a compact synopsis, so message history stops growing without bound."""
        cutoff = self._turn_boundaries[-self._keep_full_turns] if len(self._turn_boundaries) > self._keep_full_turns else 0
        if cutoff <= 0:
            return
        for i in range(cutoff):
            msg = self._messages[i]
            if msg.get("_synopsis_applied"):
                continue
            content = msg.get("content")
            if isinstance(content, list):
                summary_bits = []
                for block in content:
                    btype = getattr(block, "type", None) if not isinstance(block, dict) else block.get("type")
                    if btype == "tool_use":
                        cmd = getattr(block, "input", {}).get("command") if not isinstance(block, dict) else (block.get("input") or {}).get("command")
                        summary_bits.append(f"ran `{cmd}`" if cmd else "called a tool")
                    elif btype == "tool_result":
                        summary_bits.append("(tool result omitted from history; re-query the CLI if needed)")
                    elif btype == "text":
                        text = getattr(block, "text", "") if not isinstance(block, dict) else block.get("text", "")
                        if text:
                            summary_bits.append(text[:120])
                if summary_bits:
                    msg["content"] = "[earlier turn, trimmed] " + " | ".join(summary_bits)
            msg["_synopsis_applied"] = True

    def send_user_turn(self, text: str) -> DriverTurnResult:
        turn_start = len(self._messages)
        self._messages.append({"role": "user", "content": text})
        tool_calls_made: list[dict[str, Any]] = []
        retries: list[dict[str, Any]] = []

        for _ in range(self._max_tool_rounds):
            response = _call_with_backoff(
                lambda: self._client.messages.create(
                    model=self._model,
                    system=self._system_blocks(),
                    tools=self._tools,
                    messages=[{k: v for k, v in m.items() if not k.startswith("_")} for m in self._messages],
                    max_tokens=512,
                ),
                max_retries=self._max_retries,
                retry_log=retries,
            )
            self._messages.append({"role": "assistant", "content": response.content})

            tool_use_blocks = [b for b in response.content if getattr(b, "type", None) == "tool_use"]
            if not tool_use_blocks:
                final_text = "".join(
                    getattr(b, "text", "") for b in response.content if getattr(b, "type", None) == "text"
                )
                self._turn_boundaries.append(turn_start)
                self._trim_older_turns()
                return DriverTurnResult(final_text=final_text, tool_calls_made=tool_calls_made, retries=retries)

            tool_result_content = []
            for block in tool_use_blocks:
                command = block.input.get("command", "")
                output = self._tool_executor(command)
                tool_calls_made.append({"command": command, "output": output})
                tool_result_content.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output[:20000],
                })
            self._messages.append({"role": "user", "content": tool_result_content})

        self._turn_boundaries.append(turn_start)
        self._trim_older_turns()
        return DriverTurnResult(final_text="[max_tool_rounds exceeded without final text reply]", tool_calls_made=tool_calls_made, retries=retries)


class OpenAIDriver:
    """Driver using the OpenAI Chat Completions API (function/tool calls)."""

    def __init__(self, *, api_key: str, model: str, system_prompt: str, tool_executor: ToolExecutor, max_tool_rounds: int = 10, max_retries: int = 4):
        import openai  # local import: optional dependency, only needed for this driver

        self._client = openai.OpenAI(api_key=api_key)
        self._model = model
        self._tool_executor = tool_executor
        self._max_tool_rounds = max_tool_rounds
        self._max_retries = max_retries
        self._messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        self._tools = [{
            "type": "function",
            "function": {
                "name": "run_bash",
                "description": BASH_TOOL_DESCRIPTION,
                "parameters": {
                    "type": "object",
                    "properties": {"command": {"type": "string"}},
                    "required": ["command"],
                },
            },
        }]

    def send_user_turn(self, text: str) -> DriverTurnResult:
        self._messages.append({"role": "user", "content": text})
        tool_calls_made: list[dict[str, Any]] = []
        retries: list[dict[str, Any]] = []

        for _ in range(self._max_tool_rounds):
            response = _call_with_backoff(
                lambda: self._client.chat.completions.create(
                    model=self._model,
                    messages=self._messages,
                    tools=self._tools,
                ),
                max_retries=self._max_retries,
                retry_log=retries,
            )
            message = response.choices[0].message
            self._messages.append(message.model_dump(exclude_none=True))

            if not message.tool_calls:
                return DriverTurnResult(final_text=message.content or "", tool_calls_made=tool_calls_made, retries=retries)

            for call in message.tool_calls:
                args = json.loads(call.function.arguments or "{}")
                command = args.get("command", "")
                output = self._tool_executor(command)
                tool_calls_made.append({"command": command, "output": output})
                self._messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": output[:20000],
                })

        return DriverTurnResult(final_text="[max_tool_rounds exceeded without final text reply]", tool_calls_made=tool_calls_made, retries=retries)


def build_driver(
    driver_spec: str, *, system_prompt: str, tool_executor: ToolExecutor, api_key: str, max_retries: int = 4
) -> ModelDriver:
    """driver_spec format: 'anthropic:claude-sonnet-5' or 'openai:gpt-...'."""
    provider, _, model = driver_spec.partition(":")
    if provider == "anthropic":
        return AnthropicDriver(api_key=api_key, model=model, system_prompt=system_prompt, tool_executor=tool_executor, max_retries=max_retries)
    if provider == "openai":
        return OpenAIDriver(api_key=api_key, model=model, system_prompt=system_prompt, tool_executor=tool_executor, max_retries=max_retries)
    raise ValueError(f"Unknown driver provider: {provider!r} (expected 'anthropic:<model>' or 'openai:<model>')")
