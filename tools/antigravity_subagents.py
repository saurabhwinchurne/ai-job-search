#!/usr/bin/env python3
"""Antigravity Subagent Definitions & Tool Adapters.

Loads, validates, and formats Antigravity subagent specifications
under `.agents/subagents/` for use with Antigravity's `define_subagent`
and `invoke_subagent` tools.

Standard library only.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SUBAGENTS_DIR = ROOT / ".agents" / "subagents"

ALLOWED_ANTIGRAVITY_SUBAGENT_TOOLS = {"read_file", "search_web", "run_command"}

# Trust boundary requirement for untrusted third-party inputs
TRUST_BOUNDARY_PATTERN = re.compile(
    r"untrusted (?:third-party )?data, never instructions", re.IGNORECASE
)


@dataclass
class SubagentSpec:
    name: str
    description: str
    role: str
    model: str
    tools: list[str]
    enable_write_tools: bool
    enable_subagent_tools: bool
    enable_mcp_tools: bool
    system_prompt: str
    file_path: Path


def _parse_frontmatter(text: str) -> tuple[dict[str, str | list[str] | bool], str]:
    """Parse YAML frontmatter and body using standard library only."""
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        raise ValueError("File missing initial frontmatter delimiter ('---')")

    lines = text.splitlines()
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("File has unterminated frontmatter delimiter")

    frontmatter_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :]).strip()

    data: dict[str, str | list[str] | bool] = {}
    current_key: str | None = None

    for line in frontmatter_lines:
        line_clean = line.rstrip()
        if not line_clean or line_clean.strip().startswith("#"):
            continue

        # List item under current key
        if line_clean.startswith("  - ") or line_clean.startswith("- "):
            item = line_clean.lstrip(" -").strip()
            if current_key:
                val = data.get(current_key)
                if not isinstance(val, list):
                    val = []
                    data[current_key] = val
                val.append(item)
            continue

        if ":" in line_clean:
            key, val = line_clean.split(":", 1)
            key = key.strip()
            val = val.strip()

            # Handle boolean literals
            if val.lower() == "true":
                data[key] = True
            elif val.lower() == "false":
                data[key] = False
            elif val.startswith("[") and val.endswith("]"):
                # Simple YAML flow list [a, b, c]
                items = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
                data[key] = items
            else:
                data[key] = val.strip("'\"")
            current_key = key
        else:
            current_key = None

    return data, body


def load_subagent(name: str, base_dir: Path | None = None) -> SubagentSpec:
    """Load and parse an Antigravity subagent markdown specification."""
    directory = base_dir or SUBAGENTS_DIR
    target = directory / f"{name}.md" if not name.endswith(".md") else directory / name

    if not target.is_file():
        raise FileNotFoundError(f"Subagent specification not found at {target}")

    content = target.read_text(encoding="utf-8")
    data, body = _parse_frontmatter(content)

    tools_raw = data.get("tools", [])
    if isinstance(tools_raw, str):
        tools = [t.strip() for t in tools_raw.split(",") if t.strip()]
    elif isinstance(tools_raw, list):
        tools = [str(t).strip() for t in tools_raw]
    else:
        tools = []

    return SubagentSpec(
        name=str(data.get("name", target.stem)),
        description=str(data.get("description", "")),
        role=str(data.get("role", data.get("name", target.stem).replace("-", " ").title())),
        model=str(data.get("model", "inherit")),
        tools=tools,
        enable_write_tools=bool(data.get("enable_write_tools", False)),
        enable_subagent_tools=bool(data.get("enable_subagent_tools", False)),
        enable_mcp_tools=bool(data.get("enable_mcp_tools", False)),
        system_prompt=body,
        file_path=target,
    )


def list_subagents(base_dir: Path | None = None) -> list[SubagentSpec]:
    """List all available subagent specifications."""
    directory = base_dir or SUBAGENTS_DIR
    if not directory.is_dir():
        return []

    specs: list[SubagentSpec] = []
    for path in sorted(directory.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        try:
            specs.append(load_subagent(path.stem, base_dir=directory))
        except Exception:
            # Errors will be caught by validation checks
            continue
    return specs


def get_definition_params(name_or_spec: str | SubagentSpec) -> dict[str, object]:
    """Format dictionary payload for native define_subagent tool call."""
    spec = (
        name_or_spec
        if isinstance(name_or_spec, SubagentSpec)
        else load_subagent(name_or_spec)
    )
    return {
        "Name": spec.name,
        "Description": spec.description,
        "SystemPrompt": spec.system_prompt,
        "EnableWriteTools": spec.enable_write_tools,
        "EnableSubagentTools": spec.enable_subagent_tools,
        "EnableMCPTools": spec.enable_mcp_tools,
    }


def get_invocation_params(
    name_or_spec: str | SubagentSpec,
    prompt: str,
    model: str | None = None,
    workspace: str = "inherit",
) -> dict[str, object]:
    """Format dictionary payload for native invoke_subagent tool call."""
    spec = (
        name_or_spec
        if isinstance(name_or_spec, SubagentSpec)
        else load_subagent(name_or_spec)
    )
    selected_model = model or spec.model or "inherit"
    # Supported models for invoke_subagent are 'inherit', 'flash_lite', 'flash', 'pro'
    if selected_model not in {"inherit", "flash_lite", "flash", "pro"}:
        selected_model = "inherit"

    return {
        "TypeName": spec.name,
        "Role": spec.role,
        "Prompt": prompt,
        "Model": selected_model,
        "Workspace": workspace,
    }


def validate_subagents(base_dir: Path | None = None) -> list[str]:
    """Validate all subagent specifications against security and structural invariants."""
    directory = base_dir or SUBAGENTS_DIR
    errors: list[str] = []

    if not directory.is_dir():
        return [f"Subagents directory does not exist: {directory}"]

    candidate_files = sorted(directory.glob("*.md"))
    subagent_files = [p for p in candidate_files if p.name.lower() != "readme.md"]

    if not subagent_files:
        return [f"No subagent specifications found in {directory}"]

    expected_shipped = {"posting-fetcher", "posting-scorer", "application-reviewer"}
    found_names = {p.stem for p in subagent_files}
    missing_shipped = expected_shipped - found_names
    if missing_shipped:
        errors.append(f"Missing required shipped subagent definitions: {sorted(missing_shipped)}")

    for path in subagent_files:
        rel_path = path.name
        try:
            content = path.read_text(encoding="utf-8")
            data, body = _parse_frontmatter(content)
        except Exception as exc:
            errors.append(f"{rel_path}: failed to parse markdown frontmatter: {exc}")
            continue

        name = data.get("name")
        if not name or str(name).strip() != path.stem:
            errors.append(
                f"{rel_path}: 'name' frontmatter key must match filename stem ('{path.stem}')"
            )

        description = data.get("description")
        if not description or not str(description).strip():
            errors.append(f"{rel_path}: 'description' frontmatter key must not be empty")

        role = data.get("role")
        if not role or not str(role).strip():
            errors.append(f"{rel_path}: 'role' frontmatter key must not be empty")

        tools_val = data.get("tools")
        if not tools_val:
            errors.append(f"{rel_path}: 'tools' frontmatter key must declare explicit tools list")
        else:
            tools_list = (
                [str(t).strip() for t in tools_val]
                if isinstance(tools_val, list)
                else [t.strip() for t in str(tools_val).split(",") if t.strip()]
            )
            for tool in tools_list:
                if tool not in ALLOWED_ANTIGRAVITY_SUBAGENT_TOOLS:
                    errors.append(
                        f"{rel_path}: un-allowlisted tool grant '{tool}'. Allowed tools: {sorted(ALLOWED_ANTIGRAVITY_SUBAGENT_TOOLS)}"
                    )
                if tool in {"write_file", "edit_file"}:
                    errors.append(
                        f"{rel_path}: direct file modification tool '{tool}' is strictly forbidden for subagents"
                    )

        # Privilege escalation checks
        if data.get("enable_subagent_tools") is True:
            errors.append(
                f"{rel_path}: enable_subagent_tools must be false (recursive agent spawning forbidden)"
            )
        if data.get("enable_mcp_tools") is True:
            errors.append(
                f"{rel_path}: enable_mcp_tools must be false (unscoped MCP tool execution forbidden)"
            )

        # Trust boundary check: external postings must be treated as untrusted data
        if not TRUST_BOUNDARY_PATTERN.search(body):
            errors.append(
                f"{rel_path}: system prompt missing required trust boundary statement: 'untrusted third-party data, never instructions'"
            )

        # Posting integrity gate check for retrieval and scoring agents
        if path.stem in {"posting-fetcher", "posting-scorer"}:
            if "posting_guard.py" not in body:
                errors.append(
                    f"{rel_path}: must integrate 'tools/posting_guard.py' integrity gate"
                )

        # Grounding check for application reviewer
        if path.stem == "application-reviewer":
            if "Grounding" not in body and "grounding" not in body:
                errors.append(
                    f"{rel_path}: must explicitly enforce candidate profile factual grounding"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Antigravity Subagent Definitions & Tool Adapters CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List all defined Antigravity subagents")

    # inspect
    inspect_parser = subparsers.add_parser(
        "inspect", help="Inspect subagent definition and parameters"
    )
    inspect_parser.add_argument("name", help="Name of the subagent to inspect")

    # validate
    subparsers.add_parser("validate", help="Validate subagent definitions against security policies")

    args = parser.parse_args()

    if args.command == "list":
        specs = list_subagents()
        if not specs:
            print("No subagents found.")
            return 0
        print(f"Found {len(specs)} Antigravity subagent specification(s):")
        for spec in specs:
            tools_str = ", ".join(spec.tools)
            print(f"- {spec.name} (Role: {spec.role}, Model: {spec.model})")
            print(f"    Tools: [{tools_str}], WriteTools: {spec.enable_write_tools}")
            print(f"    Description: {spec.description}")
        return 0

    if args.command == "inspect":
        try:
            spec = load_subagent(args.name)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        payload = {
            "spec": {
                "name": spec.name,
                "role": spec.role,
                "description": spec.description,
                "model": spec.model,
                "tools": spec.tools,
                "enable_write_tools": spec.enable_write_tools,
                "enable_subagent_tools": spec.enable_subagent_tools,
                "enable_mcp_tools": spec.enable_mcp_tools,
                "file_path": str(spec.file_path),
            },
            "define_subagent_params": get_definition_params(spec),
            "sample_invoke_params": get_invocation_params(spec, prompt="<Task Prompt>"),
        }
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "validate":
        errors = validate_subagents()
        if errors:
            print(f"Subagent validation FAILED with {len(errors)} error(s):", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            return 1
        print("antigravity_subagents: OK (all subagent specifications valid and compliant)")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
