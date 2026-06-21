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

    # governance coverage — what .agent/ files did the main agent actually read?
    # only "main" lines count toward due diligence; subagent lines are audit trail
    main_reads = set()
    sub_reads = set()
    reads_file = os.path.join(agent_dir, ".reads")
    if os.path.isfile(reads_file):
        with open(reads_file, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                if "\t" in line:
                    who, path = line.split("\t", 1)
                    if who == "main":
                        main_reads.add(path)
                    else:
                        sub_reads.add(path)
                else:
                    # legacy format (no who prefix) — treat as main
                    main_reads.add(line)

    expected = set()
    expected.add(".agent/constitution.md")
    for c in active:
        for f in sorted(glob.glob(os.path.join(contracts_dir, "*.md"))):
            expected.add(".agent/contracts/" + os.path.basename(f))

    covered = expected & main_reads
    uncovered = expected - main_reads

    parts = []

    if missing:
        parts.append(
            f"{len(missing)} active contract(s) have no evidence: "
            f"{', '.join(missing)}. "
            "Per Article 3, claims require evidence. "
            "Per Article 4, absence of expected evidence is prima facie evidence of non-performance."
        )

    if uncovered:
        detail = f"GOVERNANCE COVERAGE: {len(covered)}/{len(expected)}. "
        detail += f"Unread: {', '.join(sorted(uncovered))}"
        # flag if subagent read something the main agent didn't
        delegated = uncovered & sub_reads
        if delegated:
            detail += f". Note: {len(delegated)} read by subagent only (does not count — read the report, not the delegation)"
        parts.append(detail)

    if parts:
        json.dump({"systemMessage": "[agent-compact] " + " | ".join(parts)}, sys.stdout)

if __name__ == "__main__":
    main()
