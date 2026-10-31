"""Unit tests for the text helpers: CJK expansion, FTS5 matching, front matter.

Pure functions — no network, no filesystem, no knowledge base.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from handrolled.text import (  # noqa: E402
    expand_for_index,
    make_snippet,
    match_expression,
    parse_frontmatter,
    split_frontmatter,
    query_tokens,
)


class TestTextExpansion(unittest.TestCase):
    def test_latin_survives_expansion(self):
        """Regression: an early version dropped all latin text, so identifiers
        and paths became unsearchable while Chinese still worked."""
        out = expand_for_index("docker 与 fstab 的配置")
        for needle in ("docker", "fstab", "配置"):
            self.assertIn(needle, out)

    def test_cjk_bigrams_are_appended(self):
        out = expand_for_index("知识库")
        self.assertIn("知识", out)
        self.assertIn("识库", out)

    def test_pure_latin_is_untouched(self):
        self.assertEqual(expand_for_index("only latin here"), "only latin here")

    def test_query_tokens_split_identifiers(self):
        tokens = query_tokens("z2-sensitive")
        self.assertEqual(tokens[0], "z2-sensitive")
        self.assertIn("z2", tokens)
        self.assertIn("sensitive", tokens)

    def test_query_tokens_expand_chinese(self):
        tokens = query_tokens("挂载")
        self.assertIn("挂载", tokens)

    def test_query_tokens_are_deduplicated(self):
        tokens = query_tokens("docker docker DOCKER")
        self.assertEqual([t.lower() for t in tokens], ["docker"])

    def test_match_expression_quotes_every_token(self):
        self.assertEqual(match_expression(["a", "b"]), '"a" OR "b"')

    def test_match_expression_neutralises_fts_syntax(self):
        expr = match_expression(['OR "x"'])
        self.assertTrue(expr.startswith('"'))
        self.assertNotIn(" OR x", expr)


class TestSnippets(unittest.TestCase):
    def test_reports_line_of_first_hit(self):
        body = "line one\nline two\nneedle here\nline four"
        snippet, line = make_snippet(body, ["needle"], width=80)
        self.assertEqual(line, 3)
        self.assertIn("needle", snippet)

    def test_falls_back_to_head_when_no_hit(self):
        snippet, line = make_snippet("nothing to see", ["absent"], width=80)
        self.assertEqual(line, 1)
        self.assertTrue(snippet)

    def test_window_is_bounded(self):
        body = "x" * 500 + "needle" + "y" * 500
        snippet, _ = make_snippet(body, ["needle"], width=100)
        self.assertLessEqual(len(snippet), 110)


class TestFrontmatter(unittest.TestCase):
    def test_reads_scalars_and_inline_lists(self):
        text = "---\ntype: lesson\ntitle: 标题\ntags: [a, b]\n---\nbody\n"
        meta = parse_frontmatter(text)
        self.assertEqual(meta["type"], "lesson")
        self.assertEqual(meta["title"], "标题")
        self.assertEqual(meta["tags"], ["a", "b"])

    def test_missing_frontmatter_is_empty(self):
        self.assertEqual(parse_frontmatter("# just a heading"), {})

    def test_inline_mapping_is_read(self):
        """``generated.at`` 是"谁更新"的判据，所以内联 map 必须读出来。

        改写自旧断言（旧版刻意跳过 `{...}`）。跳过它意味着 `pages.fm_at`
        永远是空的，而 supersede 的默认 `valid_until` 与"谁取代谁"的排序都要
        它。仍然不支持的只有**更深的块状嵌套**，那是另一条断言。
        """
        meta = parse_frontmatter("---\ntype: x\ngenerated: { by: a, at: b }\n---\n")
        self.assertEqual(meta["type"], "x")
        self.assertEqual(meta["generated"], {"by": "a", "at": "b"})

    def test_block_list_and_deep_nesting(self):
        """块状列表（supersedes 的常见写法）要读；更深的嵌套只吃掉、不报错。"""
        text = ("---\ntype: x\nsupersedes:\n  - \"z1/a.md\"\n  - z1/b.md\n"
                "sources:\n  - id: a\n    resource: /b\n---\nbody\n")
        meta = parse_frontmatter(text)
        self.assertEqual(meta["supersedes"], ["z1/a.md", "z1/b.md"])
        self.assertEqual(meta["sources"], [{"id": "a"}])

    def test_quoted_comma_survives_the_inline_split(self):
        meta = parse_frontmatter('---\ntags: ["a,b", c]\n---\n')
        self.assertEqual(meta["tags"], ["a,b", "c"])

    def test_valueless_key_is_an_empty_list(self):
        self.assertEqual(parse_frontmatter("---\nsupersedes:\n---\nx\n"), {"supersedes": []})


class TestSplitFrontmatter(unittest.TestCase):
    """前端块剥离 + **行号回算**：报错行号比不剥更糟。"""

    def test_header_lines_are_counted_so_file_lines_survive(self):
        text = "---\ntype: x\ntitle: T\n---\nbody one\nbody two\n"
        body, header = split_frontmatter(text)
        self.assertEqual(body, "body one\nbody two\n")
        self.assertEqual(header, 4, "前 4 行是头部（含收尾的 ---）")
        # body 第 2 行 → 文件第 6 行
        self.assertEqual(6, header + 2)

    def test_no_header_is_a_noop(self):
        text = "# just a heading\nmore\n"
        self.assertEqual(split_frontmatter(text), (text, 0))

    def test_unterminated_header_is_left_alone(self):
        text = "---\ntype: x\nno closing rule\n"
        self.assertEqual(split_frontmatter(text), (text, 0))

    def test_header_without_body(self):
        """没有正文页也要算对：头部占了 1..3 行（含收尾那条 ---）。"""
        body, header = split_frontmatter("---\ntype: x\n---")
        self.assertEqual(body, "")
        self.assertEqual(header, 3)

    def test_inline_rule_inside_the_body_is_not_a_terminator_twice(self):
        text = "---\ntype: x\n---\nbody\n---\nafter\n"
        body, header = split_frontmatter(text)
        self.assertEqual(body, "body\n---\nafter\n")
        self.assertEqual(header, 3)


if __name__ == "__main__":
    unittest.main()
