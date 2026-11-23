---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

make the tracker for the bakeoff lesson. feature framework-bakeoff, vault project projects/gen-ai-engineer. tasks: 1. claude sets up agents/framework-bakeoff and installs langgraph, pydantic-ai and crewai (uv add), done when imports work. 2. i write run_crewai(query, lookup) by hand returning Result(answer, tool_calls). 3. claude runs the live bench (local model), make bench

Input files: vault/projects/gen-ai-engineer/insights/crewai-needs-py312.md, vault/projects/gen-ai-engineer/insights/pydantic-ai-uses-v1-api.md, vault/projects/gen-ai-engineer/insights/rag-chunk-overlap.md
