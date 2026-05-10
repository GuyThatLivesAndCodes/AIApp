import json
import threading
from typing import Callable, Optional

from PyQt5.QtCore import QObject, pyqtSignal

from config import SYSTEM_PROMPT, TOOL_DEFINITIONS
from database import Database


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
        {"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}}
        for t in TOOL_DEFINITIONS
    ]


# ------------------------------------------------------------------ provider runners

def _run_anthropic(db: Database, settings: dict) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=settings["ai"]["anthropic_api_key"])
    model = settings["ai"].get("anthropic_model", "claude-opus-4-7")
    messages = [{"role": "user", "content": "Generate a report based on the latest messages."}]

    for _ in range(10):
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
                    return block.text
            return "No report generated."

        if resp.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": resp.content})
            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    result = execute_tool(db, block.name, block.input)
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": result}
                    )
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "Report generation stopped unexpectedly."


def _run_openai_compat(db: Database, api_key: str, base_url: Optional[str], model: str) -> str:
    from openai import OpenAI

    kwargs = {"api_key": api_key or "not-needed"}
    if base_url:
        kwargs["base_url"] = base_url

    client = OpenAI(**kwargs)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Generate a report based on the latest messages."},
    ]
    tools = _openai_tools()

    for _ in range(10):
        resp = client.chat.completions.create(model=model, messages=messages, tools=tools, tool_choice="auto")
        choice = resp.choices[0]

        if choice.finish_reason == "stop":
            return choice.message.content or "No report generated."

        if choice.finish_reason == "tool_calls":
            messages.append(choice.message)
            for tc in choice.message.tool_calls:
                args = json.loads(tc.function.arguments)
                result = execute_tool(db, tc.function.name, args)
                messages.append(
                    {"role": "tool", "tool_call_id": tc.id, "content": result}
                )
        else:
            break

    return "Report generation stopped unexpectedly."


def _detect_local_model(host: str, port: int, provider: str) -> str:
    """Auto-detect first available model on Ollama or LM Studio."""
    import requests
    try:
        if provider == "ollama":
            r = requests.get(f"http://{host}:{port}/api/tags", timeout=3)
            data = r.json()
            models = data.get("models", [])
            if models:
                return models[0].get("name", "llama3")
        else:
            r = requests.get(f"http://{host}:{port}/v1/models", timeout=3)
            data = r.json()
            models = data.get("data", [])
            if models:
                return models[0].get("id", "local-model")
    except Exception:
        pass
    return "local-model"


def generate_report(db: Database, settings: dict) -> str:
    provider = settings["ai"].get("provider", "anthropic")

    if provider == "anthropic":
        if not settings["ai"].get("anthropic_api_key"):
            return "report: no anthropic api key configured, add one in settings to get reports"
        return _run_anthropic(db, settings)

    elif provider == "openai":
        if not settings["ai"].get("openai_api_key"):
            return "report: no openai api key configured, add one in settings to get reports"
        model = settings["ai"].get("openai_model", "gpt-4o")
        return _run_openai_compat(db, settings["ai"]["openai_api_key"], None, model)

    elif provider == "xai":
        if not settings["ai"].get("xai_api_key"):
            return "report: no xai api key configured, add one in settings to get reports"
        model = settings["ai"].get("xai_model", "grok-3")
        return _run_openai_compat(db, settings["ai"]["xai_api_key"], "https://api.x.ai/v1", model)

    elif provider == "ollama":
        host = settings["ai"].get("ollama_host", "localhost")
        port = settings["ai"].get("ollama_port", 11434)
        model = settings["ai"].get("ollama_model") or _detect_local_model(host, port, "ollama")
        return _run_openai_compat(db, "ollama", f"http://{host}:{port}/v1", model)

    elif provider == "lm_studio":
        host = settings["ai"].get("lm_studio_host", "localhost")
        port = settings["ai"].get("lm_studio_port", 1234)
        model = settings["ai"].get("lm_studio_model") or _detect_local_model(host, port, "lm_studio")
        return _run_openai_compat(db, "lm-studio", f"http://{host}:{port}/v1", model)

    return "report: unknown provider selected"


# ------------------------------------------------------------------ async worker

class ReportWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, db: Database, settings: dict):
        super().__init__()
        self._db = db
        self._settings = settings

    def run(self):
        try:
            report = generate_report(self._db, self._settings)
            self.finished.emit(report)
        except Exception as e:
            self.error.emit(str(e))
