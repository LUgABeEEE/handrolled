# handrolled

**Hand-rolled, stdlib-only replacements for things you would normally `pip install`.**

Every module here exists for the same reason: the obvious solution adds a dependency,
and the dependency is bigger than the problem.

```bash
pip install handrolled        # installs nothing else
```

Python ≥ 3.10, **no runtime dependencies**. `import handrolled` never touches
third-party code — the optional pieces import inside functions and return `None`
when their dependency is missing.

## What's in it

| Module | Instead of | What it actually does |
|---|---|---|
| `handrolled.text` | `jieba`, a query builder, `PyYAML` | CJK bigram expansion for SQLite FTS5, FTS5 match-expression building (quotes and neutralises user input), and a YAML-**subset** front matter reader |
| `handrolled.webdav` | `requests` + `webdavclient3` | WebDAV over the RFC 4918 subset that gets used: `PROPFIND`, `GET`, `PUT`, `MKCOL`, `DELETE`; Basic auth, mTLS, and connect-host/SNI separation for appliances whose certificate CN is not their address |
| `handrolled.mounts` | parsing `mount` output | Network mount inspection that reports the **real** filesystem rather than its `autofs` trigger, `rw`/`ro` state, and `ESTALE`/`EACCES`/`ENOENT` turned into sentences a human can act on |
| `handrolled.pages` + `handrolled.importers` | hand-written one-off scripts | Turn another tool's export into Markdown pages: `mem0`, Obsidian, Notion's Markdown export, basic-memory, plain JSON/JSONL, and a neutral `records/v1` format. Deterministic, additive, guarded |
| `handrolled.rerank` | `sentence-transformers` | Cross-encoder reranking of `(query, passage)` pairs from an int8 ONNX model, with idle unloading so the memory comes back |
| `handrolled.deeprank` | an SDK per vendor | Let a remote chat model pick which candidate pages answer a query; any failure degrades to the original order |
| `handrolled.embed_onnx` | `sentence-transformers` | ONNX embedding backend (last-token pooling, L2 normalised), kept for A/B work |

## Design rules

1. **Standard library only.** If a module cannot be written with the stdlib and a
   documented protocol, it does not belong here.
2. **Optional means optional.** Anything needing a model or an extra package
   imports lazily and returns `None`/`False` when it is absent. Nothing raises at
   import time, and nothing silently changes behaviour because a package happens
   to be installed.
3. **No machine assumptions.** Optional layers have no built-in paths: unset
   environment variable means the layer is off. Nothing guesses where your models
   or credentials live.
4. **Deterministic output.** `handrolled.pages` renders the same records to the
   same bytes, so a second run is a no-op and a diff means something.

## Quick example

```python
from handrolled import importers
from handrolled.pages import plan, apply

records = importers.load("obsidian", "/path/to/vault")
planned = plan(policy, records, prefix="notes", zone="private")
print(f"{planned.items} records → {len(planned.pages)} pages")
apply(source, planned, write=True)
```

`policy` is any object with `zones` (things with a `.name`) and
`is_never(rel) -> bool` — the caller owns the privacy model, not this library.

## Where this comes from

Extracted from [dsh-kb](https://github.com/LUgABeEEE/dsh-kb), a personal
knowledge base built to be queried cheaply by AI agents. Those modules were
written there, hardened against a real deployment, and turned out to have nothing
to do with knowledge bases in particular.

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -t .
```

Offline, dependency-free, no fixtures to download.

## License

MIT — see [LICENSE](LICENSE).
