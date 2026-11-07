---
name: setup
version: 1.0.0
description: >
  Profile onboarding wizard. Populates CLAUDE.md, the seven job-application-assistant
  skill files, the LaTeX CV template, and the job-search query file from your documents
  folder, a single CV paste, or an interactive interview. Run once when you first clone
  the repo; re-run with --section <name> to update a specific section (e.g.
  /setup --section search to reconfigure job-search queries).
  Trigger phrases: setup, onboarding, fill my profile, configure my profile, /setup,
  set up job search, initialize profile.
context: fork
enabled: true
---

# /setup — Profile Onboarding

> **Canonical spec:** `.claude/commands/setup.md`
> Read and follow that file's instructions exactly, translating each tool call to
> Antigravity equivalents per the matrix below.

## Tool Translation Matrix

| Canonical (Claude Code) | Antigravity Native |
|-------------------------|--------------------|
| `View` / `Read`         | `read_file`        |
| `Glob`                  | `run_command` with `find` / `ls` |
| `Edit`                  | `edit_file`        |
| `Write`                 | `write_file`       |
| `Bash`                  | `run_command`      |
| `WebFetch` / `WebSearch`| `search_web` + `run_command` with `python3 tools/fetch_page.py <url>` |
| `AskUserQuestion`       | `ask_question` (multi-choice) or plain-text prompt (open-ended) |
| `Agent`                 | `invoke_subagent`  |

## Runtime Notes for Antigravity

### @-Mention Shortcut (Antigravity IDE / `agy` CLI)

In Antigravity IDE and the `agy` CLI you can @-mention files directly in the chat. Use
this to hand documents to `/setup` without manual copy-paste:

```
/setup @documents/cv/my-cv.pdf @documents/linkedin/linkedin-profile.pdf
```

Each `@`-mentioned file is passed as an argument path. When one or more files are
@-mentioned, treat the invocation as **Path B (single document import)** in the
canonical spec — read the first @-mentioned file as the primary CV and any additional
files as supplementary sources.

### Path Selection (`ask_question`)

Use `ask_question` with `options` for the three-path selection (A / B / C) and for the
"apply all additive changes?" confirmation. Example:

```python
ask_question(questions=[{
    "question": "Which setup path would you like?",
    "options": [
        "(Recommended) Path A: Read my documents/ folder",
        "Path B: Single CV import",
        "Path C: Interview mode (guided questions)"
    ],
    "is_multi_select": False
}])
```

For open-ended sections (biography, career goals, deal-breakers) use a plain-text reply
prompt — no multi-choice needed.

### Public-Fork Preflight

Run `git remote get-url origin` via `run_command` for the public-fork check in Step 0.
If the remote is a GitHub fork and `gh` is available, run
`gh repo view <owner/repo> --json visibility,isFork` to check visibility.
The privacy warning must fire **before** any file is written (Step 0 of the canonical
spec). Do not defer it to the closing notes.

### Document Discovery

Use `run_command` with `find documents -type f` to list files inside `documents/`. Do
not use a bare Glob — `find` traverses hidden entries and nested subfolders uniformly.

## Read the Canonical Spec

Now read `.claude/commands/setup.md` and follow it step-by-step, applying the tool
translations above.
