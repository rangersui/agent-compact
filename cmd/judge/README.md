# judge

Local docket viewer for `.agent/` directories. Single binary, zero dependencies.

## Build

```
cd cmd/judge
go build -o judge .
```

## Usage

```
./judge                          # serves .agent/ in current directory
./judge /path/to/.agent          # explicit path
./judge -port 9999 .agent        # custom port
./judge -no-browser .agent       # don't auto-open browser
```

Auto-opens browser to a dark-themed viewer with:

- **Sidebar** — Contracts / Evidence / Precedents tabs
- **Metadata table** — YAML frontmatter rendered as key-value pairs
- **Markdown body** — headings, code blocks, tables, evidence type badges
- **Lifecycle checker** — verifies archived contracts have evidence, evidence has commit pins
- **Scaffold templates** — copy-paste starters for new contracts, evidence, precedents

Read-only. Does not write to the `.agent/` directory.

## API

| Endpoint | Method | Response |
|----------|--------|----------|
| `/` | GET | Embedded HTML viewer |
| `/api/files` | GET | JSON array of `{path, content}` for all `.md`/`.yaml`/`.yml` files |
