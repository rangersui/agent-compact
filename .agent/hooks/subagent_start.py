"""SubagentStart hook — inject governance context into subagent sessions.

Subagents spawn with zero context. They don't get SessionStart.
This hook ensures every subagent knows it's operating under
agent-compact governance and where to find the rules.
"""
import json, os, sys, glob

def main():
    agent_dir = os.path.join(os.getcwd(), ".agent")
    if not os.path.isdir(agent_dir):
        return

    parts = []

    # constitution one-liner
    const_path = os.path.join(agent_dir, "constitution.md")
    if os.path.isfile(const_path):
        parts.append(
            "You are under agent-compact governance. "
            "Key rules: check precedents before judgment calls (Article 2), "
            "evidence required for claims (Article 3), "
            "you do not judge your own work (Article 5), "
            "mark inferences with (inferred)."
        )

    # active contracts — subagent needs to know what's in play
    contracts_dir = os.path.join(agent_dir, "contracts")
    if os.path.isdir(contracts_dir):
        active = []
        for f in sorted(glob.glob(os.path.join(contracts_dir, "*.md"))):
            name = os.path.basename(f).replace(".md", "")
            active.append(name)
        if active:
            parts.append(f"Active contracts: {', '.join(active)}")

    # precedent count
    prec_dir = os.path.join(agent_dir, "precedents")
    if os.path.isdir(prec_dir):
        precs = [f for f in os.listdir(prec_dir)
                 if f.endswith((".yaml", ".yml")) and f != "INDEX.yaml"]
        if precs:
            parts.append(f"{len(precs)} precedents in .agent/precedents/")

    # role-specific prompts available
    prompts_dir = os.path.join(agent_dir, "prompts")
    if os.path.isdir(prompts_dir):
        available = [f.replace(".md", "") for f in os.listdir(prompts_dir) if f.endswith(".md")]
        if available:
            parts.append(f"Role briefings available: {', '.join(sorted(available))}")

    if parts:
        msg = "[agent-compact] " + " | ".join(parts)
        json.dump({"systemMessage": msg}, sys.stdout)

if __name__ == "__main__":
    main()
