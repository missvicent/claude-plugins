---
type: tool-fact
topic: crewai
applies_to: [coding, tracker-build]
status: active
seen: 1
first_seen: 2026-11-10
last_seen: 2026-11-10
source: "[[2026-11-10-crewai-spike]]"
---
CrewAI needs Python 3.12: on 3.13+ it dies inside Chroma's Pydantic v1 shim (chroma_server_nofile).
**Why it matters:** pin the interpreter before installing, or lose an hour.
Seen in: [[2026-11-10-crewai-spike]]
