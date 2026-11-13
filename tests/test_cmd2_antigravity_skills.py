"""Tests for CMD-2 Antigravity job-search skills (/scrape, /rank).

Guards the two Antigravity skill definitions under .agents/skills/ against
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


class TestScrapeSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "scrape" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "skills" / "job-scraper" / "SKILL.md"

    def test_scrape_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/scrape/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/skills/job-scraper/SKILL.md must exist")

    def test_scrape_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "scrape")
        self.assertTrue(data.get("description"), "scrape skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "scrape skill must be enabled by default")

    def test_scrape_skill_content_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/skills/job-scraper/SKILL.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("edit_file", text)
        self.assertIn("run_command", text)
        self.assertIn("search_web", text)
        self.assertIn("ask_question", text)
        self.assertIn("invoke_subagent", text)

    def test_scrape_skill_has_portal_discovery_and_trust_boundary(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Portal CLI Discovery", text)
        self.assertIn("posting_guard.py", text)
        self.assertIn("09-web-research.md", text)
        self.assertIn("scrape_state.py", text)
        self.assertIn("invoke_subagent", text)
        self.assertIn("search-queries.md", text)

    def test_scrape_skill_has_health_check_and_referral_notes(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Portal Health Check", text)
        self.assertIn("Referral Contact Links", text)
        self.assertIn("enabled:", text)
        self.assertIn("job_key.py", text)

    def test_scrape_skill_has_parallel_and_bun_notes(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Parallel Portal Searches", text)
        self.assertIn("bun", text)
        self.assertIn("fetch_page.py", text)


class TestRankSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "rank" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "commands" / "rank.md"

    def test_rank_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/rank/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/commands/rank.md must exist")

    def test_rank_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "rank")
        self.assertTrue(data.get("description"), "rank skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "rank skill must be enabled by default")

    def test_rank_skill_content_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/commands/rank.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("edit_file", text)
        self.assertIn("run_command", text)
        self.assertIn("search_web", text)
        self.assertIn("ask_question", text)
        self.assertIn("invoke_subagent", text)

    def test_rank_skill_has_subagent_and_state_management(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("posting-scorer", text)
        self.assertIn("rank_state.py", text)
        self.assertIn("posting_guard.py", text)
        self.assertIn("04-job-evaluation.md", text)
        self.assertIn("01-candidate-profile.md", text)
        self.assertIn("invoke_subagent", text)

    def test_rank_skill_has_sweep_and_scoring_notes(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Expiry Sweep", text)
        self.assertIn("Score Aggregation", text)
        self.assertIn("Veto Rules", text)
        self.assertIn("30%", text)
        self.assertIn("25%", text)
        self.assertIn("15%", text)
        self.assertIn("Strong Fit", text)

    def test_rank_skill_has_temporary_files_and_profile_loading(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Temporary Files", text)
        self.assertIn("Profile and Framework Loading", text)
        self.assertIn("antigravity_subagents.py", text)
        self.assertIn("09-web-research.md", text)


class TestCMD2Integration(unittest.TestCase):
    def test_lint_skills_passes_with_new_skills(self):
        res = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "lint_skills.py")],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"lint_skills.py failed:\n{res.stdout}\n{res.stderr}")
        self.assertIn("24 skills", res.stdout)

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
