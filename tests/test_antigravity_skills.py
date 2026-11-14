#!/usr/bin/env python3
"""Unified test suite for Antigravity skills and runtime integration.

Validates all 21 skills under .agents/skills/ (15 workflow skills + 6 portal skills):
- Frontmatter integrity and directory name parity
- Canonical specification pointer validity
- Runtime Tool Translation Matrix definitions
- Portal CLI contracts and allowed-tools scoping
- Integration with lint_skills.py, security_guards.py, check_framework_version.py,
  and check_upstream_updates.py
"""

from __future__ import annotations

import re
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

WORKFLOW_SKILLS = {
    "setup": ".claude/commands/setup.md",
    "reset": ".claude/commands/reset.md",
    "expand": ".claude/commands/expand.md",
    "scrape": ".claude/skills/job-scraper/SKILL.md",
    "rank": ".claude/commands/rank.md",
    "apply": ".claude/commands/apply.md",
    "job-application-assistant": ".claude/skills/job-application-assistant/SKILL.md",
    "interview": ".claude/commands/interview.md",
    "outcome": ".claude/commands/outcome.md",
    "upskill": ".claude/skills/upskill/SKILL.md",
    "gmail-sync": ".claude/commands/gmail-sync.md",
    "add-template": ".claude/commands/add-template.md",
    "add-portal": ".claude/commands/add-portal.md",
    "html-report": ".claude/commands/html-report.md",
    "notion-sync": ".claude/commands/notion-sync.md",
}

PORTAL_SKILLS = {
    "jobbank-search",
    "jobdanmark-search",
    "jobindex-search",
    "jobnet-search",
    "linkedin-search",
    "freehire-search",
}

ALL_EXPECTED_SKILLS = set(WORKFLOW_SKILLS.keys()) | PORTAL_SKILLS


def _parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    if yaml is None:
        # Fallback simple line-based parser
        data = {}
        for line in text[4:end].splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip().strip('"').strip("'")
        return data
    return yaml.safe_load(text[4:end]) or {}


class TestAntigravitySkillsCatalog(unittest.TestCase):
    def test_skills_directory_exists(self):
        self.assertTrue(AGENTS_SKILLS_DIR.is_dir(), ".agents/skills/ directory must exist")

    def test_all_expected_skills_present(self):
        present_dirs = {p.name for p in AGENTS_SKILLS_DIR.iterdir() if p.is_dir()}
        self.assertEqual(
            present_dirs,
            ALL_EXPECTED_SKILLS,
            f"Skill directory mismatch. Missing: {ALL_EXPECTED_SKILLS - present_dirs}, Extra: {present_dirs - ALL_EXPECTED_SKILLS}",
        )
        self.assertEqual(len(present_dirs), 21, "Total skill count must be exactly 21")

    def test_every_skill_has_skill_md(self):
        for skill_name in ALL_EXPECTED_SKILLS:
            skill_file = AGENTS_SKILLS_DIR / skill_name / "SKILL.md"
            self.assertTrue(skill_file.is_file(), f"Missing SKILL.md in {skill_name}")


class TestSkillFrontmatterAndParity(unittest.TestCase):
    def test_frontmatter_validity_and_name_parity(self):
        for skill_name in sorted(ALL_EXPECTED_SKILLS):
            skill_file = AGENTS_SKILLS_DIR / skill_name / "SKILL.md"
            data = _parse_frontmatter(skill_file)
            self.assertTrue(data, f"{skill_file} frontmatter failed to parse or is empty")
            self.assertEqual(
                data.get("name"),
                skill_name,
                f"Frontmatter name '{data.get('name')}' must match directory '{skill_name}'",
            )
            desc = data.get("description")
            self.assertIsInstance(desc, str, f"{skill_name} description must be a string")
            self.assertTrue(len(desc.strip()) > 10, f"{skill_name} description is too short")

    def test_workflow_skills_metadata(self):
        for skill_name in sorted(WORKFLOW_SKILLS.keys()):
            skill_file = AGENTS_SKILLS_DIR / skill_name / "SKILL.md"
            data = _parse_frontmatter(skill_file)
            self.assertEqual(data.get("context"), "fork", f"{skill_name} must specify 'context: fork'")
            self.assertTrue(data.get("enabled"), f"{skill_name} must specify 'enabled: true'")
            self.assertTrue(data.get("version"), f"{skill_name} must declare a version")


class TestCanonicalSpecPointers(unittest.TestCase):
    def test_workflow_skills_point_to_valid_canonical_specs(self):
        for skill_name, canonical_rel_path in WORKFLOW_SKILLS.items():
            skill_file = AGENTS_SKILLS_DIR / skill_name / "SKILL.md"
            canonical_file = REPO_ROOT / canonical_rel_path
            self.assertTrue(
                canonical_file.exists(),
                f"Canonical spec {canonical_rel_path} referenced by {skill_name} does not exist",
            )
            text = skill_file.read_text(encoding="utf-8")
            self.assertIn(
                canonical_rel_path,
                text,
                f"{skill_name}/SKILL.md must explicitly reference canonical spec {canonical_rel_path}",
            )

    def test_no_broken_canonical_references_in_any_skill(self):
        for skill_path in AGENTS_SKILLS_DIR.glob("*/SKILL.md"):
            text = skill_path.read_text(encoding="utf-8")
            matches = re.finditer(r"\.claude/(?:commands|skills)/[A-Za-z0-9_./-]+", text)
            for m in matches:
                ref = m.group(0).rstrip(".,;:)'\"`")
                target = REPO_ROOT / ref
                self.assertTrue(
                    target.exists(),
                    f"{skill_path.relative_to(REPO_ROOT)} references non-existent path {ref}",
                )


class TestRuntimeToolTranslationMatrix(unittest.TestCase):
    CORE_TOOLS = ["read_file"]
    COMMAND_RUN_SKILLS = {
        "setup",
        "reset",
        "expand",
        "scrape",
        "rank",
        "apply",
        "interview",
        "outcome",
        "upskill",
        "add-template",
        "add-portal",
        "html-report",
    }
    SUBAGENT_SKILLS = {"apply", "rank", "scrape", "setup"}
    INTERACTIVE_SKILLS = {
        "setup",
        "reset",
        "expand",
        "add-portal",
        "add-template",
        "interview",
        "gmail-sync",
    }

    def test_workflow_skills_define_translation_matrix(self):
        for skill_name in sorted(WORKFLOW_SKILLS.keys()):
            skill_file = AGENTS_SKILLS_DIR / skill_name / "SKILL.md"
            text = skill_file.read_text(encoding="utf-8")
            self.assertIn(
                "Tool Translation Matrix",
                text,
                f"{skill_name}/SKILL.md must contain a 'Tool Translation Matrix' section",
            )
            for tool in self.CORE_TOOLS:
                self.assertIn(
                    tool,
                    text,
                    f"{skill_name}/SKILL.md translation matrix must specify Antigravity tool '{tool}'",
                )

    def test_command_skills_specify_run_command(self):
        for skill_name in sorted(self.COMMAND_RUN_SKILLS):
            skill_file = AGENTS_SKILLS_DIR / skill_name / "SKILL.md"
            text = skill_file.read_text(encoding="utf-8")
            self.assertIn(
                "run_command",
                text,
                f"{skill_name}/SKILL.md translation matrix must specify Antigravity tool 'run_command'",
            )

    def test_subagent_skills_specify_invoke_subagent(self):
        for skill_name in sorted(self.SUBAGENT_SKILLS):
            skill_file = AGENTS_SKILLS_DIR / skill_name / "SKILL.md"
            text = skill_file.read_text(encoding="utf-8")
            self.assertIn(
                "invoke_subagent",
                text,
                f"{skill_name}/SKILL.md translation matrix must specify Antigravity tool 'invoke_subagent'",
            )

    def test_interactive_skills_specify_ask_question(self):
        for skill_name in sorted(self.INTERACTIVE_SKILLS):
            skill_file = AGENTS_SKILLS_DIR / skill_name / "SKILL.md"
            text = skill_file.read_text(encoding="utf-8")
            self.assertIn(
                "ask_question",
                text,
                f"{skill_name}/SKILL.md translation matrix must specify Antigravity tool 'ask_question'",
            )


class TestPortalSkillsContract(unittest.TestCase):
    def test_portal_skills_have_cli_or_executable(self):
        for portal in sorted(PORTAL_SKILLS):
            portal_dir = AGENTS_SKILLS_DIR / portal
            cli_ts = portal_dir / "cli" / "src" / "cli.ts"
            self.assertTrue(
                cli_ts.is_file(),
                f"Portal skill {portal} must provide CLI at cli/src/cli.ts",
            )

    def test_portal_skills_allowed_tools_scoped(self):
        for portal in sorted(PORTAL_SKILLS):
            skill_file = AGENTS_SKILLS_DIR / portal / "SKILL.md"
            text = skill_file.read_text(encoding="utf-8")
            self.assertIn("allowed-tools:", text, f"{portal}/SKILL.md must declare allowed-tools")
            self.assertIn(
                f"bun run .agents/skills/{portal}/cli/src/cli.ts",
                text,
                f"{portal}/SKILL.md allowed-tools must be strictly scoped to its own CLI",
            )


class TestVerificationToolchainIntegration(unittest.TestCase):
    def test_lint_skills_passes(self):
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "lint_skills.py")],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"lint_skills failed:\n{proc.stdout}\n{proc.stderr}")
        self.assertIn("lint_skills: OK (24 skills, 12 commands, settings.json)", proc.stdout)

    def test_security_guards_passes(self):
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "security_guards.py")],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"security_guards failed:\n{proc.stdout}\n{proc.stderr}")
        self.assertIn("security_guards: OK", proc.stdout)

    def test_antigravity_subagents_validation_passes(self):
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "antigravity_subagents.py"), "validate"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"antigravity_subagents validation failed:\n{proc.stdout}\n{proc.stderr}")

    def test_check_framework_version_passes(self):
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "check_framework_version.py")],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"check_framework_version failed:\n{proc.stdout}\n{proc.stderr}")


class TestUpstreamCompatibility(unittest.TestCase):
    def test_check_upstream_updates_runs_cleanly(self):
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "check_upstream_updates.py"), "--no-fetch"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"check_upstream_updates failed:\n{proc.stdout}\n{proc.stderr}")
        self.assertIn("All framework files are up to date", proc.stdout)


if __name__ == "__main__":
    unittest.main()
