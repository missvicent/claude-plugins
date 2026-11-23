---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

our jira isnt connected in here so ill just paste the card. whats left on it? i want something i can download as pdf for standup

PROJ-42  Universal LLM client
Description: One provider-agnostic client in foundations/universal-client/src/client.py that normalizes OpenAI, Anthropic, Gemini, Ollama and MLX behind one interface.
Acceptance criteria:
- complete() returns plain text for every provider
- stream() yields text chunks
- call_tool() returns a normalized ToolCall
- extract() returns validated structured output
- unit tests cover each function
Status: In Progress
