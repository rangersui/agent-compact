"""Generate or check .agent/precedents/INDEX.yaml from precedent files.

Usage:
    python .agent/tools/index.py .agent/precedents          # generate INDEX.yaml
    python .agent/tools/index.py .agent/precedents --check   # check only, exit 1 if stale

INDEX.yaml is a generated artifact, not a source of truth.
Precedent files are the source of truth. Manual edits to INDEX.yaml
are forbidden — add fields to the precedent file instead.

Copied fields (deterministic order):
    id, holding, applies_when, tags, severity, status, date,
    supersedes, superseded_by
"""
import os
import sys
import glob

# fields copied from each precedent file into INDEX.yaml, in order
COPIED_FIELDS = [
    "id", "holding", "applies_when", "tags", "severity",
    "status", "date", "supersedes", "superseded_by",
]


def parse_yaml_simple(text):
    """Minimal YAML parser — flat key: value pairs only."""
    obj = {}
    current_key = None
    in_multiline = False
    for line in text.split("\n"):
        # top-level key: value
        if line and not line[0].isspace() and ":" in line:
            in_multiline = False
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            current_key = key
            if val.startswith(">") or val.startswith("|"):
                obj[key] = ""  # multiline — will accumulate
                in_multiline = True
            elif val == "":
                obj[key] = None
            else:
                obj[key] = val
        elif in_multiline and current_key and line.startswith("  "):
            # multiline continuation
            obj[current_key] = (obj[current_key] + " " + line.strip()).strip()
        elif current_key and line.startswith("  ") and obj.get(current_key) is None:
            # could be a list or nested — skip for now
            pass
    return obj


def load_precedents(prec_dir):
    """Load all precedent files, return list of parsed dicts sorted by id."""
    entries = []
    pattern = os.path.join(prec_dir, "*.yaml")
    for path in sorted(glob.glob(pattern)):
        name = os.path.basename(path)
        if name == "INDEX.yaml":
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        parsed = parse_yaml_simple(text)
        if "id" not in parsed:
            parsed["id"] = name.replace(".yaml", "")
        entries.append(parsed)
    # deterministic order: by id
    entries.sort(key=lambda e: e.get("id", ""))
    return entries


def generate_index(entries):
    """Generate INDEX.yaml content from parsed precedent entries."""
    lines = [
        "# AUTO-GENERATED — do not edit manually.",
        "# Source: .agent/precedents/*.yaml (excluding INDEX.yaml)",
        "# Regenerate: python .agent/tools/index.py .agent/precedents",
        "",
        "entries:",
    ]
    for entry in entries:
        first = True
        for field in COPIED_FIELDS:
            val = entry.get(field)
            if val is None:
                continue
            prefix = "  - " if first else "    "
            first = False
            lines.append(f"{prefix}{field}: {val}")
        if first:
            # no fields found — emit at least id
            lines.append(f"  - id: {entry.get('id', 'unknown')}")
        lines.append("")  # blank line between entries
    return "\n".join(lines) + "\n"


def load_existing_index(prec_dir):
    """Load existing INDEX.yaml if it exists."""
    index_path = os.path.join(prec_dir, "INDEX.yaml")
    if not os.path.isfile(index_path):
        return None
    with open(index_path, encoding="utf-8") as f:
        return f.read()


USAGE = """\
Usage: python index.py <precedents-dir> [--check]

  <precedents-dir>   directory containing *.yaml precedent files
  --check            compare only, exit 1 if INDEX.yaml is stale
  -h, --help         show this help and exit

Examples:
  python .agent/tools/index.py .agent/precedents          # generate
  python .agent/tools/index.py .agent/precedents --check   # verify
"""


def main():
    args = sys.argv[1:]

    # help
    if not args or "-h" in args or "--help" in args:
        print(USAGE, file=sys.stderr)
        sys.exit(0 if ("-h" in args or "--help" in args) else 2)

    # reject unknown flags
    known_flags = {"--check", "-h", "--help"}
    for arg in args:
        if arg.startswith("-") and arg not in known_flags:
            print(f"Unknown option: {arg}", file=sys.stderr)
            print(USAGE, file=sys.stderr)
            sys.exit(2)

    prec_dir = [a for a in args if not a.startswith("-")][0]
    check_only = "--check" in args

    if not os.path.isdir(prec_dir):
        print(f"Not a directory: {prec_dir}", file=sys.stderr)
        sys.exit(2)

    entries = load_precedents(prec_dir)
    existing = load_existing_index(prec_dir)

    if not entries:
        # no precedent files — but orphan INDEX.yaml?
        if existing is not None:
            if check_only:
                print("FAIL: INDEX.yaml exists but no precedent files found.", file=sys.stderr)
                sys.exit(1)
            else:
                # remove orphan INDEX
                os.remove(os.path.join(prec_dir, "INDEX.yaml"))
                print("Removed orphan INDEX.yaml (no precedent files).", file=sys.stderr)
        else:
            print("No precedent files found.", file=sys.stderr)
        sys.exit(0)

    generated = generate_index(entries)

    if check_only:
        existing = load_existing_index(prec_dir)
        if existing is None:
            print("FAIL: INDEX.yaml does not exist.", file=sys.stderr)
            sys.exit(1)
        if existing != generated:
            print("FAIL: INDEX.yaml is stale.", file=sys.stderr)
            # show which entries differ
            existing_ids = set()
            generated_ids = set()
            for line in existing.split("\n"):
                line = line.strip()
                if line.startswith("- id:") or line.startswith("id:"):
                    existing_ids.add(line.split(":", 1)[1].strip())
            for entry in entries:
                generated_ids.add(entry.get("id", ""))
            missing = generated_ids - existing_ids
            extra = existing_ids - generated_ids
            if missing:
                print(f"  Missing from INDEX: {', '.join(sorted(missing))}", file=sys.stderr)
            if extra:
                print(f"  In INDEX but no file: {', '.join(sorted(extra))}", file=sys.stderr)
            if not missing and not extra:
                print("  IDs match but field values differ.", file=sys.stderr)
            sys.exit(1)
        else:
            print("OK: INDEX.yaml is up to date.", file=sys.stderr)
            sys.exit(0)
    else:
        index_path = os.path.join(prec_dir, "INDEX.yaml")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(generated)
        print(f"Generated {index_path} ({len(entries)} entries)", file=sys.stderr)


if __name__ == "__main__":
    main()
