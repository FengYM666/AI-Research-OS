#!/usr/bin/env python3
"""aris-zhipu — the `codex` MCP server, implemented over the Zhipu (BigModel) API.

ARIS skills call `mcp__codex__codex` / `mcp__codex__codex-reply` (the contract
the removed `codex mcp-server` spoke). This bridge speaks that same contract —
tools named `codex` and `codex-reply`, results shaped `{threadId, content}` —
and runs each call against the Zhipu GLM API, so the skills do not change.

Designed for a GLM Coding Plan key: the Anthropic-compatible endpoint
(https://open.bigmodel.cn/api/anthropic/v1/messages) is where Coding Plan
quota lives; the /api/paas/v4 endpoint rejects plan keys with code 1113.

Environment:
    ZHIPU_API_KEY          - required. BigModel API key (id.secret format).
    ZHIPU_BASE_URL         - default: https://open.bigmodel.cn/api/anthropic
    ZHIPU_MODEL            - default: glm-5.3 (used for all reviewer tiers)
    ZHIPU_REVIEWER_SYSTEM  - optional system prompt override
    ZHIPU_MAX_TOKENS       - default: 10240
    ZHIPU_TIMEOUT_SEC      - HTTP timeout per call, default: 900
    ARIS_ZHIPU_DEBUG       - set to a file path to enable debug logging

Model routing: any model name starting with "glm-" (case-insensitive) is
passed through; anything else (gpt-*, o3, ...) maps to ZHIPU_MODEL. ARIS's
capability-fallback chain keys on error wording, so unknown-model errors from
upstream are surfaced verbatim.

Reasoning effort: config.model_reasoning_effort in {ultra, max, xhigh, high}
enables extended thinking (budget scaled by tier); lower tiers send no
thinking field. If the endpoint rejects the thinking field entirely, the call
is retried once without it.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
import traceback
import urllib.error
import urllib.request
import uuid
from pathlib import Path

SERVER_NAME = "aris-zhipu"
SERVER_VERSION = "1.0.0"

API_KEY = os.environ.get("ZHIPU_API_KEY", "")
BASE_URL = os.environ.get("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/anthropic").rstrip("/")
DEFAULT_MODEL = os.environ.get("ZHIPU_MODEL", "glm-5.3")
REVIEWER_SYSTEM = os.environ.get(
    "ZHIPU_REVIEWER_SYSTEM",
    "You are an independent, rigorous research reviewer in the ARIS workflow. "
    "You did not write the work you are reviewing. Critique honestly and "
    "concretely: identify real flaws, cite specifics from the material, and "
    "assign scores/verdicts only as instructed by the prompt. Do not soften "
    "findings to be polite; do not invent findings to seem thorough.",
)
MAX_TOKENS = int(os.environ.get("ZHIPU_MAX_TOKENS", "10240"))
HTTP_TIMEOUT = float(os.environ.get("ZHIPU_TIMEOUT_SEC", "900"))

STATE_DIR = Path(os.environ.get("ARIS_ZHIPU_STATE_DIR", str(Path.home() / ".aris-zhipu")))
THREADS_DIR = STATE_DIR / "threads"

DEBUG_LOG = os.environ.get("ARIS_ZHIPU_DEBUG", "")

_stdout_lock = threading.Lock()
_use_ndjson = False  # set once from the first incoming frame


def debug_log(message: str) -> None:
    if not DEBUG_LOG:
        return
    try:
        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: {message}\n")
    except Exception:
        pass


# ─── MCP stdio framing ───────────────────────────────────────────────────────

def _configure_stdio_for_mcp() -> None:
    sys.stdout = os.fdopen(sys.stdout.fileno(), "wb", buffering=0)
    sys.stdin = os.fdopen(sys.stdin.fileno(), "rb", buffering=0)


def send_message(payload: dict) -> None:
    data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    if _use_ndjson:
        frame = data + b"\n"
    else:
        frame = f"Content-Length: {len(data)}\r\n\r\n".encode("ascii") + data
    with _stdout_lock:
        sys.stdout.write(frame)
        sys.stdout.flush()


def read_message():
    """Read one JSON-RPC frame. Accepts NDJSON or Content-Length framing.

    The framing mode is decided by the first frame and used for replies.
    """
    global _use_ndjson
    line = sys.stdin.readline()
    if not line:
        return None
    stripped = line.strip()
    if not stripped:
        return None
    if stripped.startswith(b"{"):
        _use_ndjson = True
        try:
            return json.loads(stripped.decode("utf-8"))
        except json.JSONDecodeError:
            return None
    # Content-Length framing
    try:
        length = int(stripped.split(b":", 1)[1].strip())
    except (IndexError, ValueError):
        return None
    sys.stdin.readline()  # blank line after headers
    body = sys.stdin.read(length)
    try:
        return json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return None


# ─── thread persistence ──────────────────────────────────────────────────────

def _load_thread(thread_id: str):
    path = THREADS_DIR / f"{thread_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_thread(thread_id: str, thread: dict) -> None:
    THREADS_DIR.mkdir(parents=True, exist_ok=True)
    path = THREADS_DIR / f"{thread_id}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(thread, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)


# ─── Zhipu API call (Anthropic Messages protocol) ────────────────────────────

_THINKING_BUDGETS = {"ultra": 16000, "max": 16000, "xhigh": 10000, "high": 8000}


def _resolve_model(requested):
    if requested and str(requested).lower().startswith("glm-"):
        return str(requested)
    if requested:
        debug_log(f"model '{requested}' not a glm-* name -> routing to {DEFAULT_MODEL}")
    return DEFAULT_MODEL


def _call_zhipu(messages, model, thinking_budget):
    """POST /v1/messages. Returns (text, error). Retries once without
    thinking when the endpoint rejects the thinking field."""
    url = f"{BASE_URL}/v1/messages"
    payload = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "system": REVIEWER_SYSTEM,
        "messages": messages,
    }
    if thinking_budget:
        payload["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}

    def _post(pl):
        body = json.dumps(pl, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": API_KEY,
                "Authorization": f"Bearer {API_KEY}",
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            return json.load(resp)

    try:
        data = _post(payload)
    except urllib.error.HTTPError as e:
        err_text = e.read().decode("utf-8", "ignore")[:800]
        if thinking_budget and e.code == 400 and "thinking" in err_text.lower():
            debug_log("thinking field rejected; retrying without it")
            payload.pop("thinking", None)
            try:
                data = _post(payload)
            except urllib.error.HTTPError as e2:
                return None, f"HTTP {e2.code}: {e2.read().decode('utf-8', 'ignore')[:800]}"
            except Exception as e2:
                return None, f"{type(e2).__name__}: {e2}"
        else:
            return None, f"HTTP {e.code}: {err_text}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

    blocks = data.get("content") or []
    text = "".join(b.get("text", "") for b in blocks if isinstance(b, dict) and b.get("type") == "text")
    if not text:
        # Some endpoints return {"content":[{"type":"text","text":...}]} only;
        # others may put everything in a single string block. Be lenient.
        text = "".join(str(b.get("text", "")) for b in blocks if isinstance(b, dict))
    return text, None


# ─── tool handlers ───────────────────────────────────────────────────────────

def _tool_result_text(payload: dict) -> dict:
    return {
        "content": [
            {"type": "text", "text": json.dumps(payload, ensure_ascii=False)}
        ]
    }


def _tool_error(message: str) -> dict:
    return {
        "content": [{"type": "text", "text": message}],
        "isError": True,
    }


def handle_codex(arguments: dict):
    prompt = arguments.get("prompt")
    if not prompt or not str(prompt).strip():
        return _tool_error("codex: 'prompt' is required")
    model = _resolve_model(arguments.get("model"))
    config = arguments.get("config") or {}
    effort = str(config.get("model_reasoning_effort", "")).lower()
    budget = _THINKING_BUDGETS.get(effort)
    debug_log(f"codex call: model={model} effort={effort or 'default'} thinking_budget={budget}")

    messages = [{"role": "user", "content": str(prompt)}]
    text, err = _call_zhipu(messages, model, budget)
    if err:
        return _tool_error(f"codex: reviewer backend error — {err}")

    thread_id = uuid.uuid4().hex[:16]
    _save_thread(thread_id, {"model": model, "messages": messages + [{"role": "assistant", "content": text}]})
    return _tool_result_text({"threadId": thread_id, "content": text})


def handle_codex_reply(arguments: dict):
    thread_id = str(arguments.get("threadId") or "")
    message = arguments.get("message")
    if not thread_id or not message:
        return _tool_error("codex-reply: 'threadId' and 'message' are required")
    thread = _load_thread(thread_id)
    if thread is None:
        return _tool_error(f"codex-reply: unknown threadId {thread_id}")
    messages = list(thread.get("messages", []))
    messages.append({"role": "user", "content": str(message)})

    model = _resolve_model(arguments.get("model") or thread.get("model"))
    config = arguments.get("config") or {}
    effort = str(config.get("model_reasoning_effort", "")).lower()
    budget = _THINKING_BUDGETS.get(effort)
    debug_log(f"codex-reply call: thread={thread_id} model={model} effort={effort or 'inherit'}")

    text, err = _call_zhipu(messages, model, budget)
    if err:
        return _tool_error(f"codex-reply: reviewer backend error — {err}")

    _save_thread(thread_id, {"model": model, "messages": messages + [{"role": "assistant", "content": text}]})
    return _tool_result_text({"threadId": thread_id, "content": text})


# ─── MCP protocol ────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "codex",
        "description": (
            "Send a prompt to the independent ARIS reviewer (Zhipu GLM backend) "
            "and get a fresh review. Returns JSON {threadId, content}. Pass "
            "config={\"model_reasoning_effort\": \"xhigh\"|\"ultra\"} to raise "
            "reasoning depth. sandbox/cwd are accepted and ignored (prompt-only review)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "The review prompt (full context; the reviewer sees only this)."},
                "model": {"type": "string", "description": "Reviewer model; glm-* passes through, anything else routes to the default GLM model."},
                "config": {"type": "object", "description": "e.g. {\"model_reasoning_effort\": \"xhigh\"}"},
                "sandbox": {"type": "string", "description": "Accepted for contract compatibility; ignored."},
                "cwd": {"type": "string", "description": "Accepted for contract compatibility; ignored."},
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "codex-reply",
        "description": (
            "Continue an existing reviewer thread with a follow-up message. "
            "Keeps the thread's model. Returns JSON {threadId, content}."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "threadId": {"type": "string"},
                "message": {"type": "string"},
                "model": {"type": "string", "description": "Override; defaults to the thread's model."},
                "config": {"type": "object"},
            },
            "required": ["threadId", "message"],
        },
    },
]


def handle_request(req: dict):
    method = req.get("method", "")
    req_id = req.get("id")
    is_notification = req_id is None and method.startswith("notifications/")

    if method == "initialize":
        send_message({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": req.get("params", {}).get("protocolVersion", "2025-03-26"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        })
    elif method == "notifications/initialized":
        pass
    elif method == "ping":
        send_message({"jsonrpc": "2.0", "id": req_id, "result": {}})
    elif method == "tools/list":
        send_message({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})
    elif method == "tools/call":
        params = req.get("params", {})
        name = params.get("name", "")
        arguments = params.get("arguments", {}) or {}
        try:
            if name == "codex":
                result = handle_codex(arguments)
            elif name == "codex-reply":
                result = handle_codex_reply(arguments)
            else:
                result = _tool_error(f"unknown tool: {name}")
        except Exception as e:
            debug_log("handler exception: " + traceback.format_exc())
            result = _tool_error(f"{type(e).__name__}: {e}")
        send_message({"jsonrpc": "2.0", "id": req_id, "result": result})
    else:
        if not is_notification and req_id is not None:
            send_message({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"method not found: {method}"}})


def main() -> int:
    _configure_stdio_for_mcp()
    if not API_KEY:
        # Fail loudly at startup so a misregistered server is visible in host logs.
        debug_log("FATAL: ZHIPU_API_KEY not set")
    debug_log(f"=== {SERVER_NAME} starting; base={BASE_URL} model={DEFAULT_MODEL} key_set={bool(API_KEY)} ===")
    while True:
        try:
            req = read_message()
        except Exception:
            debug_log("read error: " + traceback.format_exc())
            break
        if req is None:
            break
        try:
            handle_request(req)
        except Exception:
            debug_log("handle error: " + traceback.format_exc())
    return 0


if __name__ == "__main__":
    sys.exit(main())
