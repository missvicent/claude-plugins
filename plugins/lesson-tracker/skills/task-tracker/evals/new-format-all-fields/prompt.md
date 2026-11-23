---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

ok plan for the bakeoff lesson is done, make me the tracker. feature name framework-bakeoff, repo phase4-agents/04-framework-bakeoff, local code in agents/framework-bakeoff

1. claude writes the offline tests first (tests/test_bakeoff.py), done when `make test` fails only with NotImplementedError
2. i write run_langgraph(query, lookup) by hand, returns Result(answer: str, tool_calls: int). done when make test passes the langgraph tests
3. claude figures out how pydantic ai TestModel fills tool args, no idea yet how, it's a research thing. need a short written finding with the evidence
4. run all three on the local model qwen3.5:9b and record latency + cost, make bench
5. i write the verdict paragraph in README: which dimensions the test failed to separate, and one winner per row only where the gap is real
not sure yet if crewai runs on the local model or we need claude for it (costs money) — leave that open
