import json
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal

from config import SYSTEM_PROMPT, TOOL_DEFINITIONS

CHAT_SYSTEM_PROMPT = (
    SYSTEM_PROMPT
    + "\n\nYou are now in a back-and-forth conversation with the user. "
    "Answer their questions directly and casually. Use your tools to look up "
    "specific messages or details whenever needed. Same tone — casual, like a friend, all lowercase."
)
from database import Database


# ------------------------------------------------------------------ context builder

def _build_context_message(db: Database) -> str:
    """
    Feed the AI a snapshot of what's in the database so it can reason
    immediately without fumbling through empty tool calls first.
    """
    total = db.get_message_count()
    senders = db.get_senders()
    recent = db.get_recent_messages(n=20)

    lines = []

    if total == 0:
        lines.append("There are no messages in the directory yet.")
        lines.append(
            "Generate a brief report noting there's nothing to report right now."
        )
        return "\n".join(lines)

    lines.append(
        f"There are {total} message(s) in the directory from "
        f"{len(senders)} sender(s): {', '.join(senders)}."
    )
    lines.append("")
    lines.append(f"Here are the {len(recent)} most recent message(s) — read them carefully:")
    lines.append("")

    for msg in recent:
        lines.append(
            f"  [ID {msg['id']}] {msg['date']} | From: {msg['sender']}\n"
            f"  {msg['content']}"
        )

    if total > len(recent):
        lines.append("")
        lines.append(
            f"  (showing latest {len(recent)} of {total} total — "
            f"use search_messages or get_raw_messages to retrieve older ones)"
        )

    lines.append("")
    lines.append(
        "Using the messages above (and any additional ones you fetch with tools), "
        "generate your casual, direct report now. "
        "If something significant happened — relationships, drama, plans — call it out. "
        "Keep it one or two sentences max."
    )

    return "\n".join(lines)


# ------------------------------------------------------------------ tool executor

def execute_tool(db: Database, name: str, args: dict) -> str:
    try:
        if name == "search_messages":
            rows = db.search_messages(
                sender=args.get("sender"),
                start_date=args.get("start_date"),
                end_date=args.get("end_date"),
                keywords=args.get("keywords"),
            )
            if not rows:
                return "No messages found matching those criteria."
            return json.dumps(rows, indent=2)

        elif name == "get_raw_messages":
            rows = db.get_raw_messages(
                message_ids=args.get("message_ids"),
                start_date=args.get("start_date"),
                end_date=args.get("end_date"),
            )
            if not rows:
                return "No messages found."
            return json.dumps(rows, indent=2)

        elif name == "get_senders":
            senders = db.get_senders()
            if not senders:
                return "No messages in the directory yet."
            return json.dumps(senders)

        elif name == "get_message_count":
            count = db.get_message_count(
                sender=args.get("sender"),
                start_date=args.get("start_date"),
                end_date=args.get("end_date"),
            )
            return str(count)

        else:
            return f"Unknown tool: {name}"
    except Exception as e:
        return f"Tool error: {e}"


# ------------------------------------------------------------------ provider helpers

def _anthropic_tools():
    return [
        {
            "name": t["name"],
            "description": t["description"],
            "input_schema": t["parameters"],
        }
        for t in TOOL_DEFINITIONS
    ]


def _openai_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"],
            },
        }
        for t in TOOL_DEFINITIONS
    ]


# ------------------------------------------------------------------ log helpers

def _fmt_args(args: dict) -> str:
    if not args:
        return ""
    parts = []
    for k, v in args.items():
        if v is None:
            continue
        if isinstance(v, list):
            parts.append(f"{k}=[{', '.join(str(x) for x in v)}]")
        else:
            parts.append(f'{k}="{v}"')
    return ", ".join(parts)


def _fmt_result(result: str) -> str:
    """Return a short human-readable summary of a tool result."""
    stripped = result.strip()
    if stripped.startswith("[") or stripped.startswith("{"):
        try:
            data = json.loads(stripped)
            if isinstance(data, list):
                return f"{len(data)} result(s)"
            if isinstance(data, dict):
                return "1 result"
        except Exception:
            pass
    if len(stripped) > 80:
        return stripped[:77] + "…"
    return stripped


# ------------------------------------------------------------------ provider runners

def _run_anthropic(db: Database, settings: dict, log_fn=None) -> str:
    import anthropic

    def log(msg):
        if log_fn:
            log_fn(msg)

    client = anthropic.Anthropic(api_key=settings["ai"]["anthropic_api_key"])
    model = settings["ai"].get("anthropic_model", "claude-opus-4-7")
    user_msg = _build_context_message(db)
    messages = [{"role": "user", "content": user_msg}]

    log("── scanning messages ──")

    for _ in range(15):
        resp = client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=_anthropic_tools(),
            messages=messages,
        )
        if resp.stop_reason == "end_turn":
            for block in resp.content:
                if hasattr(block, "text"):
                    log("── writing report ──")
                    return block.text
            return "No report generated."

        if resp.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": resp.content})
            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    log(f"→ {block.name}({_fmt_args(block.input)})")
                    result = execute_tool(db, block.name, block.input)
                    log(f"  ↳ {_fmt_result(result)}")
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": result}
                    )
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "Report generation stopped unexpectedly."


def _run_openai_compat(db: Database, api_key: str, base_url: Optional[str], model: str, log_fn=None) -> str:
    from openai import OpenAI

    def log(msg):
        if log_fn:
            log_fn(msg)

    kwargs = {"api_key": api_key or "not-needed"}
    if base_url:
        kwargs["base_url"] = base_url

    client = OpenAI(**kwargs)
    user_msg = _build_context_message(db)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
    tools = _openai_tools()

    log("── scanning messages ──")

    for _ in range(15):
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        choice = resp.choices[0]

        if choice.finish_reason == "stop":
            log("── writing report ──")
            return choice.message.content or "No report generated."

        if choice.finish_reason == "tool_calls":
            messages.append(choice.message)
            for tc in choice.message.tool_calls:
                args = json.loads(tc.function.arguments)
                log(f"→ {tc.function.name}({_fmt_args(args)})")
                result = execute_tool(db, tc.function.name, args)
                log(f"  ↳ {_fmt_result(result)}")
                messages.append(
                    {"role": "tool", "tool_call_id": tc.id, "content": result}
                )
        else:
            break

    return "Report generation stopped unexpectedly."


# ------------------------------------------------------------------ local model detection

def _detect_local_model(host: str, port: int, provider: str) -> str:
    import requests
    try:
        if provider == "ollama":
            r = requests.get(f"http://{host}:{port}/api/tags", timeout=3)
            models = r.json().get("models", [])
            if models:
                return models[0].get("name", "llama3")
        else:
            r = requests.get(f"http://{host}:{port}/v1/models", timeout=3)
            models = r.json().get("data", [])
            if models:
                return models[0].get("id", "local-model")
    except Exception:
        pass
    return "local-model"


# ------------------------------------------------------------------ public entry point

def generate_report(db: Database, settings: dict, log_fn=None) -> str:
    provider = settings["ai"].get("provider", "anthropic")

    if provider == "anthropic":
        if not settings["ai"].get("anthropic_api_key"):
            return "no anthropic api key configured — add one in Settings"
        return _run_anthropic(db, settings, log_fn=log_fn)

    elif provider == "openai":
        if not settings["ai"].get("openai_api_key"):
            return "no openai api key configured — add one in Settings"
        model = settings["ai"].get("openai_model", "gpt-4o")
        return _run_openai_compat(db, settings["ai"]["openai_api_key"], None, model, log_fn=log_fn)

    elif provider == "xai":
        if not settings["ai"].get("xai_api_key"):
            return "no xai api key configured — add one in Settings"
        model = settings["ai"].get("xai_model", "grok-3")
        return _run_openai_compat(db, settings["ai"]["xai_api_key"], "https://api.x.ai/v1", model, log_fn=log_fn)

    elif provider == "ollama":
        host = settings["ai"].get("ollama_host", "localhost")
        port = settings["ai"].get("ollama_port", 11434)
        model = settings["ai"].get("ollama_model") or _detect_local_model(host, port, "ollama")
        return _run_openai_compat(db, "ollama", f"http://{host}:{port}/v1", model, log_fn=log_fn)

    elif provider == "lm_studio":
        host = settings["ai"].get("lm_studio_host", "localhost")
        port = settings["ai"].get("lm_studio_port", 1234)
        model = settings["ai"].get("lm_studio_model") or _detect_local_model(host, port, "lm_studio")
        return _run_openai_compat(db, "lm-studio", f"http://{host}:{port}/v1", model, log_fn=log_fn)

    return "unknown provider selected"


# ------------------------------------------------------------------ chat turn runners

def _chat_anthropic(db: Database, settings: dict, history: list, user_message: str, log_fn=None) -> str:
    import anthropic

    def log(msg):
        if log_fn:
            log_fn(msg)

    client = anthropic.Anthropic(api_key=settings["ai"]["anthropic_api_key"])
    model = settings["ai"].get("anthropic_model", "claude-opus-4-7")

    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": user_message})

    log("── thinking ──")

    for _ in range(15):
        resp = client.messages.create(
            model=model,
            max_tokens=1024,
            system=CHAT_SYSTEM_PROMPT,
            tools=_anthropic_tools(),
            messages=messages,
        )
        if resp.stop_reason == "end_turn":
            for block in resp.content:
                if hasattr(block, "text"):
                    log("── done ──")
                    return block.text
            return ""

        if resp.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": resp.content})
            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    log(f"→ {block.name}({_fmt_args(block.input)})")
                    result = execute_tool(db, block.name, block.input)
                    log(f"  ↳ {_fmt_result(result)}")
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": result}
                    )
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "..."


def _chat_openai_compat(
    db: Database, api_key: str, base_url: Optional[str], model: str,
    history: list, user_message: str, log_fn=None
) -> str:
    from openai import OpenAI

    def log(msg):
        if log_fn:
            log_fn(msg)

    kwargs = {"api_key": api_key or "not-needed"}
    if base_url:
        kwargs["base_url"] = base_url

    client = OpenAI(**kwargs)
    messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
    messages += [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": user_message})

    log("── thinking ──")

    for _ in range(15):
        resp = client.chat.completions.create(
            model=model, messages=messages, tools=_openai_tools(), tool_choice="auto"
        )
        choice = resp.choices[0]

        if choice.finish_reason == "stop":
            log("── done ──")
            return choice.message.content or ""

        if choice.finish_reason == "tool_calls":
            messages.append(choice.message)
            for tc in choice.message.tool_calls:
                args = json.loads(tc.function.arguments)
                log(f"→ {tc.function.name}({_fmt_args(args)})")
                result = execute_tool(db, tc.function.name, args)
                log(f"  ↳ {_fmt_result(result)}")
                messages.append(
                    {"role": "tool", "tool_call_id": tc.id, "content": result}
                )
        else:
            break

    return "..."


def run_chat_turn(
    db: Database, settings: dict, history: list, user_message: str, log_fn=None
) -> str:
    provider = settings["ai"].get("provider", "anthropic")

    if provider == "anthropic":
        return _chat_anthropic(db, settings, history, user_message, log_fn)
    elif provider == "openai":
        model = settings["ai"].get("openai_model", "gpt-4o")
        return _chat_openai_compat(db, settings["ai"]["openai_api_key"], None, model, history, user_message, log_fn)
    elif provider == "xai":
        model = settings["ai"].get("xai_model", "grok-3")
        return _chat_openai_compat(db, settings["ai"]["xai_api_key"], "https://api.x.ai/v1", model, history, user_message, log_fn)
    elif provider == "ollama":
        host = settings["ai"].get("ollama_host", "localhost")
        port = settings["ai"].get("ollama_port", 11434)
        model = settings["ai"].get("ollama_model") or _detect_local_model(host, port, "ollama")
        return _chat_openai_compat(db, "ollama", f"http://{host}:{port}/v1", model, history, user_message, log_fn)
    elif provider == "lm_studio":
        host = settings["ai"].get("lm_studio_host", "localhost")
        port = settings["ai"].get("lm_studio_port", 1234)
        model = settings["ai"].get("lm_studio_model") or _detect_local_model(host, port, "lm_studio")
        return _chat_openai_compat(db, "lm-studio", f"http://{host}:{port}/v1", model, history, user_message, log_fn)

    return "unknown provider"


# ------------------------------------------------------------------ async worker

class ReportWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    log_update = pyqtSignal(str)   # emitted for each tool call / status line

    def __init__(self, db: Database, settings: dict):
        super().__init__()
        self._db = db
        self._settings = settings

    def run(self):
        try:
            report = generate_report(self._db, self._settings, log_fn=self.log_update.emit)
            self.finished.emit(report)
        except Exception as e:
            self.error.emit(str(e))


class ChatTurnWorker(QObject):
    finished = pyqtSignal(str)
    log_update = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, db: Database, settings: dict, history: list, user_message: str):
        super().__init__()
        self._db = db
        self._settings = settings
        self._history = history
        self._user_message = user_message

    def run(self):
        try:
            response = run_chat_turn(
                self._db, self._settings, self._history,
                self._user_message, log_fn=self.log_update.emit
            )
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))
