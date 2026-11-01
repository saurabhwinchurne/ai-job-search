---
trigger: always_on
---

# AI Rules

> These rules are auto-loaded by Antigravity IDE from `.agents/rules/`.

## Branching & PR Lifecycle
These rules govern every ticket from start to close. No exceptions.

**Branch creation:** Before starting work on any ticket, create a dedicated local branch:
`git checkout -b feature/[TICKET-ID]-short-description`
Move the ticket to In Progress on the Kanban board. No commits go directly to main.

**Commit messages:** Reference the ticket ID in every commit:
`[TICKET-ID] Short description of what this commit does`

**PR creation:** 
- PR title: [TICKET-ID] Short description
- PR description: reference the ticket, include a walkthrough summary, add screenshots for UI changes, list test results
- Assign the PR to the human for review
- Move the ticket to In Review on the Kanban board
- **The AI must NOT merge the PR. Merging is exclusively the human's action.**

**After human merges:** Once the human merges the PR to main:
1. Close the ticket with a comment: "Completed in PR #[number]. Merged to main on [date]. [Brief summary.]"
2. Append a CHANGELOG.md entry under [Unreleased]
3. Delete the feature branch locally and remotely
4. Move the ticket to Done on the Kanban board

## Project Management Dashboard
Use github project features to manage project. Create kanban board under `Projects` of github repo if not exists or use existing kanban board and create all the tickets to work on this project under `Work Items` of github project.

**Kanban Board to Use:** https://github.com/users/saurabhwinchurne/projects/4

## Kanban WIP Limits
- In Progress: max 2 tickets. Complete or unblock before picking up another.
- In Review: max 3 tickets.
- Always pull from Ready column, highest priority first. Never self-assign from Backlog.

## Ticket Context & Progress Tracking (`CONTEXT.md`)
To maintain complete context, progress history, and architectural continuity across agent sessions:
- Maintain a persistent living document `CONTEXT.md` at the project root capturing the state and context of all tickets.
- **When starting a ticket:** Update `CONTEXT.md` with the active Ticket ID, feature branch, goal, and planned approach before writing code.
- **During implementation:** Log key technical decisions, trade-offs, schemas, and modified file paths.
- **When opening a PR / closing a ticket:** Record the PR link, summary of changes, test verification results, and acceptance criteria fulfilled.
- **Sync Knowledge Graph:** Whenever `CONTEXT.md` is updated with a phase change or new ticket status, run `graphify update .` to keep the codebase knowledge graph in sync.

## Starting a Ticket: Standard Agent Prompt
When prompting the agent to start working on any ticket from the Kanban board, use the standard prompt template below to ensure full compliance with the workflow, context ledger, and signing requirements:

```text
/graphify /plan
Please start working on Ticket #[TICKET-ID]: [TICKET-TITLE] from the Kanban board (https://github.com/users/saurabhwinchurne/projects/4).

Follow the project lifecycle rules strictly:
1. Inspect the ticket details, scope, and acceptance criteria via GitHub MCP.
2. Create and switch to the dedicated feature branch:
   git checkout -b feature/[TICKET-ID]-[short-description]
3. Update the ticket status to 'In Progress' on the Kanban board.
4. Update `CONTEXT.md` with the active Ticket ID, branch name, goal, and planned technical approach, then run `graphify update .`.
5. Implement the solution adhering to the 7-rung ladder (ponytail) and security rules.
6. Commit all changes with signed commits using `git commit -S -m "[TICKET-ID] Short description"`.
7. Push the branch using `bash -ic "git push origin feature/[TICKET-ID]-[short-description]"`.
8. Create a PR assigned to the human reviewer, update `CONTEXT.md` with the PR link, move the ticket to 'In Review' on the Kanban board, and do NOT merge the PR.
```

## ponytail — YAGNI-First Code Rule (full mode)
Before writing any code, run the 7-rung ladder:
1. Does this need to exist? → no: skip it
2. Already in this codebase? → reuse it
3. Does stdlib do it? → use it
4. Installed dependency? → use it
5. One line? → one line
6. Only then: the minimum that works
Mark deliberate shortcuts with a `# ponytail: [ceiling] [upgrade-path]` comment.

## Security
- Never commit API keys, tokens, or passwords. Always use .env (gitignored).
- Keep .env.example updated whenever a new environment variable is added.

## graphify — Knowledge Graph Maintenance
To maintain context and prevent architectural drift, the following graphify workflows must be strictly followed:

### Keep the Graph Synced
Whenever the architecture, folder structure, or Current Phase changes (e.g., updating `CONTEXT.md`), run:
```bash
graphify update .
```
This keeps the machine-readable graph in sync with the actual codebase.

### PR Conflict Detection
Before creating a Pull Request, run:
```bash
graphify prs --conflicts
```
This identifies other open PRs that share graph communities with your changes (i.e., PRs touching related code). Critical given our github project board has multiple planned, overlapping tasks.

### Architecture Review & Callflows
Run the callflow export after significant feature work (not just at the start of the project):
```bash
graphify export callflow-html
```
The Mermaid call-flow diagrams are useful for code reviews and keeping the architecture picture updated as the project evolves.

## GitHub MCP
For any GitHub issues, PRs, labels, or related metadata operations, ALWAYS use the GitHub MCP.

## Git — SSH Authentication & Commit Signing
This project's GitHub remote uses SSH (`git@github.com:...`). The user loads their SSH key passphrase
into `ssh-agent` at login. For the AI agent to run `git push`, `git pull`, `git fetch`, or any git
command that requires SSH authentication, the command **must** be invoked with `bash -ic` so the
ssh-agent environment is inherited:

```bash
bash -ic "git push origin main"
bash -ic "git pull origin main"
```

**Never** run bare `git push` — it will fail with an SSH passphrase prompt. Always wrap in `bash -ic`.

Whenever creating a git commit, you MUST use the `-S` flag (e.g., `git commit -S -m "..."`) to sign the commit with the configured SSH key.