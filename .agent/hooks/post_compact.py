"""PostCompact hook — re-inject .agent/ context after conversation compaction.

Compaction wipes the SessionStart injection. Without this hook, the agent
loses all awareness of constitution, contracts, and precedents mid-session.
This is the most critical hook — a compacted agent executing a contract
without legal consciousness is the silent non-performance case from Article 4.
"""
import json, os, sys, glob

def main():
    agent_dir = os.path.join(os.getcwd(), ".agent")
    if not os.path.isdir(agent_dir):
        return

    parts = []

    # constitution — inject more than session_start since agent lost all context
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

    # active contracts — include subject/target so agent knows what it was doing
    contracts_dir = os.path.join(agent_dir, "contracts")
    if os.path.isdir(contracts_dir):
        active_details = []
        for f in sorted(glob.glob(os.path.join(contracts_dir, "*.md"))):
            name = os.path.basename(f).replace(".md", "")
            with open(f, encoding="utf-8") as fh:
                text = fh.read()
            # extract contract_id and target
            cid = name
            target = ""
            for line in text.split("\n"):
                if line.strip().startswith("contract_id:"):
                    cid = line.split(":", 1)[1].strip()
                elif line.strip().startswith("target:"):
                    target = line.split(":", 1)[1].strip()
            detail = cid
            if target:
                detail += f" (target: {target})"
            active_details.append(detail)
        if active_details:
            parts.append(f"[Active contracts] {'; '.join(active_details)}")

    # precedent count
    prec_dir = os.path.join(agent_dir, "precedents")
    if os.path.isdir(prec_dir):
        precs = [f for f in os.listdir(prec_dir)
                 if f.endswith((".yaml", ".yml")) and f != "INDEX.yaml"]
        if precs:
            parts.append(f"[Precedents] {len(precs)} entries — read INDEX.yaml before judgment calls")

    # evidence — list existing so agent knows what's already done
    ev_dir = os.path.join(agent_dir, "evidence")
    if os.path.isdir(ev_dir):
        evs = [f.replace(".md", "") for f in os.listdir(ev_dir) if f.endswith(".md")]
        if evs:
            parts.append(f"[Evidence on record] {', '.join(sorted(evs))}")

    # check for evidence gaps on active contracts
    if os.path.isdir(contracts_dir):
        active_ids = []
        for f in sorted(glob.glob(os.path.join(contracts_dir, "*.md"))):
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    if line.strip().startswith("contract_id:"):
                        active_ids.append(line.split(":", 1)[1].strip())
                        break

        evidence_ids = set()
        if os.path.isdir(ev_dir):
            for f in os.listdir(ev_dir):
                if not f.endswith(".md"):
                    continue
                with open(os.path.join(ev_dir, f), encoding="utf-8") as fh:
                    for line in fh:
                        if line.strip().startswith("contract_id:"):
                            evidence_ids.add(line.split(":", 1)[1].strip())
                            break

        missing = [c for c in active_ids if c not in evidence_ids]
        if missing:
            parts.append(f"[EVIDENCE GAP] {', '.join(missing)} — no evidence yet")

    # reset governance coverage — agent no longer has prior reads in context
    reads_file = os.path.join(agent_dir, ".reads")
    if os.path.isfile(reads_file):
        os.remove(reads_file)

    if parts:
        msg = (
            "[Post-compaction context restore] "
            "Your conversation was compacted. Re-injecting .agent/ awareness. "
            + " | ".join(parts)
            + " | Read .agent/constitution.md for full terms. "
            "If you were executing a contract, read it again before continuing."
        )
        json.dump({"systemMessage": msg}, sys.stdout)

if __name__ == "__main__":
    main()
