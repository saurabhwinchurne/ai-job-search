# Project Context & Ticket Progress Ledger

> **Single Source of Truth for Session Continuity:** This file tracks all ongoing ticket progress, architectural decisions, and handoff context across agent turns. Keep this updated per [.agents/rules/rules.md](.agents/rules/rules.md).

---

## 1. Project Overview & Dashboard

- **Project:** Native Google Antigravity, Antigravity IDE, and `agy` CLI support for AI Job Search
- **Repository:** `https://github.com/saurabhwinchurne/ai-job-search`
- **Kanban Board:** [GitHub Project #4 (@saurabhwinchurne's ai-job-search)](https://github.com/users/saurabhwinchurne/projects/4)
- **Current Phase:** Ticket Execution: ARCH-1 In Progress.
- **Active Ticket:** Ticket #1: [ARCH-1] Foundation & Runtime Bridge — Native Antigravity Rules & Single Source of Truth Configuration
- **Active Branch:** `feature/ARCH-1-foundation-runtime-bridge`

---

## 2. Master Work Items & Status

| Issue # | Scope | Title | Status | Branch | PR |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [#1](https://github.com/saurabhwinchurne/ai-job-search/issues/1) | `[ARCH-1]` | Foundation & Runtime Bridge — Native Antigravity Rules & Single Source of Truth | `In Progress` | `feature/ARCH-1-foundation-runtime-bridge` | - |
| [#2](https://github.com/saurabhwinchurne/ai-job-search/issues/2) | `[ARCH-2]` | Subagent Architecture — Antigravity Subagent Definitions & Tool Adapters | `Todo` | - | - |
| [#3](https://github.com/saurabhwinchurne/ai-job-search/issues/3) | `[CMD-1]` | Profile Onboarding & Management — Port `/setup`, `/reset`, and `/expand` | `Todo` | - | - |
| [#4](https://github.com/saurabhwinchurne/ai-job-search/issues/4) | `[CMD-2]` | Job Search & Triage Pipeline — Port `/scrape` and `/rank` Skills | `Todo` | - | - |
| [#5](https://github.com/saurabhwinchurne/ai-job-search/issues/5) | `[CMD-3]` | Core Application Engine — Port `/apply` and `job-application-assistant` | `Todo` | - | - |
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
- **Status:** In Progress
- **Goal:** Establish native Google Antigravity support by configuring the repository entry point and directory-level rules using the Thin-Pointer architecture, ensuring a single source of truth across AI runtimes.
- **Planned Approach:**
  - Create `GEMINI.md` at root pointing to candidate profile in `CLAUDE.md` and `.claude/skills/job-application-assistant/01-candidate-profile.md`, canonical workflow specs in `.claude/`, LaTeX and ATS verification checklists, and tool attribution guidelines.
  - Update `AGENTS.md` with multi-runtime hierarchy (Claude Code + Google Antigravity / Antigravity IDE / `agy` CLI), discovery roots, runtime tool translation matrix, and bump `framework_version` to `1.1.0`.
  - Maintain all security guards and linters.
- **Files Modified/Created:**
  - `GEMINI.md` (New)
  - `AGENTS.md` (Modified)
  - `CONTEXT.md` (Modified)
- **Verification:**
  - `python3 tools/check_framework_version.py` (Passed — version bumped to 1.1.0)
  - `python3 tools/security_guards.py` (Passed — 0 errors)
  - `python3 tools/lint_skills.py` (Passed — 0 errors)
  - `GIT_EDITOR=true python3 -m unittest discover -s tests` (Passed — 879 tests, 0 failures)
- **PR:** -

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

