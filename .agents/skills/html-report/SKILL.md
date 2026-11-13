---
name: html-report
version: 1.0.0
description: >
  Generates a self-contained offline HTML application tracker dashboard with inline SVG charts
  and filterable tables from job_search_tracker.csv and application archives.
  Triggers on: html-report, dashboard, application report, tracker report, visual report, /html-report
context: fork
enabled: true
---

# /html-report — Generate Application Tracker Dashboard

> **Canonical spec:** `.claude/commands/html-report.md`
> Read and follow that file's instructions exactly, translating each tool call to
> Antigravity equivalents per the matrix below.

> [!NOTE]
> **Antigravity Generative UI & Artifact Integration:**
> In Google Antigravity, Antigravity IDE, and `agy` CLI, the generated dashboard can be saved to
> `reports/application-dashboard.html` and also mirrored directly into the conversation artifact directory
> (`<appDataDir>/brain/<conversation-id>/dashboard.html`) or rendered as a generative UI view.

> [!IMPORTANT]
> **Zero external dependencies & full offline rendering:**
> Charts are hand-generated inline SVG elements (doughnut, horizontal bars). No CDN, no Chart.js, and no external scripts.
>
> **Mandatory escaping:**
> HTML-escape every CSV and outcome-file string (`&`, `<`, `>`, `"`, `'`) before interpolating into HTML table cells,
> tooltip titles, and SVG `<text>` elements.

---

## Tool Translation Matrix

| Canonical (Claude Code) | Antigravity Native |
|-------------------------|---------------------|
| `View` / `Read`         | `read_file`         |
| `Glob`                  | `run_command` with `find documents/applications/ -name outcome.md` |
| `Write`                 | `write_file` (supports `ArtifactMetadata` when outputting to artifact directory) |

---

## Step-by-Step Workflow Execution

### Step 0: Parse Arguments

Handle `$ARGUMENTS`:
- **No arguments**: Write to `reports/application-dashboard.html` (create `reports/` if missing).
- **Path argument**: Write to specified output path.
- **`--open`**: Note browser view instructions.
- **Antigravity artifact output**: Write directly to conversation artifact directory when requested.

---

### Step 1: Collect Data

Read in parallel:
1. **`job_search_tracker.csv`**:
   - Fields: `date`, `company`, `sector`, `role`, `role_type`, `channel`, `status`, `contact_person`, `fit_rating`, `notes`, `cv_file`, `cover_letter_file`, `source`, `deadline`.
   - Rows written before `deadline` existed have 13 fields. Treat missing deadline as empty string; never drop rows.
2. **`documents/applications/*/outcome.md`**:
   - For resolved applications, read interview stage checkboxes and outcome notes. Merge into matching tracker row by lowercase company+role fuzzy match.

#### Status Normalization (6 Canonical Buckets)
- `drafted` → **Drafted** (created by `/apply`, not yet submitted)
- `applied` → **Active** (submitted, awaiting signal)
- `interview` → **Interview**
- `offer` → **Offer**
- `hired` → **Hired**
- `rejected` / `no_response` / `no response` / `offer_declined` / `offer declined` / `withdrawn` → **Rejected/Closed**
- Unrecognized values → **Rejected/Closed** (flagged in breakdown)

---

### Step 2: Compute Summary Stats

*Drafted applications are excluded from pipeline conversion metrics below (counted only in total drafts and status breakdown).*

Compute:
- **Total applications** (submitted)
- **Status breakdown**: Count per canonical bucket
- **By sector**: Count per unique sector
- **By channel**: Portal vs online vs referral vs other
- **By year/season**: Grouped by `date`
- **Funnel rates**: Percentage progressing past resume screen (reached Interview or beyond). Reconstructed from historical stage checkboxes in `outcome.md`, not just current status.
- **Rejection rate**: True rejections (`rejected`, `no_response`) divided by applications with a finalized outcome (`offer_declined` and `withdrawn` are voluntary candidate actions, not employer rejections).

---

### Step 3: Generate the HTML

Build a single self-contained `.html` file:
- **CSS**: Inline `<style>` block using CSS custom properties (`--drafted: #64748b`, `--active: #3b82f6`, `--interview: #f59e0b`, `--offer: #8b5cf6`, `--hired: #22c55e`, `--closed: #ef4444`).
- **Typography**: System UI font stack (`system-ui, -apple-system, sans-serif`).
- **Stat Cards**: Bold counts, status colored left borders.
- **Inline SVG Charts**:
  - **Status Doughnut**: Arc paths computed directly from status proportions.
  - **By Sector Horizontal Bar**: Bars sorted descending.
  - **By Channel Bar**: Distribution across channels.
  - **Application Funnel Horizontal Bar**: Applied → Interview → Offer → Hired progression.
- **Filterable Table**:
  - Live client-side text filtering across company, role, sector.
  - Status and sector dropdown filters (AND logic).
  - Status badges with palette colors.
  - Hyperlinked URLs in `source` column.
  - Notes truncated to 80 characters with full text in `title` attribute.
  - Newest-first default sort.
- **Escaping**: All values sanitized to prevent XSS.
- **Footer**: `Generated by Google Antigravity · ai-job-search · {ISO date}`.

---

### Step 4: Write and Confirm

1. Write HTML to designated path using `write_file`.
2. Present execution summary:
   - Dashboard file location.
   - Submitted vs drafted application counts.
   - Status bucket distribution.
   - Funnel conversion percentage.
