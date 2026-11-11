# Project Context & Ticket Progress Ledger

> **Single Source of Truth for Session Continuity:** This file tracks all ongoing ticket progress, architectural decisions, and handoff context across agent turns. Keep this updated per [.agents/rules/rules.md](.agents/rules/rules.md).

---

## 1. Project Overview & Dashboard

- **Project:** Native Google Antigravity, Antigravity IDE, and `agy` CLI support for AI Job Search
- **Repository:** `https://github.com/saurabhwinchurne/ai-job-search`
- **Kanban Board:** [GitHub Project #4 (@saurabhwinchurne's ai-job-search)](https://github.com/users/saurabhwinchurne/projects/4)
- **Current Phase:** Ticket Execution: CMD-3 In Progress
- **Active Ticket:** Ticket #5: `[CMD-3] Core Application Engine — Port /apply and job-application-assistant Skills`
- **Active Branch:** `feature/CMD-3-core-application-engine`

---

## 2. Master Work Items & Status

| Issue # | Scope | Title | Status | Branch | PR |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [#1](https://github.com/saurabhwinchurne/ai-job-search/issues/1) | `[ARCH-1]` | Foundation & Runtime Bridge — Native Antigravity Rules & Single Source of Truth | `Done` | `feature/ARCH-1-foundation-runtime-bridge` | [#9](https://github.com/saurabhwinchurne/ai-job-search/pull/9) |
| [#2](https://github.com/saurabhwinchurne/ai-job-search/issues/2) | `[ARCH-2]` | Subagent Architecture — Antigravity Subagent Definitions & Tool Adapters | `Done` | `feature/ARCH-2-subagent-architecture` | [#10](https://github.com/saurabhwinchurne/ai-job-search/pull/10) |
| [#3](https://github.com/saurabhwinchurne/ai-job-search/issues/3) | `[CMD-1]` | Profile Onboarding & Management — Port `/setup`, `/reset`, and `/expand` | `Done` | `feature/CMD-1-profile-onboarding-skills` | [#11](https://github.com/saurabhwinchurne/ai-job-search/pull/11) |
| [#4](https://github.com/saurabhwinchurne/ai-job-search/issues/4) | `[CMD-2]` | Job Search & Triage Pipeline — Port `/scrape` and `/rank` Skills | `Done` | `feature/CMD-2-job-search-triage-pipeline` | [#12](https://github.com/saurabhwinchurne/ai-job-search/pull/12) |
| [#5](https://github.com/saurabhwinchurne/ai-job-search/issues/5) | `[CMD-3]` | Core Application Engine — Port `/apply` and `job-application-assistant` | `In Review` | `feature/CMD-3-core-application-engine` | [#13](https://github.com/saurabhwinchurne/ai-job-search/pull/13) |
| [#6](https://github.com/saurabhwinchurne/ai-job-search/issues/6) | `[CMD-4]` | Post-Application Lifecycle — Port `/interview`, `/outcome`, `/upskill`, `/gmail-sync` | `Todo` | - | - |
| [#7](https://github.com/saurabhwinchurne/ai-job-search/issues/7) | `[CMD-5]` | Customization & Reporting Tools — Port `/add-template`, `/add-portal`, `/html-report`, `/notion-sync` | `Todo` | - | - |
| [#8](https://github.com/saurabhwinchurne/ai-job-search/issues/8) | `[QA-1]` | Verification Suite, Tooling Hardening & Antigravity Documentation | `Todo` | - | - |

---

## 3. Key Architectural Decisions (ADRs)

1. **Thin-Pointer Single Source of Truth:**
   - To avoid configuration drift from upstream rebase, all workflow skills under `.agents/skills/<command>/SKILL.md` act as thin pointers to canonical `.claude/commands/` and `.claude/skills/` specs while translating runtime tools (`read_file`, `write_file`, `edit_file`, `run_command`, `ask_question`, `invoke_subagent`).
2. **Subagent Execution Strategy:**
   - Option A (Multi-Agent) is primary: dispatch worker agents (`posting-fetcher`, `posting-scorer`, `application-reviewer`) using Antigravity's `invoke_subagent` and `define_subagent` tools with isolated prompts.
   - Option B (In-Context) is transparent fallback: execute worker procedures directly in the conversation context when subagent spawning is unavailable.
3. **LaTeX Verification Toolchain:**
   - Local system does not currently have LaTeX compilers (`lualatex`/`xelatex`) installed. They will be installed or containerized when implementing Ticket #5 (`/apply`).
4. **Knowledge Graph Synchronization:**
   - Whenever `CONTEXT.md` is updated or phases change, run `graphify update .` to keep the code knowledge graph synchronized.

---

## 4. Ticket Execution Log

### [ARCH-1] Foundation & Runtime Bridge — Native Antigravity Rules & Single Source of Truth
- **Branch:** `feature/ARCH-1-foundation-runtime-bridge`
- **Status:** Done (Merged to master on 2026-11-01 in PR #9)
- **Goal:** Establish native Google Antigravity support by configuring the repository entry point and directory-level rules using the Thin-Pointer architecture, ensuring a single source of truth across AI runtimes.
- **Planned Approach:**
  - Create `GEMINI.md` at root pointing to candidate profile in `CLAUDE.md` and `.claude/skills/job-application-assistant/01-candidate-profile.md`, canonical workflow specs in `.claude/`, LaTeX and ATS verification checklists, and tool attribution guidelines.
  - Update `AGENTS.md` with multi-runtime hierarchy (Claude Code + Google Antigravity / Antigravity IDE / `agy` CLI), discovery roots, runtime tool translation matrix, and bump `framework_version` to `1.1.0`.
  - Maintain all security guards and linters.
- **Files Modified/Created:**
  - `GEMINI.md` (New)
  - `AGENTS.md` (Modified)
  - `CONTEXT.md` (Modified)
  - `CHANGELOG.md` (Appended under [Unreleased])
- **Verification:**
  - `python3 tools/check_framework_version.py` (Passed — version bumped to 1.1.0)
  - `python3 tools/security_guards.py` (Passed — 0 errors)
  - `python3 tools/lint_skills.py` (Passed — 0 errors)
  - `GIT_EDITOR=true python3 -m unittest discover -s tests` (Passed — 879 tests, 0 failures)
- **PR:** [#9](https://github.com/saurabhwinchurne/ai-job-search/pull/9)

---

### [ARCH-2] Subagent Architecture — Antigravity Subagent Definitions & Tool Adapters
- **Branch:** `feature/ARCH-2-subagent-architecture`
- **Status:** Done (Merged to master on 2026-11-01 in PR #10)
- **Goal:** Establish Antigravity-native subagent definitions and tool permission adapters for the three specialized worker agents (`posting-fetcher`, `posting-scorer`, `application-reviewer`), adhering to the workspace's trust boundaries, prompt injection defenses, and factual grounding rules.
- **Planned Approach:**
  - Create Antigravity subagent specifications under `.agents/subagents/`:
    - `posting-fetcher.md`: 4-level retrieval escalation ladder, `posting_guard.py` integrity gate, metadata & cleaned text output.
    - `posting-scorer.md`: batch fit triage, `posting_guard.py` integration, structured JSON array output.
    - `application-reviewer.md`: hiring-manager proxy persona, factual grounding audit, text diff suggestions, company research caching.
    - `README.md`: complete architecture, tool permissions, and invocation guide.
  - Implement tool adapter & CLI helper `tools/antigravity_subagents.py` to translate subagent specs into `define_subagent` and `invoke_subagent` parameters.
  - Extend `tools/security_guards.py` with `check_antigravity_subagents()` to enforce least-privilege tool grants, prompt injection defenses, and grounding rules.
  - Create unit test suite `tests/test_antigravity_subagents.py`.
  - Update `AGENTS.md` and `GEMINI.md` to reference `.agents/subagents/`.
- **Files Modified/Created:**
  - `.agents/subagents/posting-fetcher.md` (New)
  - `.agents/subagents/posting-scorer.md` (New)
  - `.agents/subagents/application-reviewer.md` (New)
  - `.agents/subagents/README.md` (New)
  - `tools/antigravity_subagents.py` (New)
  - `tools/security_guards.py` (Modified)
  - `tests/test_antigravity_subagents.py` (New)
  - `AGENTS.md` (Modified)
  - `GEMINI.md` (Modified)
  - `CONTEXT.md` (Modified)
- **Verification:**
  - `python3 -m unittest tests/test_antigravity_subagents.py` (Passed — 15 tests, 0 failures)
  - `python3 tools/security_guards.py` (Passed — 0 errors)
  - `python3 tools/lint_skills.py` (Passed — 0 errors)
  - `python3 tools/check_framework_version.py` (Passed — OK)
  - `python3 tools/antigravity_subagents.py validate` (Passed — OK)
  - `GIT_EDITOR=true python3 -m unittest discover -s tests` (Passed — 894 tests, 0 failures)
- **PR:** [#10](https://github.com/saurabhwinchurne/ai-job-search/pull/10)

---

### [CMD-1] Profile Onboarding & Management — Port /setup, /reset, and /expand Skills
- **Branch:** `feature/CMD-1-profile-onboarding-skills`
- **Status:** Done (Merged to master on 2026-11-08 in PR #11)
- **Goal:** Port the three canonical profile-management commands (`/setup`, `/reset`, `/expand`) to Antigravity-native skill specifications under `.agents/skills/` using the Thin-Pointer architecture, ensuring single-source-of-truth continuity and adding unit test coverage.
- **Planned Approach:**
  - Create `.agents/skills/setup/SKILL.md` wrapping `.claude/commands/setup.md` with tool translation matrix, Antigravity `@-mention` file shortcuts, public-fork preflight check, and `ask_question` interactive flow.
  - Create `.agents/skills/reset/SKILL.md` wrapping `.claude/commands/reset.md` with tool translation matrix, destructive prompt safeguards (`RESET` confirmation), and POSIX delete script specifications.
  - Create `.agents/skills/expand/SKILL.md` wrapping `.claude/commands/expand.md` with tool translation matrix, trust boundary rules from `09-web-research.md`, additive-only invariants, and `fetch_page.py` fallback notes.
  - Create `tests/test_cmd1_antigravity_skills.py` validating skill files exist, parse clean frontmatter, reference canonical specs, contain translation matrices, and pass linting & security guards.
  - Update `AGENTS.md` (bump `framework_version` to `1.1.2`), `GEMINI.md`, `CHANGELOG.md`, and `CONTEXT.md`.
- **Files Modified/Created:**
  - `.agents/skills/setup/SKILL.md` (New)
  - `.agents/skills/reset/SKILL.md` (New)
  - `.agents/skills/expand/SKILL.md` (New)
  - `tests/test_cmd1_antigravity_skills.py` (New)
  - `AGENTS.md` (Modified)
  - `GEMINI.md` (Modified)
  - `CHANGELOG.md` (Modified)
  - `CONTEXT.md` (Modified)
- **Verification:**
  - `python3 -m unittest tests/test_cmd1_antigravity_skills.py -v` (Passed — 14 tests, 0 failures)
  - `python3 tools/lint_skills.py` (Passed — 12 skills, 12 commands, settings.json)
  - `python3 tools/security_guards.py` (Passed — 0 errors)
  - `python3 tools/check_framework_version.py` (Passed — OK)
  - `GIT_EDITOR=true python3 -m unittest discover -s tests` (Passed — 908 tests, 0 failures)
- **PR:** [#11](https://github.com/saurabhwinchurne/ai-job-search/pull/11)

---

### [CMD-2] Job Search & Triage Pipeline — Port /scrape and /rank Skills
- **Branch:** `feature/CMD-2-job-search-triage-pipeline`
- **Status:** Done (Merged to master on 2026-11-08 in PR #12)
- **Goal:** Port the two canonical job-search-and-triage commands (`/scrape` from `.claude/skills/job-scraper/SKILL.md` and `/rank` from `.claude/commands/rank.md`) to Antigravity-native skill specifications under `.agents/skills/` using the Thin-Pointer architecture, enabling the full scrape→rank pipeline as Antigravity IDE / `agy` CLI slash commands.
- **Planned Approach:**
  - Create `.agents/skills/scrape/SKILL.md` wrapping `.claude/skills/job-scraper/SKILL.md` with tool translation matrix, parallel portal search via `invoke_subagent`, state tool usage (never read state directly), portal CLI discovery, trust boundary, health check, and referral link notes.
  - Create `.agents/skills/rank/SKILL.md` wrapping `.claude/commands/rank.md` with tool translation matrix, `posting-scorer` subagent dispatch via `invoke_subagent`, `rank_state.py` state management, profile/framework inline loading, posting guard, expiry sweep, score aggregation, and veto rules.
  - Create `tests/test_cmd2_antigravity_skills.py` validating skill files exist, parse clean frontmatter, reference canonical specs, contain translation matrices, and pass linting & security guards.
  - Update `AGENTS.md` (bump `framework_version` to `1.1.3`), `GEMINI.md`, `CHANGELOG.md`, and `CONTEXT.md`.
  - Update `tests/test_cmd1_antigravity_skills.py` skill count assertion from 12 to 14.
- **Files Modified/Created:**
  - `.agents/skills/scrape/SKILL.md` (New)
  - `.agents/skills/rank/SKILL.md` (New)
  - `tests/test_cmd2_antigravity_skills.py` (New)
  - `tests/test_cmd1_antigravity_skills.py` (Modified)
  - `AGENTS.md` (Modified)
  - `GEMINI.md` (Modified)
  - `CHANGELOG.md` (Modified)
  - `CONTEXT.md` (Modified)
- **Verification:**
  - `python3 -m unittest tests/test_cmd2_antigravity_skills.py -v` (Passed — 14 tests, 0 failures)
  - `python3 -m unittest tests/test_cmd1_antigravity_skills.py -v` (Passed — 14 tests, 0 failures)
  - `python3 tools/lint_skills.py` (Passed — 14 skills, 12 commands)
  - `python3 tools/security_guards.py` (Passed — 0 errors)
  - `python3 tools/check_framework_version.py` (Passed — OK)
  - `GIT_EDITOR=true python3 -m unittest discover -s tests` (Passed — 922 tests, 0 failures)
- **PR:** [#12](https://github.com/saurabhwinchurne/ai-job-search/pull/12)

---

### [CMD-3] Core Application Engine — Port /apply and job-application-assistant Skills
- **Branch:** `feature/CMD-3-core-application-engine`
- **Status:** In Review
- **Goal:** Port the core job application engine (`/apply` and `job-application-assistant`) to native Antigravity workspace skills under `.agents/skills/` using the Thin-Pointer architecture, executing the two-agent drafter/reviewer lifecycle, LaTeX compilation, ATS verification, application tracking, and unit test coverage.
- **Planned Approach:**
  - Create `.agents/skills/apply/SKILL.md` wrapping `.claude/commands/apply.md` with tool translation matrix, subagent orchestration (`posting-fetcher`, `application-reviewer`), active template resolution, strict page limits (2-page CV, 1-page cover letter), LaTeX/ATS verification (`verify_pdf.py`, `verify_layout.py`), application logging in `job_search_tracker.csv`, and posting archiving.
  - Create `.agents/skills/job-application-assistant/SKILL.md` wrapping `.claude/skills/job-application-assistant/SKILL.md` and referencing all 9 canonical methodology files (`01` through `09`) with tool translation matrix, trust boundary, and application recording.
  - Create `tests/test_cmd3_antigravity_skills.py` validating skill files exist, parse clean frontmatter, reference canonical specs, contain translation matrices, and pass linting & security guards.
  - Update skill count assertions in `tests/test_cmd1_antigravity_skills.py` and `tests/test_cmd2_antigravity_skills.py` from 14 to 16.
  - Update `AGENTS.md` (bump `framework_version` to `1.1.4`), `GEMINI.md`, `CHANGELOG.md`, and `CONTEXT.md`.
- **Files Modified/Created:**
  - `.agents/skills/apply/SKILL.md` (New)
  - `.agents/skills/job-application-assistant/SKILL.md` (New)
  - `tests/test_cmd3_antigravity_skills.py` (New)
  - `tests/test_cmd1_antigravity_skills.py` (Modified)
  - `tests/test_cmd2_antigravity_skills.py` (Modified)
  - `AGENTS.md` (Modified)
  - `GEMINI.md` (Modified)
  - `CHANGELOG.md` (Modified)
  - `CONTEXT.md` (Modified)
- **Verification:**
  - `python3 -m unittest tests/test_cmd3_antigravity_skills.py -v` (Passed — 16 tests, 0 failures)
  - `python3 -m unittest tests/test_cmd1_antigravity_skills.py tests/test_cmd2_antigravity_skills.py -v` (Passed — 28 tests, 0 failures)
  - `python3 tools/lint_skills.py` (Passed — 16 skills, 12 commands)
  - `python3 tools/security_guards.py` (Passed — 0 errors)
  - `python3 tools/check_framework_version.py` (Passed — OK)
  - `python3 tools/antigravity_subagents.py validate` (Passed — OK)
  - `GIT_EDITOR=true python3 -m unittest discover -s tests` (Passed — 938 tests, 0 failures)
- **PR:** [#13](https://github.com/saurabhwinchurne/ai-job-search/pull/13)

---

### Template for Ticket Updates:
```markdown
### [TICKET-ID] Short Title
- **Branch:** `feature/[TICKET-ID]-short-description`
- **Status:** In Progress | In Review | Done
- **Key Decisions & Changes:**
  - ...
- **Files Modified/Created:**
  - ...
- **Verification:**
  - Automated tests run and results
- **PR:** #...
```

