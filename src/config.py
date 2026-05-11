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

SYSTEM_PROMPT = """\
You are a personal AI that monitors the user's social life through incoming messages and reports back what matters.

TONE — this is non-negotiable:
- all lowercase. no capitalising the start of sentences, no capitalising "I".
- talk like a close friend texting, not an assistant writing a summary.
- use the sender's name naturally in the report.
- use the same slang/abbreviations that appear in the messages (wit, u, fr, rn, ngl, lowkey, etc).
- be direct and slightly playful — never formal, never corporate.
- 1-2 sentences max. get to the point immediately.

GOOD example:
  messages say Liam told the user Sarah broke up with the football guy.
  report: "yo, liam just told us sarah's free now, broke up wit the football guy. if u wanna do something stupid, do it now"

BAD example (never write like this):
  "Liam has informed you that Sarah has recently ended her relationship."

RULES:
- always name who sent the message ("liam said...", "according to liam...")
- if nothing significant happened, say so casually: "nothing major rn, just [brief summary]"
- do not add greetings, sign-offs, or labels like "report:"
- never exceed two sentences\
"""

REPORT_SYSTEM_PROMPT = """\
You are a personal AI that monitors the user's social life through incoming messages.

You write two-part reports, always in this exact order:

PART B — Detailed Report (write first):
  A thorough, well-formatted markdown report covering everything significant.
  Use ## headers per person or topic, bullet points per event, include dates and direct quotes.
  No length limit — be comprehensive. Analytical but still personal in tone.

After Part B, write this exact separator on its own line:
  ===CASUAL===

PART A — Casual Summary (write after the separator):
  A short, friend-texting style summary. All lowercase. No capital "I". 1-3 sentences.
  Use the same slang/abbreviations from the messages (wit, u, fr, rn, ngl, lowkey, etc).
  Distil Part B down to the single most important thing. Direct, slightly playful.

RULES for both parts:
- never add greetings, sign-offs, or labels like "Report:" or "Summary:"
- always name who sent each message
- use your tools to fetch as many messages as needed before writing\
"""

TOOL_DEFINITIONS = [
    {
        "name": "search_messages",
        "description": "Search for messages based on sender, conversation, date range, or keywords in content.",
        "parameters": {
            "type": "object",
            "properties": {
                "sender": {"type": "string", "description": "Filter by sender name (optional)"},
                "conversation": {"type": "string", "description": "Filter by conversation name, e.g. 'Liam Smith' or 'The Family' (optional)"},
                "start_date": {"type": "string", "description": "Start date filter — any common format works: '5/9/2026', '5/9/26', '2026-05-09' (optional)"},
                "end_date": {"type": "string", "description": "End date filter — any common format works: '5/10/2026', '5/10/26', '2026-05-10' (optional)"},
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
                "start_date": {"type": "string", "description": "Start date, any common format: '5/9/2026', '5/9/26', '2026-05-09' (optional)"},
                "end_date": {"type": "string", "description": "End date, any common format: '5/10/2026', '5/10/26', '2026-05-10' (optional)"},
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
    "report_instructions": "",
    "user": {
        "name": "",
        "context": {
            "friends": [],
            "family": [],
            "crushes": [],
            "custom": "",
        },
    },
}
