# agent-compact

Executable contracts for AI agents.

Prompt engineering is oral negotiation. agent-compact is the written
contract — definitions, precedents, evidence requirements, dispute
resolution, and constraints, version-controlled alongside your code.

## Why

You spend eight turns getting an AI to admit it hallucinates.
It restarts. It forgets everything. You start over.

If those admissions were contract clauses instead of chat
messages, not one would be lost. That is the difference between
oral negotiation and a written contract.

Agents work in natural language. Natural language is ambiguous.
Four thousand years of legal practice solved this: bind terms,
cite precedent, require evidence, define dispute resolution,
constrain power. agent-compact brings that structure to agent
workflows.

The constitution governs process, not content. It does not say
what to build — it says how to work.

## Quick Start

Create an `.agent/` directory in your project and copy in
`constitution.md`. Add subdirectories as needed:

```bash
mkdir -p .agent/contracts .agent/precedents .agent/evidence .agent/tools
cp path/to/agent-compact/constitution.md .agent/
cp path/to/agent-compact/.agent/tools/index.py .agent/tools/
```

```
.agent/
  constitution.md        <- how the agent works
  contracts/             <- task specs (Markdown + frontmatter)
  precedents/            <- accumulated decisions (YAML)
  evidence/              <- verification artifacts
  tools/                 <- governance scripts (INDEX generator, etc.)
```

Add one line to your system prompt or CLAUDE.md:

```
Check .agent/constitution.md before non-trivial work.
```

The constitution is a pointer, not the content. The agent reads
it from disk — like a judge who knows where to find the law,
not one who memorizes every statute.

## File Format

**Contracts**: Markdown + YAML frontmatter.
Frontmatter is the docket (machine-parseable metadata).
Body is the contract (natural language clauses).

```markdown
---
contract_id: audit-cli
version: 1
subject: src/main.rs
---
# Operation
Read-only audit for correctness findings.
```

**Precedents**: YAML with structured fields.

```yaml
id: context-is-ephemeral
holding: State in context window dies on restart or compaction
applies_when: designing agent memory or evaluating state persistence
origin: observed restart/compaction loss
tags: [memory, persistence, architecture]
status: active
supersedes: null
```

**Evidence**: Markdown + YAML frontmatter.
Pins reports to repo + commit, records scope status,
precedents checked, and findings with evidence type.

**Retrieval**: `INDEX.yaml` is a **generated artifact** — precedent
files are the source of truth. Generate or verify with:

```bash
python .agent/tools/index.py .agent/precedents          # generate
python .agent/tools/index.py .agent/precedents --check   # verify, exit 1 if stale
```

Manual edits to INDEX.yaml are forbidden. The generator copies
`id`, `holding`, `applies_when`, `tags`, `severity`, `status`,
`date`, `supersedes`, `superseded_by` from each precedent file
into one small index. Agent reads the index first, matches
against the current task, then loads only the matching precedent
files. Index first, full text second.

**Constitution**: seven articles.

| Article | Governs |
| ------- | ------- |
| 1. Contract Awareness | where to find and how to read contracts |
| 2. Precedent | check, cite, and record past decisions |
| 3. Evidence | claims need proof; match judge to evidence type |
| 4. Default Dispute Resolution | conflict priority, ambiguity, failure, scope |
| 5. Separation of Powers | agent does not judge its own work |
| 6. Amendment | how to change the constitution |
| 7. Constraints | what the agent must never do (Bill of Rights) |

## Progressive Disclosure

Simple tasks need only a minimal contract:

```markdown
---
contract_id: quick-fix
subject: cli.py
---
# Operation
Fix the Unicode crash on Windows.
```

Complex tasks add sections as needed:

```markdown
# On Ambiguity
# On Failure
# On Conflict
# Amendment
```

Do not add sections preemptively. The constitution provides
defaults (Article 4) for anything a contract does not specify.

## Design Principles

**Contracts are natural language with addressable bindings.**
Not YAML-as-language, not free-form chat. Structured natural
language — the same format humans used for four thousand years
of written law.

**The interpreter has understanding.** Agent contracts assume
an interpreting mind (LLM / judge). Clauses are written for
comprehension, not parsing.

**Separation of powers handles indistinguishable error.** The
agent is not your adversary. Its errors are — they exploit
verification gaps the same way an adversary would. Independent
verification exists because you cannot tell correct output
from incorrect output without it.

**Vague where precision would expire.** The constitution avoids
tool names, coding styles, and implementation details that
would make it expire with the next framework release.

## Files

```
constitution.md              the seven articles
schemas/
  contract.schema.yaml       contract format reference
  precedent.schema.yaml      precedent format reference
  evidence.schema.yaml       evidence format reference
examples/
  precedents/                example precedents (format reference)
    INDEX.yaml               generated index (do not edit manually)
    context-is-ephemeral.yaml
.agent/
  tools/
    index.py                 INDEX.yaml generator/checker
  hooks/                     lifecycle hooks (SessionStart, PostCompact, etc.)
  prompts/                   role briefings (executor, jury, preamble)
```

Your project accumulates its own precedents, contracts, and
evidence in `.agent/`. This repo is the framework — the
constitution and the schemas. Case law is local.

## Origin

Extracted from repeated agent audit sessions where corrections,
accepted risks, and evidence needed to survive beyond chat history.
