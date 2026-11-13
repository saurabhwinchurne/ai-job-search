"""Tests for CMD-5 Antigravity customization and reporting skills (/add-template, /add-portal, /html-report, /notion-sync).

Guards the Antigravity skill definitions under .agents/skills/ against
structural drift, broken YAML frontmatter, missing canonical spec references,
untranslated tools, safety violations, and security guard regressions.
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


class TestAddTemplateSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "add-template" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "commands" / "add-template.md"

    def test_add_template_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/add-template/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/commands/add-template.md must exist")

    def test_add_template_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "add-template")
        self.assertTrue(data.get("description"), "add-template skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "add-template skill must be enabled by default")

    def test_add_template_skill_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/commands/add-template.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("edit_file", text)
        self.assertIn("run_command", text)
        self.assertIn("ask_question", text)

    def test_add_template_skill_has_modes(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("--list", text)
        self.assertIn("--use <name>", text)
        self.assertIn("--use default", text)
        self.assertIn("List Mode", text)
        self.assertIn("Switch Mode", text)

    def test_add_template_skill_has_build_redirect_and_test_compile(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("build/", text)
        self.assertIn("_compile_test", text)
        self.assertIn("rm -f <file>.pdf", text)
        self.assertIn("lualatex", text)
        self.assertIn("typst", text)

    def test_add_template_skill_has_managed_block_activation(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("BEGIN ACTIVE-TEMPLATE", text)
        self.assertIn("END ACTIVE-TEMPLATE", text)
        self.assertIn("05-cv-templates.md", text)
        self.assertIn("06-cover-letter-templates.md", text)


class TestAddPortalSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "add-portal" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "commands" / "add-portal.md"

    def test_add_portal_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/add-portal/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/commands/add-portal.md must exist")

    def test_add_portal_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "add-portal")
        self.assertTrue(data.get("description"), "add-portal skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "add-portal skill must be enabled by default")

    def test_add_portal_skill_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/commands/add-portal.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("edit_file", text)
        self.assertIn("run_command", text)
        self.assertIn("search_web", text)
        self.assertIn("fetch_page.py", text)

    def test_add_portal_skill_trust_boundary_and_robots(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Trust boundary", text)
        self.assertIn("09-web-research.md", text)
        self.assertIn("robots.txt", text)
        self.assertIn("personal-use", text)

    def test_add_portal_skill_scaffold_structure_and_contract(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("url-reference.md", text)
        self.assertIn("helpers.ts", text)
        self.assertIn("search.ts", text)
        self.assertIn("detail.ts", text)
        self.assertIn("visibleHtml", text)
        self.assertIn("stripInvisible", text)
        self.assertIn("package.json", text)
        self.assertIn("tsconfig.json", text)

    def test_add_portal_skill_cli_contract_and_security(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("search", text)
        self.assertIn("detail", text)
        self.assertIn("meta", text)
        self.assertIn("results", text)
        self.assertIn("ALLOWED_PERMISSIONS", text)
        self.assertIn("security_guards.py", text)
        self.assertIn("<SERVICE>_API_TOKEN", text)


class TestHtmlReportSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "html-report" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "commands" / "html-report.md"

    def test_html_report_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/html-report/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/commands/html-report.md must exist")

    def test_html_report_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "html-report")
        self.assertTrue(data.get("description"), "html-report skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "html-report skill must be enabled by default")

    def test_html_report_skill_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/commands/html-report.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)

    def test_html_report_skill_has_artifact_integration(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("dashboard.html", text)
        self.assertIn("artifact directory", text)
        self.assertIn("Generative UI", text)

    def test_html_report_skill_has_status_buckets_and_stats(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("job_search_tracker.csv", text)
        self.assertIn("outcome.md", text)
        self.assertIn("Drafted", text)
        self.assertIn("Active", text)
        self.assertIn("Interview", text)
        self.assertIn("Offer", text)
        self.assertIn("Hired", text)
        self.assertIn("Rejected/Closed", text)

    def test_html_report_skill_has_svg_charts_and_escaping(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("inline SVG", text)
        self.assertIn("Status Doughnut", text)
        self.assertIn("Application Funnel", text)
        self.assertIn("Mandatory escaping", text)
        self.assertIn("XSS", text)


class TestNotionSyncSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "notion-sync" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "commands" / "notion-sync.md"

    def test_notion_sync_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/notion-sync/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/commands/notion-sync.md must exist")

    def test_notion_sync_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "notion-sync")
        self.assertTrue(data.get("description"), "notion-sync skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "notion-sync skill must be enabled by default")

    def test_notion_sync_skill_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/commands/notion-sync.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("call_mcp_tool", text)

    def test_notion_sync_skill_has_trust_boundary_and_privacy(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("09-web-research.md", text)
        self.assertIn("Trust boundary", text)
        self.assertIn("filenames only", text)

    def test_notion_sync_skill_has_preflight_and_precedence(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Silently optional preflight", text)
        self.assertIn("Tracker status overrides scraper status", text)
        self.assertIn("Tracker deadline overrides scraper deadline", text)
        self.assertIn("expired", text)

    def test_notion_sync_skill_has_schema_and_upsert_rules(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("notion_sync.json", text)
        self.assertIn("Job Search Pipeline", text)
        self.assertIn("Key", text)
        self.assertIn("write-once", text)


class TestCMD5Integration(unittest.TestCase):
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

    def test_subagent_validation_passes(self):
        res = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "antigravity_subagents.py"), "validate"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"antigravity_subagents.py validate failed:\n{res.stdout}\n{res.stderr}")


if __name__ == "__main__":
    unittest.main()
