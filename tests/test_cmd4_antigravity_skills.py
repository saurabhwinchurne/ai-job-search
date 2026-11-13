"""Tests for CMD-4 Antigravity post-application lifecycle skills (/interview, /outcome, /upskill, /gmail-sync).

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


class TestInterviewSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "interview" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "commands" / "interview.md"

    def test_interview_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/interview/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/commands/interview.md must exist")

    def test_interview_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "interview")
        self.assertTrue(data.get("description"), "interview skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "interview skill must be enabled by default")

    def test_interview_skill_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/commands/interview.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("edit_file", text)
        self.assertIn("run_command", text)
        self.assertIn("search_web", text)
        self.assertIn("ask_question", text)

    def test_interview_skill_references_methodology_files(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("07-interview-prep.md", text)
        self.assertIn("01-candidate-profile.md", text)
        self.assertIn("02-behavioral-profile.md", text)
        self.assertIn("04-job-evaluation.md", text)
        self.assertIn("09-web-research.md", text)

    def test_interview_skill_has_prep_pack_and_consistency_brief(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("interview_prep_<stage>.md", text)
        self.assertIn("Consistency Brief", text)
        self.assertIn("cv_draft.tex", text)
        self.assertIn("cover_letter.tex", text)
        self.assertIn("documents/applications/", text)

    def test_interview_skill_has_posting_guard_and_cache(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("posting_guard.py", text)
        self.assertIn("company_research", text)
        self.assertIn("Trust boundary", text)

    def test_interview_skill_has_mock_interview_and_profile_update(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Mock Interview", text)
        self.assertIn("01-candidate-profile.md", text)
        self.assertIn("/outcome", text)


class TestOutcomeSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "outcome" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "commands" / "outcome.md"

    def test_outcome_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/outcome/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/commands/outcome.md must exist")

    def test_outcome_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "outcome")
        self.assertTrue(data.get("description"), "outcome skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "outcome skill must be enabled by default")

    def test_outcome_skill_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/commands/outcome.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("edit_file", text)
        self.assertIn("run_command", text)
        self.assertIn("ask_question", text)

    def test_outcome_skill_has_tracker_vocabulary_and_preservation(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("job_search_tracker.csv", text)
        for status in ["drafted", "applied", "interview", "offer", "hired", "rejected", "no_response", "offer_declined", "withdrawn"]:
            self.assertIn(status, text)
        self.assertIn("deadline", text)
        self.assertIn("commas", text)

    def test_outcome_skill_has_archiving_and_idempotency(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("outcome.md", text)
        self.assertIn("documents/README.md", text)
        self.assertIn("cv_draft.tex", text)
        self.assertIn("cover_letter.tex", text)
        self.assertIn("posting_guard.py", text)

    def test_outcome_skill_has_followup_and_stale_branches(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Step 2b", text)
        self.assertIn("followup", text)
        self.assertIn("Step 2c", text)
        self.assertIn("Stale Sweep", text)
        self.assertIn("ask_question", text)

    def test_outcome_skill_has_calibration_and_coffee(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("/setup", text)
        self.assertIn("buying it a coffee", text)


class TestUpskillSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "upskill" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "skills" / "upskill" / "SKILL.md"

    def test_upskill_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/upskill/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/skills/upskill/SKILL.md must exist")

    def test_upskill_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "upskill")
        self.assertTrue(data.get("description"), "upskill skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "upskill skill must be enabled by default")

    def test_upskill_skill_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/skills/upskill/SKILL.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("search_web", text)
        self.assertIn("fetch_page.py", text)

    def test_upskill_skill_has_aggregate_and_targeted_modes(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Aggregate Mode", text)
        self.assertIn("Targeted Mode", text)
        self.assertIn("job_search_tracker.csv", text)
        self.assertIn("seen_jobs.json", text)
        self.assertIn("rank_score", text)

    def test_upskill_skill_has_two_pass_gap_analysis(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Pass 1", text)
        self.assertIn("Pass 2", text)
        self.assertIn("[domain]", text)
        self.assertIn("[soft]", text)
        self.assertIn("[tooling]", text)
        self.assertIn("[credential]", text)
        self.assertIn("01-candidate-profile.md", text)

    def test_upskill_skill_has_heatmap_and_learning_plan(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Gap Heatmap", text)
        self.assertIn("Critical", text)
        self.assertIn("High", text)
        self.assertIn("Learning Plan", text)
        self.assertIn("search_web", text)
        self.assertIn("2026", text)
        self.assertIn("Suggested Study Order", text)

    def test_upskill_skill_has_report_saving_and_diff(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("upskill/report-", text)
        self.assertIn("Since Last Report", text)


class TestGmailSyncSkill(unittest.TestCase):
    def setUp(self):
        self.skill_file = AGENTS_SKILLS_DIR / "gmail-sync" / "SKILL.md"
        self.canonical_file = REPO_ROOT / ".claude" / "commands" / "gmail-sync.md"

    def test_gmail_sync_skill_file_exists(self):
        self.assertTrue(self.skill_file.is_file(), ".agents/skills/gmail-sync/SKILL.md must exist")
        self.assertTrue(self.canonical_file.is_file(), ".claude/commands/gmail-sync.md must exist")

    def test_gmail_sync_skill_frontmatter(self):
        data = _parse_frontmatter(self.skill_file)
        self.assertEqual(data.get("name"), "gmail-sync")
        self.assertTrue(data.get("description"), "gmail-sync skill must have a non-empty description")
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertEqual(data.get("context"), "fork")
        self.assertTrue(data.get("enabled"), "gmail-sync skill must be enabled by default")

    def test_gmail_sync_skill_references_canonical_spec(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn(".claude/commands/gmail-sync.md", text)
        self.assertIn("Tool Translation Matrix", text)
        self.assertIn("read_file", text)
        self.assertIn("write_file", text)
        self.assertIn("edit_file", text)
        self.assertIn("ask_question", text)

    def test_gmail_sync_skill_has_trust_boundary_and_state(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Trust boundary", text)
        self.assertIn("gmail_sync/state.json", text)
        self.assertIn("processed_message_ids", text)
        self.assertIn("newer_than", text)

    def test_gmail_sync_skill_has_propose_and_approve_gate(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Proposed Updates", text)
        self.assertIn("Approval Gate", text)
        self.assertIn("approve all", text)
        self.assertIn("offer_declined", text)

    def test_gmail_sync_skill_has_signal_classification(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("Application ack", text)
        self.assertIn("OA / Assessment", text)
        self.assertIn("Interview invite", text)
        self.assertIn("Offer extended", text)
        self.assertIn("Rejection", text)

    def test_gmail_sync_skill_has_tracker_and_archive_writing(self):
        text = self.skill_file.read_text(encoding="utf-8")
        self.assertIn("job_search_tracker.csv", text)
        self.assertIn("outcome.md", text)
        self.assertIn("commas", text)
        self.assertIn("drafted", text)
        self.assertIn("30+ days", text)


class TestCMD4Integration(unittest.TestCase):
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
