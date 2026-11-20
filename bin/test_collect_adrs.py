import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import collect_adrs


class CollectAdrsTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.target = self.root / "home" / "docs" / "adr"
        self.target.mkdir(parents=True)
        self.source_root = self.root / "clones"
        self.source = self.source_root / "example" / "docs" / "adr"
        self.source.mkdir(parents=True)
        self.source_text = "# Decision\n\n- **Status:** proposed\n"
        (self.source / "0001-decision.md").write_text(self.source_text)
        self.snapshot = self.target / "example" / "0001-decision.md"
        self.snapshot.parent.mkdir()
        self.snapshot.write_text("previous snapshot\n")
        self.index = self.target / "index.md"
        self.index.write_text("previous index\n")
        self.nav = self.root / "home" / "mkdocs.yml"
        self.nav_text = collect_adrs.NAV_START + "\n" + collect_adrs.NAV_END + "\n"
        self.nav.write_text(self.nav_text)
        repos = self.root / "home" / "git-repos.txt"
        repos.write_text("example\n")
        for name, value in (
            ("TARGET", self.target),
            ("MKDOCS", self.nav),
            ("SOURCES", repos),
        ):
            patcher = patch.object(collect_adrs, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch("sys.argv", ["collect_adrs.py", "--source-root", str(self.source_root)])
        patcher.start()
        self.addCleanup(patcher.stop)

    def assert_previous_output(self):
        self.assertEqual(self.snapshot.read_text(), "previous snapshot\n")
        self.assertEqual(self.index.read_text(), "previous index\n")
        self.assertEqual(self.nav.read_text(), self.nav_text)

    def test_missing_source_preserves_existing_snapshots_index_and_nav(self):
        (self.source / "0001-decision.md").unlink()
        self.source.rmdir()
        with self.assertRaisesRegex(SystemExit, "existing snapshot has no source"):
            collect_adrs.main()
        self.assert_previous_output()

    def test_dirty_source_aborts_before_replacing_output(self):
        with patch.object(collect_adrs, "git", side_effect=["a" * 40, " M docs/adr/0001-decision.md"]):
            with self.assertRaisesRegex(SystemExit, "must be committed"):
                collect_adrs.main()
        self.assert_previous_output()

    def test_explicit_source_root_preserves_decision_and_full_commit_provenance(self):
        sha = "a" * 40
        with patch.object(collect_adrs, "git", side_effect=[sha, "", sha]) as git:
            with contextlib.redirect_stdout(io.StringIO()):
                collect_adrs.main()
        self.assertEqual(git.call_args_list[0].args[0], self.source_root.resolve() / "example")
        self.assertTrue(self.snapshot.read_text().startswith(self.source_text))
        self.assertIn(f"/blob/{sha}/docs/adr/0001-decision.md", self.snapshot.read_text())
        self.assertIn(f"example@{sha}", self.index.read_text())
        self.assertIn("proposed", self.index.read_text())
        self.assertIn("adr/example/0001-decision.md", self.nav.read_text())


if __name__ == "__main__":
    unittest.main()
