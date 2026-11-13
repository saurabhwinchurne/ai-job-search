---
name: add-template
version: 1.0.0
description: >
  Guides registration of custom CV and cover letter templates (LaTeX, Typst, or custom engines),
  captures build rules, verifies compilation with dummy data, and activates templates in /apply.
  Triggers on: add-template, register template, custom cv template, custom cover letter, switch template, /add-template
context: fork
enabled: true
---

# /add-template — Register a Custom CV or Cover Letter Template

> **Canonical spec:** `.claude/commands/add-template.md`
> Read and follow that file's instructions exactly, translating each tool call to
> Antigravity equivalents per the matrix below.

> [!IMPORTANT]
> **Compilation isolation:** Build artifacts must be contained. If the toolchain supports redirecting intermediate
> files, use a `build/` directory next to the source and move the final PDF back (`rm -f <file>.pdf && mkdir -p build && lualatex -interaction=nonstopmode -output-directory=build <file>.tex && mv build/<file>.pdf ./`).
> **Single active template:** Exactly one managed block (`<!-- BEGIN ACTIVE-TEMPLATE ... -->`) may exist per guidance file (`05-cv-templates.md` for CVs, `06-cover-letter-templates.md` for cover letters).

---

## Tool Translation Matrix

| Canonical (Claude Code) | Antigravity Native |
|-------------------------|---------------------|
| `View` / `Read`         | `read_file`         |
| `Glob`                  | `run_command` with `find templates/ -name TEMPLATE.md` |
| `Edit`                  | `edit_file`         |
| `Write`                 | `write_file`        |
| `Bash`                  | `run_command`       |
| `AskUserQuestion`       | `ask_question` (interactive selection) or chat prompt |

---

## Step-by-Step Workflow Execution

### Step 0: Parse Arguments

Handle `$ARGUMENTS`:
- **`--list`**: Run **List Mode** below and stop.
- **`--use <name>`**: Run **Switch Mode** below, then proceed to **Step 5: Activate**. (`--use default` restores stock guidance).
- **File path or `@-mention`**: Treat as the template source and proceed to Step 1.
- **Empty / No arguments**: Start interactive registration flow at Step 1.

#### List Mode
Scan registered templates with `find templates/ -name TEMPLATE.md`. For each manifest, read and display:
```
## Registered Templates

| Name | Type | Source | Toolchain | Fonts | Active |
|------|------|--------|-----------|-------|--------|
| <name> | CV / Cover letter | .tex/.typ/... | lualatex/typst/... | <main font> | yes/no |
```
A template is **active** if `05-cv-templates.md` (CV) or `06-cover-letter-templates.md` (Cover letter) contains an `ACTIVE-TEMPLATE` managed block naming it.

#### Switch Mode
If `$ARGUMENTS` contains `--use <name>`:
1. If `<name>` is `default`, proceed to Step 5 with `default` target.
2. Locate manifest in `templates/**/TEMPLATE.md` where parent directory matches `<name>`.
3. If not found, report error and suggest `/add-template --list`.
4. If multiple found, prompt user to resolve collision.
5. Extract metadata: Type (`CV` or `Cover letter`), source extension, compile command, toolchain, page limit, fonts.
6. Verify `template<source-extension>` exists in the template directory.
7. Derive `<type>` (`cv` or `cover_letters`) from the manifest path.
8. Proceed to Step 5. Do not re-run Steps 1-4.

---

### Step 1: Template Type and Source

Ask the user (skipping answered parts):
1. **Type**: **CV** or **cover letter** template?
2. **Source**: Location of template:
   - File path or `@-mention` (`.tex` + companion `.cls`/`.sty`, `.typ`, etc.)
   - Pasted template content
   - Directory containing template and assets (fonts, classes, images)

Read all provided files. If dependencies/classes are missing from standard distributions, request them before proceeding.

---

### Step 2: Capture Template Instructions

Interview or infer from source:
1. **Name**: Kebab-case identifier (e.g. `awesome-cv`). Must not collide with existing folders in `templates/`.
2. **Source extension**: Inferred from main file (`.tex`, `.typ`, etc.).
3. **Compile command**: Command executed with `<file>` placeholder:
   - `.tex` source: If `fontspec` or font files are used, require `xelatex` or `lualatex`.
     Standard build command: `rm -f <file>.pdf && mkdir -p build && lualatex -interaction=nonstopmode -output-directory=build <file>.tex && mv build/<file>.pdf ./`
   - `.typ` source: `typst compile <file>.typ <file>.pdf`
   - Other: Prompt user for exact compile command.
4. **Fonts**: Bundled font files (`.ttf`/`.otf` copied to `fonts/`) vs system/distribution fonts.
5. **Style rules**: Colors, section ordering, spacing, bullets, date formats to preserve.
6. **Page limit**: Hard bound (default: **2 pages** for CV, **1 page** for cover letter).
7. **Known pitfalls**: Fragile macros, characters requiring escaping, fixed sections.

---

### Step 3: Store the Template

Create destination directory:
- CV: `templates/cv/<name>/`
- Cover letter: `templates/cover_letters/<name>/`

Write:
1. **`template<source-extension>`**: Template skeleton with personal data replaced by `[PLACEHOLDER]` tokens (`[YOUR_NAME]`, `[YOUR_EMAIL]`, `[YOUR_PHONE]`, `[YOUR_LINKEDIN_URL]`, etc.).
2. **Class/style/package files**: Copy companion files alongside skeleton.
3. **`fonts/`**: Store bundled fonts and adjust skeleton font paths to be relative.
4. **`TEMPLATE.md`**: Canonical manifest following the template schema in `.claude/commands/add-template.md`.

---

### Step 4: Verify the Template Compiles (MANDATORY)

Never register a template without a successful test compile:
1. Copy `template<source-extension>` to scratch file `_compile_test<source-extension>` and substitute realistic dummy data into placeholders.
2. Compile with declared command substituting `_compile_test` for `<file>`.
3. If compile fails: display error lines, diagnose root cause (fonts, engine, packages), fix and recompile.
4. On success: verify PDF exists, verify readable layout, verify page count matches declared limit.
5. Clean up all scratch files (`_compile_test.*`, scratch PDF, `build/` directory).

---

### Step 5: Activate the Template

Insert or replace the managed block in `05-cv-templates.md` (CV) or `06-cover-letter-templates.md` (Cover letter) immediately after the H1 title:

```markdown
<!-- BEGIN ACTIVE-TEMPLATE (managed by /add-template - do not edit by hand) -->
> **Active template override: `<name>`**
>
> A custom template is active. Where this block conflicts with the stock guidance below, this block wins. Structural advice below (tailoring, page-budget, cutting rules) still applies.
>
> - **Template skeleton:** `templates/<type>/<name>/template<source-extension>` — use this as the structural reference instead of the stock template
> - **Manifest:** `templates/<type>/<name>/TEMPLATE.md` — read this for style rules and known pitfalls before drafting
> - **Source extension:** `<source-extension>` (not `.tex` unless the template's own toolchain is LaTeX)
> - **Compile command:** `<the full declared command>` (not the command named in the stock guidance below — `/apply`'s compile step must use this instead). Run it from the output directory. If it redirects to `build/`, the log is in `build/`, and `/apply`'s Step 5e cleanup must delete that `build/` folder too
> - **Fonts:** <font summary, including any path note for bundled fonts>
> - **Page limit:** exactly <N> page(s)
> - **Output file:** `cv/main_<company>_<role><source-extension>` / `cover_letters/cover_<company>_<role><source-extension>`; copy any class/package/font files the template needs into the output directory, or reference them by relative path
<!-- END ACTIVE-TEMPLATE -->
```

Rules:
- Exactly **one** managed block per guidance file.
- `--use default`: Remove the managed block entirely to revert to stock moderncv / cover.cls guidance.
- Never edit content outside the markers.

---

### Step 6: Confirm

Summarize registration and activation:
- Template directory and files
- Test compile status and verified page count
- Follow-up commands: `/add-template --list`, `/add-template --use <name>`, `/add-template --use default`.
