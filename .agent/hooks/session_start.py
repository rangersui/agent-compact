"""SessionStart hook — inject .agent/ context at session open."""
import json, os, sys, glob

def main():
    agent_dir = os.path.join(os.getcwd(), ".agent")
    if not os.path.isdir(agent_dir):
        return  # no .agent/, nothing to inject

    parts = []

    # constitution summary (first paragraph only)
    const_path = os.path.join(agent_dir, "constitution.md")
    if os.path.isfile(const_path):
        with open(const_path, encoding="utf-8") as f:
            text = f.read()
        # strip frontmatter
        if text.startswith("---"):
            parts_split = text.split("---", 2)
            text = parts_split[2] if len(parts_split) > 2 else text
        first_para = text.strip().split("\n\n")[0].strip()
        parts.append(f"[Constitution] {first_para}")

    # active contracts
    contracts_dir = os.path.join(agent_dir, "contracts")
    if os.path.isdir(contracts_dir):
        active = []
        for f in sorted(glob.glob(os.path.join(contracts_dir, "*.md"))):
            name = os.path.basename(f).replace(".md", "")
            active.append(name)
        archived = []
        arch_dir = os.path.join(contracts_dir, "archived")
        if os.path.isdir(arch_dir):
            for f in sorted(glob.glob(os.path.join(arch_dir, "*.md"))):
                name = os.path.basename(f).replace(".md", "")
                archived.append(name)
        if active:
            parts.append(f"[Active contracts] {', '.join(active)}")
        if archived:
            parts.append(f"[Archived contracts] {', '.join(archived)}")

    # precedent count
    prec_dir = os.path.join(agent_dir, "precedents")
    if os.path.isdir(prec_dir):
        precs = [f for f in os.listdir(prec_dir)
                 if f.endswith((".yaml", ".yml")) and f != "INDEX.yaml"]
        if precs:
            parts.append(f"[Precedents] {len(precs)} entries — read INDEX.yaml before judgment calls")

    # evidence count
    ev_dir = os.path.join(agent_dir, "evidence")
    if os.path.isdir(ev_dir):
        evs = [f for f in os.listdir(ev_dir) if f.endswith(".md")]
        if evs:
            parts.append(f"[Evidence] {len(evs)} files on record")

    if parts:
        msg = "agent-compact active. " + " | ".join(parts)
        msg += " | Read .agent/constitution.md for full terms."
        json.dump({"systemMessage": msg}, sys.stdout)

if __name__ == "__main__":
    main()
