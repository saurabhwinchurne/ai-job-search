---
name: rank
version: 1.0.0
description: >
  Batch-scores scraped jobs against the fit framework and returns a ranked shortlist.
  Dispatches posting-scorer subagents for parallel triage. Trigger phrases: rank jobs,
  triage jobs, score jobs, prioritize jobs, /rank
context: fork
enabled: true
---

# /rank — Triage Scraped Jobs into a Ranked Shortlist

> **Canonical spec:** `.claude/commands/rank.md`
> Read and follow that file's instructions exactly, translating each tool call to
> Antigravity equivalents per the matrix below.

> [!IMPORTANT]
> `/rank` produces **triage scores**, not final evaluations. It scores from the posting
> text and the candidate profile only — no company research, no reviewer agent. `/apply`'s
> Step 1 evaluation remains authoritative.

## Tool Translation Matrix

| Canonical (Claude Code) | Antigravity Native |
|-------------------------|---------------------|
| `View` / `Read`         | `read_file`         |
| `Glob`                  | `run_command` with `find` / `ls` |
| `Edit`                  | `edit_file`         |
| `Write`                 | `write_file`        |
| `Bash`                  | `run_command`       |
| `WebFetch` / `WebSearch`| `search_web` + `run_command` with `python3 tools/fetch_page.py <url>` |
| `AskUserQuestion`       | `ask_question` (multi-choice) or plain-text prompt (open-ended) |
| `Agent`                 | `invoke_subagent`   |

## Runtime Notes for Antigravity

### State Tool Usage (Never Read State Directly)

All state reads and writes go through `run_command` with `tools/rank_state.py`.
**Never** read `job_scraper/seen_jobs.json` directly into the conversation:

- **Load candidates:** `python3 tools/rank_state.py candidates --limit 10`
  (add `--all` / `--focus "<text>"` per Step 0 arguments)
- **Write results:** `python3 tools/rank_state.py apply --results "<temp file>"`
- **Expiry sweep:** `python3 tools/rank_state.py sweep --write --exclude "<keys>"`

If `candidates` exits with "not found", tell the user to run `/scrape` first and stop.
If it reports no candidates, skip to the sweep-only path (canonical spec Step 1).

### Profile and Framework Loading

In Step 1, read the scoring framework and candidate profile **once** via `read_file`:
- `.claude/skills/job-application-assistant/04-job-evaluation.md`
- `.claude/skills/job-application-assistant/01-candidate-profile.md`

Extract a compact rubric (strong/moderate/weak skill match, experience domains,
behavioral thrive/drain, career goals, deal-breakers, location constraints) and pass
it **inline** to each subagent prompt. Do not make subagents re-read the profile files.

### Subagent Dispatch (`invoke_subagent`)

In Step 2, use `invoke_subagent` with the `posting-scorer` subagent specification from
`.agents/subagents/posting-scorer.md`. Dispatch **~5 jobs per subagent** and invoke
**all subagents in the same response** so they run concurrently.

Each subagent receives inline:
1. The job list (title, company, URL, key)
2. The compact scoring rubric extracted from the profile
3. The JSON output schema from the canonical spec's Step 2
4. The trust-boundary and posting-guard instructions
5. The fetch escalation order from `09-web-research.md`

Use `tools/antigravity_subagents.py` to load the subagent definition if needed:
```bash
python3 tools/antigravity_subagents.py load posting-scorer
```

### Posting Integrity Gate

Every posting fetched by a scoring subagent must pass through `tools/posting_guard.py`
before scoring. Include this instruction in every scoring agent's prompt:

- Portal CLI: `... detail '<URL>' --format plain | python3 tools/posting_guard.py --text --json`
- `fetch_page.py` output: `python3 tools/posting_guard.py --in "<file>" --html --json`
- WebSearch text: pipe through `python3 tools/posting_guard.py --text --json`

The agent scores from the **cleaned** text and returns the gate's verdict as `"guard"`.

### Temporary Files for Results

Collect subagent JSON arrays into a temporary file outside the repo tree (e.g., a
scratch directory or `/tmp`) for `rank_state.py apply`. Never commit temporary files.

### Expiry Sweep (Mandatory)

Step 3's rule 6 sweep **always runs**, even when no new candidates exist. Execute via
`run_command`:

```bash
python3 tools/rank_state.py sweep --write --exclude "<keys scored this run>"
```

This retires ranked entries whose stored deadline has passed and flags entries closing
within 7 days. It costs no fetch — it is a date comparison against stored values.

### Score Aggregation

Back in the main context after subagents return, compute the overall score with the
weighting from `04-job-evaluation.md`:
- Technical Skills: 30%
- Experience Match: 25%
- Behavioral Fit: 15%
- Career Alignment: 30%

Location is pass/fail (unweighted). Apply the verdict bands:
- **Strong Fit** (75+), **Good Fit** (60–74), **Moderate Fit** (45–59),
  **Weak Fit** (30–44), **Poor Fit** (<30)

### Veto Rules

- `location_verdict: FAIL` → excluded from shortlist
- `language_gate: FAIL` → excluded from shortlist
- `location_verdict: FLAG` / `language_gate: FLAG` → stays in ranking with ⚠ marker
- Deadline within 7 days → 🔥 marker, wins ties
- Deadline passed → status becomes `expired`
- `posted_date` > 30 days old → ⚠ staleness marker

## Read the Canonical Spec

Now read `.claude/commands/rank.md` and follow it step-by-step, applying the tool
translations above.
