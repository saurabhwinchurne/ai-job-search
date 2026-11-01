# Project Context & Ticket Progress Ledger

> **Single Source of Truth for Session Continuity:** This file tracks all ongoing ticket progress, architectural decisions, and handoff context across agent turns. Keep this updated per [.agents/rules/rules.md](.agents/rules/rules.md).

---

## 1. Project Overview & Dashboard

- **Project:** Native Google Antigravity, Antigravity IDE, and `agy` CLI support for AI Job Search
- **Repository:** `https://github.com/saurabhwinchurne/ai-job-search`
- **Kanban Board:** [GitHub Project #4 (@saurabhwinchurne's ai-job-search)](https://github.com/users/saurabhwinchurne/projects/4)
- **Current Phase:** Planning Approved & Baseline Established. Ready for Ticket Execution.
- **Active Ticket:** *None (No ticket started yet; strictly planning mode)*

---

## 2. Master Work Items & Status

| Issue # | Scope | Title | Status | Branch | PR |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [#1](https://github.com/saurabhwinchurne/ai-job-search/issues/1) | `[ARCH-1]` | Foundation & Runtime Bridge — Native Antigravity Rules & Single Source of Truth | `Todo` | - | - |
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

*(Entries are added here as tickets are picked up, implemented, and reviewed.)*

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

