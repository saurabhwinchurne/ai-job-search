"""Tests for CMD-3 Antigravity core application engine skills (/apply, job-application-assistant).

Guards the Antigravity skill definitions under .agents/skills/ against
structural drift, broken YAML frontmatter, missing canonical spec references,
untranslated tools, and security guard regressions.
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


class TestApplySkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "apply" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "commands" / "apply.md"

    def test_apply_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/apply/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/commands/apply.md must exist")

    def test_apply_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "apply")
        self.assertTrue(data.get("description"), "apply skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "apply skill must be enabled by default")

    def test_apply_skill_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/commands/apply.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("edit_file", text)
        self.assertIn("run_command", text)
        self.assertIn("search_web", text)
        self.assertIn("ask_question", text)
        self.assertIn("invoke_subagent", text)

    def test_apply_skill_has_subagent_orchestration(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("posting-fetcher", text)
        self.assertIn("application-reviewer", text)
        self.assertIn("invoke_subagent", text)
        self.assertIn("Fallback", text)

    def test_apply_skill_has_trust_boundary_and_integrity_gate(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Trust boundary", text)
        self.assertIn("posting_guard.py", text)
        self.assertIn("09-web-research.md", text)
        self.assertIn("salary_lookup.py", text)
        self.assertIn("Zero Fabrication", text)

    def test_apply_skill_has_latex_and_verification_rules(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("lualatex", text)
        self.assertIn("xelatex", text)
        self.assertIn("verify_pdf.py", text)
        self.assertIn("verify_layout.py", text)
        self.assertIn("--pages 2", text)
        self.assertIn("--pages 1", text)
        self.assertIn("--ascii-dates", text)
        self.assertIn("--dump-text", text)

    def test_apply_skill_has_tracker_and_archiving_rules(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("job_search_tracker.csv", text)
        self.assertIn("documents/applications/", text)
        self.assertIn("deadline", text)
        self.assertIn("redrafted", text)

    def test_apply_skill_has_form_questions_assistant(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("08-application-forms.md", text)


class TestJobApplicationAssistantSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "job-application-assistant" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "skills" / "job-application-assistant" / "SKILL.md"

    def test_job_application_assistant_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/job-application-assistant/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/skills/job-application-assistant/SKILL.md must exist")

    def test_job_application_assistant_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "job-application-assistant")
        self.assertTrue(data.get("description"), "job-application-assistant skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "job-application-assistant skill must be enabled by default")

    def test_job_application_assistant_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/skills/job-application-assistant/SKILL.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("edit_file", text)
        self.assertIn("run_command", text)
        self.assertIn("search_web", text)
        self.assertIn("ask_question", text)
        self.assertIn("invoke_subagent", text)

    def test_job_application_assistant_references_all_methodology_files(self):
        text = self.skill_file.read_text(encoding="utf-8")
        expected_modules = [
            "01-candidate-profile.md",
            "02-behavioral-profile.md",
            "03-writing-style.md",
            "04-job-evaluation.md",
            "05-cv-templates.md",
            "06-cover-letter-templates.md",
            "07-interview-prep.md",
            "08-application-forms.md",
            "09-web-research.md",
        ]
        for mod in expected_modules:
            self.assertIn(mod, text, f"job-application-assistant must reference {mod}")

    def test_job_application_assistant_workflow_and_sync(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Trust boundary", text)
        self.assertIn("posting_guard.py", text)
        self.assertIn("job_search_tracker.csv", text)
        self.assertIn("Step 6b", text)
        self.assertIn("documents/applications/", text)


class TestCMD3Integration(unittest.TestCase):
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

