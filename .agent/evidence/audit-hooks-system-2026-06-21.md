---
contract_id: audit-hooks-system
version: 1
type: evidence
date: 2026-06-21
repo: https://github.com/rangersui/agent-compact
commit: 541dcf110c41d766c046ab509c850a00aef36696
commit_short: 541dcf1
commit_date: 2026-06-22T00:13:46+10:00
commit_message: add hooks, prompts, and runtime governance system
scope_status:
  hooks/session_start.py: audited
  hooks/post_compact.py: audited
  hooks/subagent_start.py: audited
  hooks/pre_edit.py: audited
  hooks/on_stop.py: audited
  prompts/preamble.md: audited
  prompts/executor.md: audited
  prompts/jury.md: audited
precedents_checked:
  - id: audit-pin-to-commit
    matched: yes — commit SHA included
runtime_hooks:
  SessionStart: .agent/hooks/session_start.py
  PostCompact: .agent/hooks/post_compact.py
  SubagentStart: .agent/hooks/subagent_start.py
  PreToolUse: .agent/hooks/pre_edit.py
  Stop: .agent/hooks/on_stop.py
runtime_prompts:
  preamble: .agent/prompts/preamble.md
  executor: .agent/prompts/executor.md
  jury: .agent/prompts/jury.md
---

# Execution Evidence: audit-hooks-system

## 1. Real directory test (evidence type: deterministic)

All 5 hooks ran against `agent-repl/.agent/` (7 precedents, 1 active contract, 2 evidence files):

| Hook | Exit | Output |
|------|------|--------|
| session_start.py | 0 | 601 chars — constitution summary, contracts, precedent count |
| post_compact.py | 0 | 812 chars — constitution, contracts, evidence list, evidence gap |
| subagent_start.py | 0 | 336 chars — key rules, contracts, precedent count |
| pre_edit.py | 0 | 0 chars (silent — no stdin in batch test; requires JSON on stdin) |
| on_stop.py | 0 | 225 chars — evidence gap warning for execution-standard |

## 2. Empty directory test (evidence type: deterministic)

All 5 hooks ran on a directory with no `.agent/`:

| Hook | Exit | Output |
|------|------|--------|
| session_start.py | 0 | 0 chars (silent) |
| post_compact.py | 0 | 0 chars (silent) |
| subagent_start.py | 0 | 0 chars (silent) |
| pre_edit.py | 0 | 0 chars (silent) |
| on_stop.py | 0 | 0 chars (silent) |

## 3. Malformed input test (evidence type: deterministic)

Malformed `.agent/` directory (broken frontmatter, no-frontmatter contract):

| Hook | Exit | Output |
|------|------|--------|
| session_start.py | 0 | 173 chars — degraded gracefully |
| post_compact.py | 0 | 317 chars — degraded gracefully |
| subagent_start.py | 0 | 293 chars — degraded gracefully |
| pre_edit.py | 0 | 0 chars (silent — no matching contract target in malformed dir) |
| on_stop.py | 0 | 219 chars — used filename as fallback contract_id |

pre_edit.py additional edge cases (stdin variations):

| Input | Exit | Output |
|-------|------|--------|
| empty stdin | 0 | 0 chars (silent) |
| malformed JSON | 0 | 0 chars (silent) |
| valid JSON, no file_path | 0 | 0 chars (silent) |
| valid JSON, non-target file | 0 | 0 chars (silent) |

## 4. Article citation accuracy (evidence type: deterministic)

Cross-reference of all Article citations in hooks against constitution.md:

| Hook citation | Constitution heading | Match |
|---------------|---------------------|-------|
| Article 2 = precedents | Article 2. Precedent | yes |
| Article 3 = evidence | Article 3. Evidence | yes |
| Article 4 = non-performance | Article 4. Default Dispute Resolution | yes |
| Article 5 = self-judgment | Article 5. Separation of Powers | yes |

grep `Article \d` across hooks/ — 7 occurrences, all verified correct.

## 5. Prompts alignment (evidence type: deterministic)

| Prompt | Constitution coverage |
|--------|----------------------|
| preamble.md | Art 3 (evidence), Art 4 (failure types), Art 5 (self-judgment), Art 2 (precedents), Art 7 (constraints) |
| executor.md | Art 1 (contract reading), Art 3 (evidence), Art 2 (precedents), Art 5 (self-judgment), precedent: audit-pin-to-commit |
| jury.md | Art 5 (independence), Art 3 (evidence types/severity) |

All prompts cover their role-relevant articles. executor.md correctly marks
"pin to commit" as precedent-sourced, not constitutional.

## 6. No full-text injection (evidence type: deterministic)

Both session_start.py and post_compact.py extract only `first_para`
(first paragraph of constitution after frontmatter strip) and append
pointer "Read .agent/constitution.md for full terms."

grep `first_para|split.*\n\n` confirms: 2 files, both use
`text.strip().split("\n\n")[0]` pattern.

subagent_start.py injects a 3-rule summary, not constitution text.
on_stop.py and pre_edit.py do not inject constitution content at all.

No hook copies full contract text, full precedent text, or full
constitution text into its systemMessage.

## Termination

Contract satisfied: all 6 evidence requirements produced with
deterministic verification. 3 rounds of independent jury review,
final round returned 0 findings. Evidence pinned to commit 541dcf1.
