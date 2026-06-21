---
contract_id: audit-hooks-system
version: 2
parties:
  principal: human
  agent: claude
subject:
  targets:
    - .agent/hooks/
    - .agent/prompts/
  mode: audit
evidence:
  required:
    - each hook runs without error on a real .agent/ directory
    - each hook runs without error on an empty .agent/ directory
    - each hook runs without error on malformed input
    - hook messages accurately cite constitution articles
    - prompts/ content aligns with constitution text
    - no hook injects full source of truth (summaries and pointers only)
termination:
  done_when: all evidence items produced with deterministic verification
on_conflict:
  - safety constraints override all
---

# Operation

Audit the agent-compact hooks system (hooks/*.py and prompts/*.md)
against the constitution (constitution.md) for correctness,
completeness, and noise control.

Scope:
- hooks/session_start.py
- hooks/post_compact.py
- hooks/subagent_start.py
- hooks/pre_edit.py
- hooks/post_read.py
- hooks/on_stop.py
- prompts/preamble.md
- prompts/executor.md
- prompts/jury.md

# On Ambiguity

Infer conservatively. Mark with (inferred).

# On Failure

Report failure and stop. Do not debug unrelated issues.
Partial results are valid.
