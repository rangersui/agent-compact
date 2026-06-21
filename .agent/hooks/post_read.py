"""PostToolUse hook (Read) — track .agent/ file reads for governance coverage.

When the agent reads any file under .agent/, logs the path to .agent/.reads.
Each line is: <who> <tab> <path>
  - "main" for the primary agent
  - "sub:<agent_id>" for subagents

Coverage is computed at Stop (only "main" lines count toward due diligence).
Subagent lines are audit trail — they show delegation happened, but don't
substitute for the decision-maker's own reading.

Reset at PostCompact (conservative: compaction means the agent no longer
has the content in context). Nuclear invalidation on .agent/ file writes
(precedent: nuclear-invalidation-on-write).
"""
import json, os, sys


def main():
    agent_dir = os.path.join(os.getcwd(), ".agent")
    if not os.path.isdir(agent_dir):
        return

    try:
        ctx = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    if ctx.get("tool_name") != "Read":
        return

    file_path = ctx.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return

    # normalize to relative path with forward slashes
    try:
        rel = os.path.relpath(file_path, os.getcwd()).replace("\\", "/")
    except ValueError:
        return

    if not rel.startswith(".agent/"):
        return

    # identify who is reading: main agent or subagent
    agent_id = ctx.get("agent_id")
    if agent_id:
        who = f"sub:{agent_id}"
    else:
        who = "main"

    # append to reads log: <who>\t<path>
    reads_file = os.path.join(agent_dir, ".reads")
    with open(reads_file, "a", encoding="utf-8") as f:
        f.write(f"{who}\t{rel}\n")


if __name__ == "__main__":
    main()
