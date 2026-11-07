---
name: reset
version: 1.0.0
description: >
  Resets candidate profile data back to blank templates so you can re-run /setup from
  scratch. Supports three scopes — profile (clears the seven skill files), documents
  (deletes user-uploaded files from documents/), or all (both). Destructive: nothing is
  deleted until you type RESET to confirm. Trigger phrases: reset profile, clear profile,
  start over, /reset, wipe my profile, reset my job search data.
context: fork
enabled: true
---

# /reset — Reset Candidate Profile Data

> **Canonical spec:** `.claude/commands/reset.md`
> Read and follow that file's instructions exactly, translating each tool call to
> Antigravity equivalents per the matrix below.

> [!WARNING]
> This command is destructive. Nothing is deleted until the user explicitly types `RESET`
> (all caps) to confirm. Always show the full preview of what will be cleared before
> presenting the confirmation prompt.

## Tool Translation Matrix

| Canonical (Claude Code) | Antigravity Native |
|-------------------------|--------------------|
| `View` / `Read`         | `read_file`        |
| `Glob`                  | `run_command` with `find` / `ls` |
| `Edit`                  | `edit_file`        |
| `Write`                 | `write_file`       |
| `Bash`                  | `run_command`      |
| `AskUserQuestion`       | `ask_question`     |

## Runtime Notes for Antigravity

### Scope Selection (`ask_question`)

Use `ask_question` for the scope selection when `$ARGUMENTS` does not contain a
recognized scope keyword:

```python
ask_question(questions=[{
    "question": "What would you like to reset?",
    "options": [
        "profile — Clear skill files only (re-run /setup after)",
        "documents — Delete files from documents/ folder only",
        "all — Both profile skill files and documents folder"
    ],
    "is_multi_select": False
}])
```

### RESET Confirmation

Present the confirmation as a plain-text prompt — the user must type `RESET` (all caps)
exactly. Do **not** use `ask_question` with pre-set options here; the exact string match
is a deliberate safeguard against accidental confirmation.

### POSIX Delete Block

The shell delete block in Step 3 must be executed via `run_command` exactly as written
in the canonical spec. Do not rewrite or abbreviate it. The script uses POSIX shell
(`set -e`, `find`, `rm -rf`) so it runs correctly under both bash and zsh.

After executing the delete block, verify each subfolder with `run_command` using `ls`
to confirm only `.gitkeep` remains.

### Profile Rewrite

For the full-file rewrites (`01-candidate-profile.md`, `02-behavioral-profile.md`), use
`write_file` with `Overwrite=true`. For partial resets (`04-job-evaluation.md`,
`05-cv-templates.md`, `06-cover-letter-templates.md`, `07-interview-prep.md`,
`search-queries.md`), use `edit_file` to replace only the candidate-data sections.
Never rewrite the frontmatter `---` block of any skill file.

## Read the Canonical Spec

Now read `.claude/commands/reset.md` and follow it step-by-step, applying the tool
translations above.
