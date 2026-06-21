"""PreToolUse hook (Edit|Write) — warn only when editing a contract target.

Noise control: only fires when the edited file matches a contract's
`target:` or `targets:` list in frontmatter. Does NOT scan the full
contract body for path mentions.

Supports both formats:
  target: src/main.py          (single)
  targets:
    - .agent/hooks/            (list)
    - .agent/prompts/
"""
import json, os, sys, glob

def main():
    agent_dir = os.path.join(os.getcwd(), ".agent")
    if not os.path.isdir(agent_dir):
        return

    # read hook input from stdin
    try:
        ctx = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_input = ctx.get("tool_input", {})
    target = tool_input.get("file_path", "")
    if not target:
        return

    # normalize to relative path with forward slashes
    try:
        target_rel = os.path.relpath(target, os.getcwd()).replace("\\", "/")
    except ValueError:
        return

    # scan active contracts — match target: or targets: in frontmatter
    contracts_dir = os.path.join(agent_dir, "contracts")
    if not os.path.isdir(contracts_dir):
        return

    matching = []
    for f in sorted(glob.glob(os.path.join(contracts_dir, "*.md"))):
        with open(f, encoding="utf-8") as fh:
            text = fh.read()

        # parse frontmatter for target/targets/mode
        contract_targets = []
        mode = "edit"
        in_frontmatter = False
        reading_targets = False
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    break
            if not in_frontmatter:
                continue

            # single target:
            if stripped.startswith("target:") and not stripped.startswith("targets:"):
                val = stripped.split(":", 1)[1].strip()
                if val:
                    contract_targets.append(val)
                reading_targets = False
            # targets: (list header — may be nested under subject:)
            elif stripped.startswith("targets:"):
                reading_targets = True
            # list item under targets:
            elif reading_targets and stripped.startswith("- "):
                contract_targets.append(stripped[2:].strip())
            # mode: (may be nested under subject:)
            elif stripped.startswith("mode:"):
                mode = stripped.split(":", 1)[1].strip()
                reading_targets = False
            # a non-indented, non-list line ends targets reading
            elif reading_targets and not stripped.startswith("- "):
                reading_targets = False

        if not contract_targets:
            continue

        # check if edited file matches any contract target
        for ct in contract_targets:
            if target_rel == ct or target_rel.startswith(ct.rstrip("/") + "/"):
                name = os.path.basename(f).replace(".md", "")
                matching.append((name, mode))
                break

    if matching:
        lines = []
        for name, mode in matching:
            lines.append(f"  - {name} (mode: {mode})")
        msg = (
            f"[agent-compact] File {target_rel} is covered by contract(s):\n"
            + "\n".join(lines)
            + "\nEnsure edits comply with contract terms and evidence will be produced."
        )
        json.dump({"systemMessage": msg}, sys.stdout)

if __name__ == "__main__":
    main()
