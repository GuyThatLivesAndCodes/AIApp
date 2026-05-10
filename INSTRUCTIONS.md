# AI App: Relationship & Life Monitoring Assistant

## 1. Introduction

This document outlines the design and operational specifications for an AI-powered assistant focused on monitoring personal relationships and life events. The assistant is designed to passively collect information, analyze it at scheduled intervals, and provide concise, personalized reports to the user.

## 2. Architecture Overview

### 2.1 Message Ingestion

Messages will be ingested into the system via a dedicated network port. The system will listen for incoming messages on **port 774**. Each message is expected to be in a structured format, including `sender`, `content`, and `date` fields.

Example message format:

```
sender:Liam
content:yo sarah broke up wit that football guy, u wanna shoot your shot yet
date:5/9/2026 5:19PM
```

### 2.2 Data Storage

Upon ingestion, messages will be stored in a persistent, searchable message directory. The storage mechanism should allow for efficient retrieval based on various criteria such as sender, date range, and keywords within the content.

### 2.3 AI Processing and Reporting

### 2.4 User Interface (UI) Specifications

The application's main panel will feature a clean, interactive design with a primary color scheme of **dark gray** and **blue**. The layout is structured as follows:

*   **Top Bar**: Contains the "Serve" button and the "Data" button.
    *   **Serve Button**: Located at the top-left. Its color indicates the server's status (e.g., blue for running, gray for off). Clicking it reveals a dropdown with two options:
        *   "Start" / "Stop": Toggles the message ingestion server. If the server is running, this option changes to "Stop".
        *   "Settings": Opens a dedicated settings page for configuring the ingestion port and other server-related parameters. This option should be grayed out when the server is running.
    *   **Data Button**: Located at the top-right, next to the "Serve" button. Clicking this opens a comprehensive view of all stored data, including messages, recent reports, and other relevant information.

*   **Central Panel**: The main interactive area.
    *   **Next Report Timer**: Prominently displayed in the middle, showing a countdown to the next scheduled AI report generation.
    *   **Report Now Button**: Positioned directly below the timer. Clicking this button forces an immediate report generation and resets the timer to a random interval between 20 and 40 minutes.

*   **Report Display Area**: Below the "Report Now" button.
    *   **Report Toggle**: The report area is closed by default. A clickable element (e.g., "Open Report") allows the user to expand it. When open, this element changes to "Close Report" to collapse the view.
    *   **AI Report Content**: Displays the latest AI-generated report when expanded.

*   **Bottom Bar**: Contains the "Settings" button.
    *   **Settings Button**: Located at the very bottom, opening the application's general settings page for AI model configuration, notification preferences, and other customizable options.

The UI should prioritize user experience, ensuring all elements are clearly visible, responsive, and intuitive to interact with.

The core AI component will operate on a scheduled basis, performing bi-hourly check-ins. During these check-ins, the AI will access the stored messages, analyze them using its available tools, and generate a report. Reports will be delivered to the user via a Windows notification.

## 3. AI System Prompt

The AI's system prompt is crucial for defining its persona, objectives, and reporting style. The AI should adopt a casual, direct, and slightly informal tone, mirroring the user's communication style as observed in the ingested messages. Its primary goal is to provide actionable insights or observations based on the collected data, without being overly verbose or formal.

```
[SYSTEM PROMPT START]

You are a personal AI assistant designed to monitor relationship and life updates. Your primary function is to observe incoming messages, store them, and then, at bi-hourly intervals, review these messages to provide concise, casual, and direct reports to the user. Your tone should be informal, like a close friend, and reflect the user's observed communication style. Avoid formality, jargon, or overly polite language. Get straight to the point.

Your goal is to identify significant social updates, relationship changes, or general life events from the messages and summarize them in a way that is immediately relevant and actionable for the user. Do not offer advice unless explicitly prompted by the user in a future interaction. Your reports should be brief, typically one to two sentences.

When generating a report, consider the context of previous messages and the potential implications for the user. Focus on key information that the user would find interesting or important, delivered with a hint of playful directness.

Example Report Style:

Input Message: "sender:Liam\ncontent:yo sarah broke up wit that football guy, u wanna shoot your shot yet\ndate:5/9/2026 5:19PM"

Generated Report: "report: so liam told u that sarah's free now, as in she broke up fr, if u wanna do something stupid nows the time"

[SYSTEM PROMPT END]
```

### 3.1 AI Model Configuration

The AI application will support multiple configurable AI model providers, allowing the user to select their preferred backend. The application settings will provide options for:

*   **Anthropic API Key**: Integration with Anthropic's models via API key.
*   **OpenAI API Key**: Integration with OpenAI's models via API key.
*   **xAI API Key**: Integration with xAI's models via API key.
*   **Ollama Local Server**: Connection to a local Ollama instance. The application will automatically detect and utilize a running model with tool-enabled capabilities on the specified port.
*   **LM Studio Local Server**: Connection to a local LM Studio instance. The application will automatically detect and utilize a running model with tool-enabled capabilities on the specified port.

Users will be able to switch between these providers within the application settings.

## 4. AI Tools and Capabilities

The AI will have access to a set of tools to interact with the message directory. These tools are designed to enable efficient retrieval and analysis of stored messages.

### 4.1 Available Tools

| Tool Name           | Description                                                                 | Parameters                                                                    |
| :------------------ | :-------------------------------------------------------------------------- | :---------------------------------------------------------------------------- |
| `search_messages`   | Search for messages based on various criteria.                              | `sender` (optional), `start_date` (optional), `end_date` (optional), `keywords` (optional) |
| `get_raw_messages`  | Retrieve the full content of messages within a specified range or by ID.    | `message_ids` (list of IDs) or `date_range` (start and end date)              |
| `get_senders`       | List all unique senders present in the message directory.                   | None                                                                          |
| `get_message_count` | Get the total number of messages or messages from a specific sender/date.   | `sender` (optional), `start_date` (optional), `end_date` (optional)           |

## 5. Operational Behavior

### 5.1 Scheduled Check-ins

The AI will perform check-ins randomly every two hours. This frequency ensures timely updates without overwhelming the user with constant notifications.

### 5.2 Report Generation

During a check-in, the AI will:
1.  Utilize its `search_messages` and `get_raw_messages` tools to identify new or significant information since the last report.
2.  Synthesize the findings into a concise report, adhering to the persona defined in the system prompt.
3.  Ensure the report is brief and directly addresses the key information.

### 5.3 Notification Delivery

Once a report is generated, the system will send a notification to the user's Windows application. The notification will simply state: "Report Ready for Review!" Clicking on the notification will open the application, displaying the full AI-generated report.

## 6. Future Enhancements (Out of Scope for Initial Release)

## 7. Implementation Mandate

All features and configurations detailed in this document, including all specified AI model providers, must be fully implemented and functional in the initial release of the application. There should be no missing features or placeholders that would require subsequent updates to become operational.

*   User-configurable reporting frequency.
*   More advanced sentiment analysis of messages.
*   Ability for the user to interact directly with the AI for specific queries.
*   Integration with other communication platforms.
