"""Stop hook — check evidence gaps before session ends."""
import json, os, sys, glob

def main():
    agent_dir = os.path.join(os.getcwd(), ".agent")
    if not os.path.isdir(agent_dir):
        return

    contracts_dir = os.path.join(agent_dir, "contracts")
    evidence_dir = os.path.join(agent_dir, "evidence")

    if not os.path.isdir(contracts_dir):
        return

    # find active contracts (not in archived/)
    active = []
    for f in sorted(glob.glob(os.path.join(contracts_dir, "*.md"))):
        name = os.path.basename(f).replace(".md", "")
        # extract contract_id from frontmatter
        with open(f, encoding="utf-8") as fh:
            text = fh.read()
        cid = name  # fallback
        for line in text.split("\n"):
            if line.strip().startswith("contract_id:"):
                cid = line.split(":", 1)[1].strip()
                break
        active.append(cid)

    if not active:
        return

    # check which active contracts have evidence
    evidence_ids = set()
    if os.path.isdir(evidence_dir):
        for f in os.listdir(evidence_dir):
            if not f.endswith(".md"):
                continue
            path = os.path.join(evidence_dir, f)
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    if line.strip().startswith("contract_id:"):
                        evidence_ids.add(line.split(":", 1)[1].strip())
                        break

    missing = [c for c in active if c not in evidence_ids]

    if missing:
        msg = (
            f"[agent-compact] {len(missing)} active contract(s) have no evidence: "
            f"{', '.join(missing)}. "
            "Per Article 3, claims require evidence. "
            "Per Article 4, absence of expected evidence is prima facie evidence of non-performance."
        )
        json.dump({"systemMessage": msg}, sys.stdout)

if __name__ == "__main__":
    main()
