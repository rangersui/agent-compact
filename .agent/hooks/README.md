# agent-compact hooks

Claude Code hooks that inject `.agent/` context automatically.

## Hooks

| Hook | Event | What it does |
|------|-------|-------------|
| `session_start.py` | SessionStart | Injects constitution summary, active contracts, precedent count |
| `post_compact.py` | PostCompact | Re-injects context after compaction — includes contract targets and evidence gaps |
| `subagent_start.py` | SubagentStart | Injects governance rules + active contracts into every subagent |
| `pre_edit.py` | PreToolUse (Edit\|Write) | Warns when editing a file covered by an active contract |
| `post_read.py` | PostToolUse (Read) | Tracks .agent/ file reads for governance coverage |
| `on_stop.py` | Stop | Reports evidence gaps + governance coverage |

`post_compact.py` and `subagent_start.py` are the most critical hooks.
Compaction wipes all prior injection. Subagents spawn with zero context.
Without these hooks, agents lose governance awareness mid-session.

## Prompts

The `prompts/` directory contains role-specific briefings for subagents:

| File | Role | When to use |
|------|------|-------------|
| `preamble.md` | Any subagent | Minimal governance awareness — include in every subagent prompt |
| `executor.md` | Contract executor | Subagent executing a contract — scope, evidence, commit pinning |
| `jury.md` | Independent reviewer | Article 5 jury — verify claims, run commands, report findings |

**Usage**: read the prompt file and include it in the Agent tool's prompt field:

```
Read .agent/prompts/executor.md, then spawn:

Agent({
  prompt: "[contents of executor.md]\n\nContract: ...\nTask: ..."
})
```

The `subagent_start.py` hook provides a lightweight reminder, but for
full role briefing, include the appropriate prompt file in the Agent call.

## Install

Add to your project's `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .agent/hooks/session_start.py"
          }
        ]
      }
    ],
    "PostCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .agent/hooks/post_compact.py"
          }
        ]
      }
    ],
    "SubagentStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .agent/hooks/subagent_start.py"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python .agent/hooks/pre_edit.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Read",
        "hooks": [
          {
            "type": "command",
            "command": "python .agent/hooks/post_read.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .agent/hooks/on_stop.py"
          }
        ]
      }
    ]
  }
}
```

Then symlink or copy the `.agent/` subdirectories into your project:

```bash
# symlink (recommended — stays in sync)
ln -s /path/to/agent-compact/.agent/hooks .agent/hooks
ln -s /path/to/agent-compact/.agent/prompts .agent/prompts

# or copy
cp -r /path/to/agent-compact/.agent/hooks .agent/hooks
cp -r /path/to/agent-compact/.agent/prompts .agent/prompts
```

## Defense in depth

Three layers ensure governance survives context loss:

```
Layer 1: CLAUDE.md          — always in context, main + subagent
Layer 2: hooks              — auto-inject at lifecycle boundaries
Layer 3: prompts/           — role-specific briefings in Agent calls
```

CLAUDE.md is the floor — add a line to your project's CLAUDE.md:

```markdown
This project uses agent-compact governance. Read .agent/constitution.md
before starting non-trivial work. Check .agent/contracts/ for active tasks.
```

Hooks fire at boundaries (start, compact, subagent, edit, stop).
Prompts are the full briefing for specific roles.
