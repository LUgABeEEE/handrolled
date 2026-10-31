# Changelog

## [0.1.1] — 2026-10-31

### Added

- `DSH_KB_DEEP_KEY_NAME` names the key to read out of the credentials file
  (default `DEEP_API_KEY`).  A host that already keeps its key under another
  name — a shared credentials file for several services — no longer has to copy
  the secret into a second file just to be readable.  The vendor name stays out
  of the code either way.

## [0.1.0] — 2026-10-31

First release.  Extracted from [dsh-kb](https://github.com/LUgABeEEE/dsh-kb),
where these modules were written and hardened against a real deployment:

- `text` — CJK bigrams for SQLite FTS5, match-expression building, front matter
- `webdav` — the RFC 4918 subset that gets used, with Basic auth, mTLS and
  connect-host/SNI separation
- `mounts` — the real mounted filesystem rather than its autofs trigger;
  `ESTALE`/`EACCES`/`ENOENT` turned into sentences
- `pages` + `importers` — mem0, Obsidian, Notion, basic-memory, JSON/JSONL and a
  neutral `records/v1` format, rendered deterministically into Markdown
- `rerank`, `deeprank`, `embed_onnx` — optional ranking layers that return
  `None` when their model or dependency is absent
