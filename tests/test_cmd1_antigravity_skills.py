"""Tests for CMD-1 Antigravity onboarding and management skills (/setup, /reset, /expand).

Guards the three Antigravity skill definitions under .agents/skills/ against
structural drift, broken YAML frontmatter, missing canonical spec references,
and security guard regressions.
"""

import subprocess
import sys
import unittest
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_SKILLS_DIR = REPO_ROOT / ".agents" / "skills"


def _parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    if yaml is None:
        raise unittest.SkipTest("PyYAML is required for frontmatter parsing")
    return yaml.safe_load(text[4:end]) or {}


class TestSetupSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "setup" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "commands" / "setup.md"

    def test_setup_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/setup/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/commands/setup.md must exist")

    def test_setup_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "setup")
        self.assertTrue(data.get("description"), "setup skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "setup skill must be enabled by default")

    def test_setup_skill_content_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/commands/setup.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("edit_file", text)
        self.assertIn("run_command", text)
        self.assertIn("ask_question", text)
        self.assertIn("invoke_subagent", text)

    def test_setup_skill_has_antigravity_runtime_notes(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("@-Mention Shortcut", text)
        self.assertIn("Public-Fork Preflight", text)
        self.assertIn("git remote get-url origin", text)
        self.assertIn("find documents", text)


class TestResetSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "reset" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "commands" / "reset.md"

    def test_reset_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/reset/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/commands/reset.md must exist")

    def test_reset_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "reset")
        self.assertTrue(data.get("description"), "reset skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "reset skill must be enabled by default")

    def test_reset_skill_content_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/commands/reset.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("edit_file", text)
        self.assertIn("run_command", text)
        self.assertIn("ask_question", text)

    def test_reset_skill_has_destructive_safeguards(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("destructive", text.lower())
        self.assertIn("RESET", text)
        self.assertIn("POSIX Delete Block", text)
        self.assertIn(".gitkeep", text)


class TestExpandSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "expand" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "commands" / "expand.md"

    def test_expand_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/expand/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/commands/expand.md must exist")

    def test_expand_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "expand")
        self.assertTrue(data.get("description"), "expand skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "expand skill must be enabled by default")

    def test_expand_skill_content_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/commands/expand.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("edit_file", text)
        self.assertIn("run_command", text)
        self.assertIn("search_web", text)
        self.assertIn("ask_question", text)

    def test_expand_skill_has_trust_boundary_and_additive_invariants(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Additive only", text)
        self.assertIn("Trust Boundary", text)
        self.assertIn("09-web-research.md", text)
        self.assertIn("fetch_page.py", text)


class TestCMD1Integration(unittest.TestCase):
    def test_lint_skills_passes_with_new_skills(self):
        res = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "lint_skills.py")],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"lint_skills.py failed:\n{res.stdout}\n{res.stderr}")
        self.assertIn("16 skills", res.stdout)

    def test_security_guards_pass(self):
        res = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "security_guards.py")],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"security_guards.py failed:\n{res.stdout}\n{res.stderr}")


if __name__ == "__main__":
    unittest.main()
