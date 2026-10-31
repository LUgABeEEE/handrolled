"""Hand-rolled, stdlib-only replacements for things you would normally pip install.

Every module here exists for the same reason: the obvious solution adds a
dependency, and the dependency is bigger than the problem.

* :mod:`handrolled.text` — CJK bigrams, FTS5 match expressions and a
  YAML-subset front matter reader (instead of jieba, a query builder and PyYAML)
* :mod:`handrolled.webdav` — a WebDAV client speaking the RFC 4918 subset that
  actually gets used (instead of requests + webdavclient3)
* :mod:`handrolled.mounts` — network mount inspection that reports what is
  really mounted, not its autofs trigger (instead of parsing ``mount`` output)
* :mod:`handrolled.pages` + :mod:`handrolled.importers` — turn another tool's
  export (mem0, Obsidian, Notion, basic-memory, JSON/JSONL) into Markdown pages
* :mod:`handrolled.rerank`, :mod:`handrolled.deeprank`,
  :mod:`handrolled.embed_onnx` — optional ranking helpers that degrade to
  ``None`` when their model or dependency is absent

Nothing here imports a third-party package at module import time; the optional
ones import inside functions and return ``None`` when the dependency is missing.
"""

from __future__ import annotations

__version__ = "0.1.1"

__all__ = ["__version__"]
