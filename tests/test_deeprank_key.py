"""The deep-rerank key name is the host's choice, not a vendor's."""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from handrolled import deeprank  # noqa: E402


class TestKeyName(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "creds.yaml"
        self.path.write_text("refs:\n  MINE: sk-abc\n  DEEP_API_KEY: sk-default\n", encoding="utf-8")
        self._env = {k: v for k, v in os.environ.items() if k.startswith("DSH_KB_DEEP")}
        for key in list(os.environ):
            if key.startswith("DSH_KB_DEEP"):
                os.environ.pop(key)
        os.environ["DSH_KB_DEEP_CREDENTIALS"] = str(self.path)

    def tearDown(self):
        for key in [k for k in os.environ if k.startswith("DSH_KB_DEEP")]:
            os.environ.pop(key, None)
        os.environ.update(self._env)
        self._tmp.cleanup()
        importlib.reload(deeprank)

    def test_the_default_name_is_used_when_unnamed(self):
        importlib.reload(deeprank)
        self.assertEqual(deeprank._api_key(), "sk-default")

    def test_the_host_can_name_its_own_key(self):
        os.environ["DSH_KB_DEEP_KEY_NAME"] = "MINE"
        importlib.reload(deeprank)
        self.assertEqual(deeprank._api_key(), "sk-abc")

    def test_an_explicit_env_key_wins_over_the_file(self):
        os.environ["DSH_KB_DEEP_API_KEY"] = "sk-explicit"
        importlib.reload(deeprank)
        self.assertEqual(deeprank._api_key(), "sk-explicit")

    def test_a_missing_name_reports_no_key_rather_than_guessing(self):
        os.environ["DSH_KB_DEEP_KEY_NAME"] = "NOT_THERE"
        importlib.reload(deeprank)
        self.assertIsNone(deeprank._api_key())


if __name__ == "__main__":
    unittest.main()
