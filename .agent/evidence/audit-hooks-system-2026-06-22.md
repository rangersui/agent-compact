---
contract_id: audit-hooks-system
version: 2
type: evidence
date: 2026-06-22
repo: https://github.com/rangersui/agent-compact
commit: 4051dc52687a6da324324c9d9e1a444b9972d4d9
commit_short: 4051dc5
commit_date: 2026-06-22T02:29:50+10:00
commit_message: add governance coverage tracking and nuclear invalidation
scope_status:
  hooks/session_start.py: audited
  hooks/post_compact.py: audited
  hooks/subagent_start.py: audited
  hooks/pre_edit.py: audited
  hooks/post_read.py: audited
  hooks/on_stop.py: audited
  prompts/preamble.md: audited
  prompts/executor.md: audited
  prompts/jury.md: audited
precedents_checked:
  - id: audit-pin-to-commit
    matched: yes — commit SHA included
  - id: nuclear-invalidation-on-write
    matched: yes — pre_edit.py clears .reads on .agent/ file write
  - id: subagent-reads-not-due-diligence
    matched: yes — on_stop.py filters to main-only reads for coverage
runtime_hooks:
  SessionStart: .agent/hooks/session_start.py
  PostCompact: .agent/hooks/post_compact.py
  SubagentStart: .agent/hooks/subagent_start.py
  PreToolUse: .agent/hooks/pre_edit.py
  PostToolUse: .agent/hooks/post_read.py
  Stop: .agent/hooks/on_stop.py
runtime_prompts:
  preamble: .agent/prompts/preamble.md
  executor: .agent/prompts/executor.md
  jury: .agent/prompts/jury.md
---

# Execution Evidence: audit-hooks-system v2

Changes from v1: added hooks/post_read.py (PostToolUse Read hook for
governance coverage tracking). Modified hooks/on_stop.py (governance
coverage reporting), hooks/post_compact.py (.reads reset on compaction),
hooks/pre_edit.py (nuclear invalidation on .agent/ writes).

## 1. Real directory test (evidence type: deterministic)

All 6 hooks ran against `agent-repl/.agent/` (7 precedents, 1 active
contract, 2 evidence files):

| Hook | Exit | Output |
|------|------|--------|
| session_start.py | 0 | 594 chars — constitution summary, active contract (execution-standard), archived contract, 6 precedents, 2 evidence files |
| post_compact.py | 0 | 800 chars — post-compaction context restore, constitution summary, contracts, evidence on record, flags EVIDENCE GAP for execution-standard |
| subagent_start.py | 0 | 334 chars — compact governance briefing: key articles (2,3,4,5), active contracts, precedent count |
| pre_edit.py | 0 | 0 chars (silent — edited path not in contract target). Side effect: nuclear invalidation deleted .reads (edit targeted .agent/ path) |
| post_read.py | 0 | 0 chars (silent — no stdout). Side effect: created .reads with `main\t.agent/constitution.md` |
| on_stop.py | 0 | 322 chars — flags 1 contract with no evidence (execution-standard), governance coverage 0/2, unread files listed |

Nuclear invalidation chain verified in-situ: pre_edit.py deleted .reads
when editing an .agent/ file, post_read.py recreated it on .agent/ read.

## 2. Empty directory test (evidence type: deterministic)

All 6 hooks ran on a directory with no `.agent/`:

| Hook | Exit | Output |
|------|------|--------|
| session_start.py | 0 | 0 chars (silent) |
| post_compact.py | 0 | 0 chars (silent) |
| subagent_start.py | 0 | 0 chars (silent) |
| pre_edit.py | 0 | 0 chars (silent) |
| post_read.py | 0 | 0 chars (silent) |
| on_stop.py | 0 | 0 chars (silent) |

## 3. Malformed input test (evidence type: deterministic)

Malformed `.agent/` directory (broken frontmatter with no closing `---`,
no-frontmatter contract with plain text only, empty constitution 0 bytes):

| Hook | Exit | Output |
|------|------|--------|
| session_start.py | 0 | degraded: empty `[Constitution]`, listed both contracts by filename |
| post_compact.py | 0 | degraded: extracted `contract_id: broken` despite missing `---`, used filename fallback for no-frontmatter, reported evidence gap |
| subagent_start.py | 0 | degraded: governance rules injected, both contracts listed |
| pre_edit.py | 0 | 0 chars (silent — no matching contract target in malformed dir) |
| post_read.py | 0 | 0 chars (silent — writes to .reads only) |
| on_stop.py | 0 | reported 2 contracts with no evidence, governance coverage 1/3 |

pre_edit.py stdin edge cases:

| Input | Exit | Output |
|-------|------|--------|
| empty stdin | 0 | 0 chars (JSONDecodeError caught) |
| malformed JSON ("not json") | 0 | 0 chars (JSONDecodeError caught) |
| valid JSON, no file_path | 0 | 0 chars (missing field, early return) |
| valid JSON, non-target file | 0 | 0 chars (no contract target match) |
| valid JSON, .agent/ target | 0 | nuclear invalidation triggered (deleted .reads) |

Resilience notes:
- Empty constitution: hooks produce empty `[Constitution]` text, no crash
- Missing `---` terminator: line-by-line `contract_id:` scan still works
- No frontmatter at all: filename used as fallback contract identifier
- JSONDecodeError/EOFError guard catches all malformed stdin

## 4. post_read.py edge cases (evidence type: deterministic)

stdin variations tested with subprocess + JSON piping:

| Input | Exit | .reads written | Who |
|-------|------|----------------|-----|
| empty stdin | 0 | no | — |
| malformed JSON | 0 | no | — |
| tool_name != "Read" | 0 | no | — |
| tool_name=Read, no file_path | 0 | no | — |
| tool_name=Read, non-.agent/ file | 0 | no | — |
| tool_name=Read, .agent/ file (no agent_id) | 0 | yes | main |
| tool_name=Read, .agent/ file (agent_id=sub-42) | 0 | yes | sub:sub-42 |

.reads file content verified:
```
main	.agent/constitution.md
sub:sub-42	.agent/constitution.md
```

Subagent identity tracking confirmed: main agent reads produce `main`
prefix, subagent reads produce `sub:{agent_id}` prefix.

## 4b. on_stop.py coverage scenarios (evidence type: deterministic)

| Scenario | Evidence | .reads | Output |
|----------|----------|--------|--------|
| No .reads, no evidence | missing | absent | evidence gap + coverage 0/N |
| Main reads constitution only | missing | partial | evidence gap + coverage 1/2 |
| Main reads all files | missing | full | evidence gap only (coverage satisfied) |
| Subagent reads all files | missing | sub-only | evidence gap + coverage 0/2 + delegation warning |
| Main reads all + evidence present | present | full | silence (no output) |
| Sub reads all + evidence present | present | sub-only | coverage 0/2 + delegation warning (no evidence gap) |

Key behavior verified:
- Full main coverage + evidence = no warnings (clean exit)
- Subagent-only reads produce delegation warning with "does not count"
- Evidence satisfaction and coverage are independent checks

## 5. Governance coverage chain (evidence type: deterministic)

The `.reads` lifecycle spans 4 hooks forming a coherent state machine:

| Hook | Role | .reads operation |
|------|------|------------------|
| post_read.py | Writer | append `{who}\t{path}` |
| pre_edit.py | Invalidator | delete on .agent/ write |
| post_compact.py | Resetter | delete on compaction |
| on_stop.py | Reporter | read, compute coverage, report |

Format alignment verified:
- post_read.py writes: `{who}\t{rel}\n` (who = "main" or "sub:{id}")
- on_stop.py reads: splits on `\t`, filters `who == "main"` for coverage
- Legacy compat: lines without `\t` treated as main

Expected set construction:
- `.agent/constitution.md` (always)
- `.agent/contracts/*.md` (per active contract)

Precedent references verified:
- pre_edit.py comment cites `nuclear-invalidation-on-write`
- post_read.py docstring cites both precedents
- on_stop.py delegation warning matches `subagent-reads-not-due-diligence`

## 6. Article citation accuracy (evidence type: deterministic)

Cross-reference of all Article citations in hooks against constitution.md:

| Hook citation | Constitution heading | Match |
|---------------|---------------------|-------|
| Article 2 = precedents | Article 2. Precedent | yes |
| Article 3 = evidence | Article 3. Evidence | yes |
| Article 4 = non-performance | Article 4. Default Dispute Resolution | yes |
| Article 5 = self-judgment | Article 5. Separation of Powers | yes |

grep `Article \d` across hooks/ — 7 occurrences, all verified correct.
post_read.py has no Article citations (correct — tracking mechanism,
not governance message).

## 7. Prompts alignment (evidence type: deterministic)

Unchanged from v1. All 3 prompts cover their role-relevant articles:

| Prompt | Constitution coverage |
|--------|----------------------|
| preamble.md | Art 3 (evidence), Art 4 (failure types), Art 5 (self-judgment), Art 2 (precedents), Art 7 (constraints) |
| executor.md | Art 1 (contract reading), Art 3 (evidence), Art 2 (precedents), Art 5 (self-judgment), precedent: audit-pin-to-commit |
| jury.md | Art 5 (independence), Art 3 (evidence types/severity) |

## 8. No full-text injection (evidence type: deterministic)

session_start.py and post_compact.py use `text.strip().split("\n\n")[0]`
for first-paragraph extraction. subagent_start.py injects 3-rule summary.
on_stop.py and pre_edit.py do not inject constitution content.
post_read.py does not produce any systemMessage output — it only
writes to `.reads`.

No hook copies full contract, precedent, or constitution text.

## Termination

Contract v2 satisfied: all evidence requirements produced with
deterministic verification. Evidence pinned to commit 4051dc5.
