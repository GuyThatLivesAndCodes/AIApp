from pathlib import Path

APP_NAME = "AIApp"
APP_VERSION = "1.0.0"

DATA_DIR = Path.home() / "AIApp"
DB_PATH = DATA_DIR / "messages.db"
SETTINGS_PATH = DATA_DIR / "settings.json"

DEFAULT_SERVER_PORT = 774
REPORT_INTERVAL_NORMAL = 7200       # 2 hours in seconds
REPORT_INTERVAL_MANUAL_MIN = 1200   # 20 minutes
REPORT_INTERVAL_MANUAL_MAX = 2400   # 40 minutes

SYSTEM_PROMPT = (
    "You are a personal AI assistant designed to monitor relationship and life updates. "
    "Your primary function is to observe incoming messages, store them, and then, at bi-hourly intervals, "
    "review these messages to provide concise, casual, and direct reports to the user. "
    "Your tone should be informal, like a close friend, and reflect the user's observed communication style. "
    "Avoid formality, jargon, or overly polite language. Get straight to the point.\n\n"
    "Your goal is to identify significant social updates, relationship changes, or general life events "
    "from the messages and summarize them in a way that is immediately relevant and actionable for the user. "
    "Do not offer advice unless explicitly prompted. Your reports should be brief, typically one to two sentences.\n\n"
    "When generating a report, consider the context of previous messages and the potential implications for the user. "
    "Focus on key information that the user would find interesting or important, delivered with a hint of playful directness."
)

TOOL_DEFINITIONS = [
    {
        "name": "search_messages",
        "description": "Search for messages based on sender, date range, or keywords in content.",
        "parameters": {
            "type": "object",
            "properties": {
                "sender": {"type": "string", "description": "Filter by sender name (optional)"},
                "start_date": {"type": "string", "description": "Start date filter e.g. '5/9/2026' (optional)"},
                "end_date": {"type": "string", "description": "End date filter e.g. '5/10/2026' (optional)"},
                "keywords": {"type": "string", "description": "Keywords to search in message content (optional)"},
            },
        },
    },
    {
        "name": "get_raw_messages",
        "description": "Retrieve full content of messages by ID list or date range.",
        "parameters": {
            "type": "object",
            "properties": {
                "message_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of message IDs to retrieve",
                },
                "start_date": {"type": "string", "description": "Start date for range"},
                "end_date": {"type": "string", "description": "End date for range"},
            },
        },
    },
    {
        "name": "get_senders",
        "description": "List all unique senders present in the message directory.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_message_count",
        "description": "Get the total number of messages, optionally filtered by sender or date.",
        "parameters": {
            "type": "object",
            "properties": {
                "sender": {"type": "string", "description": "Filter by sender (optional)"},
                "start_date": {"type": "string", "description": "Start date (optional)"},
                "end_date": {"type": "string", "description": "End date (optional)"},
            },
        },
    },
]

DEFAULT_SETTINGS = {
    "server": {
        "port": DEFAULT_SERVER_PORT,
    },
    "ai": {
        "provider": "anthropic",
        "anthropic_api_key": "",
        "anthropic_model": "claude-opus-4-7",
        "openai_api_key": "",
        "openai_model": "gpt-4o",
        "xai_api_key": "",
        "xai_model": "grok-3",
        "ollama_host": "localhost",
        "ollama_port": 11434,
        "ollama_model": "",
        "lm_studio_host": "localhost",
        "lm_studio_port": 1234,
        "lm_studio_model": "",
    },
    "notifications": {
        "enabled": True,
    },
}
