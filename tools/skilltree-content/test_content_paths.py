#!/usr/bin/env python3
"""Path classifier for the browser-suite decision in run_gates.py."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_gates  # noqa: E402


CONTENT = [
    "skilltree/bank/bode.json",
    "./skilltree/explainers/bode.json",
    "skilltree/bank_retired/v3_archive.json",
    "skilltree/ee105_skills_draft.json",
    "skilltree/collections.json",
    "skilltree/deep_quota_grandfather.json",
    "skilltree/gen/s_bode.py",
    "skilltree/verify_me132_b1.py",
    "skilltree/verify_sg057_g1.py",
    "public/skilltree/banks/bode.1237d4f0.json",
    "public/skilltree/explainers/bode.1cfc30db.json",
    "public/skilltree/manifest.json",
    "public/skilltree/skills.f25abd9f.json",
    "public/skilltree/collections.6c18ba13.json",
    "public/skilltree/tests/test-content.js",
    "tools/skilltree-content/me132_b1_gen.py",
    "tools/skilltree-content/sg057_g1_gen.py",
    "tools/skilltree-content/banklib.py",
    "tools/skilltree-content/s_bode.py",
    "docs/briefs/me132-b1.md",
    "docs/reports/me132-b1.md",
    "docs/gates/me132-b1.json",
    "docs/batches/me132-b1.json",
    "docs/CHANGELOG.md",
    "docs/content-versions.json",
    "docs/notation.md",
    "docs/sources.md",
    "docs/dedupe-decisions.json",
]

NOT_CONTENT = [
    "public/skilltree/skilltree.js",
    "public/skilltree/skilltree.css",
    "public/skilltree/index.html",
    "public/skilltree/admin.js",
    "public/skilltree/tests/test.js",
    "skilltree/app/skilltree.html",
    "skilltree/page.tsx",
    "skilltree/build.py",
    "skilltree/validate_bank.py",
    "skilltree/verify_harness.py",
    "tools/skilltree-content/build.py",
    "tools/skilltree-content/run_gates.py",
    "tools/skilltree-content/write_batch_docs.py",
    "src/App.tsx",
    "CONTRIBUTING.md",
    "docs/skill-tree-content-SOP.md",
    "docs/batch-starter.md",
]


class ContentPathTests(unittest.TestCase):
    def test_content_paths(self):
        for path in CONTENT:
            self.assertTrue(run_gates.is_content_path(path), path)

    def test_app_ui_and_build_paths(self):
        for path in NOT_CONTENT:
            self.assertFalse(run_gates.is_content_path(path), path)

    def test_content_only_diff_skips(self):
        run, why = run_gates.decide_browser(CONTENT, None)
        self.assertFalse(run)
        self.assertIn("content-only", why)

    def test_a_ui_path_runs_the_suite(self):
        run, why = run_gates.decide_browser(
            ["skilltree/bank/bode.json", "public/skilltree/skilltree.js"], None
        )
        self.assertTrue(run)
        self.assertIn("public/skilltree/skilltree.js", why)
        self.assertNotIn("skilltree/bank/bode.json", why)

    def test_build_code_runs_the_suite(self):
        run, why = run_gates.decide_browser(["tools/skilltree-content/build.py"], None)
        self.assertTrue(run)
        self.assertIn("build.py", why)

    def test_bytecode_does_not_force_the_suite(self):
        run, why = run_gates.decide_browser(
            ["skilltree/bank/bode.json", "tools/skilltree-content/__pycache__/banklib.cpython-312.pyc"],
            None,
        )
        self.assertFalse(run)
        self.assertIn("content-only", why)

    def test_empty_diff_skips_and_unknown_diff_runs(self):
        run, why = run_gates.decide_browser([], None)
        self.assertFalse(run)
        self.assertIn("origin/main", why)
        run, why = run_gates.decide_browser(None, None)
        self.assertTrue(run)
        self.assertIn("origin/main", why)

    def test_flags_override_the_classifier(self):
        run, why = run_gates.decide_browser(["public/skilltree/index.html"], "no-browser")
        self.assertFalse(run)
        self.assertIn("--no-browser", why)
        run, why = run_gates.decide_browser(["skilltree/bank/bode.json"], "browser")
        self.assertTrue(run)
        self.assertIn("--browser", why)


if __name__ == "__main__":
    unittest.main()
