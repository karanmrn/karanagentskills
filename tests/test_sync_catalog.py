import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "sync_catalog.py"


class SyncCatalogTest(unittest.TestCase):
    def test_syncs_skills_preserves_archive_entries_and_generates_catalog(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            destination = root / "skills"
            source.mkdir()
            destination.mkdir()

            (source / "alpha").mkdir()
            (source / "alpha" / "SKILL.md").write_text(
                "---\n"
                "name: alpha\n"
                "description: >-\n"
                "  First line with | punctuation.\n"
                "  Second line stays in the description.\n"
                "---\n"
                "# Alpha\n",
                encoding="utf-8",
            )
            (source / "beta").mkdir()
            (source / "beta" / "SKILL.md").write_text(
                "---\nname: beta\ndescription: Beta skill.\n---\n# Beta\n",
                encoding="utf-8",
            )
            (source / "group" / "gamma").mkdir(parents=True)
            (source / "group" / "gamma" / "SKILL.md").write_text(
                "---\n"
                "name: gamma\n"
                "description:\n"
                "  Nested skill with an indented description.\n"
                "---\n"
                "# Gamma\n",
                encoding="utf-8",
            )
            (source / "delta").mkdir()
            (source / "delta" / "SKILL.md").write_text(
                "# Delta\n\n> Body-only skill description.\n",
                encoding="utf-8",
            )
            (source / "epsilon").mkdir()
            (source / "epsilon" / "SKILL.md").write_text(
                "---\n"
                "name: epsilon\n"
                "description: '''Clean Codex''''s summary — no leaked metadata.'' metadata: short-description: Ignore me'\n"
                "---\n",
                encoding="utf-8",
            )
            (destination / "archive-only").mkdir()
            (destination / "archive-only" / "SKILL.md").write_text(
                "---\nname: archive-only\ndescription: Preserved history.\n---\n",
                encoding="utf-8",
            )

            lock = root / "skill-lock.json"
            lock.write_text(
                json.dumps(
                    {
                        "skills": {
                            "alpha": {
                                "source": "example/skills",
                                "sourceUrl": "https://github.com/example/skills.git",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            catalog = root / "CATALOG.md"

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--source",
                    str(source),
                    "--destination",
                    str(destination),
                    "--lock",
                    str(lock),
                    "--catalog",
                    str(catalog),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((destination / "alpha" / "SKILL.md").is_file())
            self.assertTrue((destination / "beta" / "SKILL.md").is_file())
            self.assertTrue((destination / "archive-only" / "SKILL.md").is_file())

            rendered = catalog.read_text(encoding="utf-8")
            self.assertIn("6 skills.", rendered)
            self.assertIn("First line with \\| punctuation. Second line stays", rendered)
            self.assertIn("Nested skill with an indented description.", rendered)
            self.assertIn("Body-only skill description.", rendered)
            self.assertIn("Clean Codex's summary - no leaked metadata.", rendered)
            self.assertNotIn("short-description", rendered)
            self.assertIn("[example/skills](https://github.com/example/skills)", rendered)
            self.assertIn("Archive copy", rendered)
            self.assertIn("[`gamma`](skills/group/gamma/)", rendered)


if __name__ == "__main__":
    unittest.main()
