#!/usr/bin/env python3
"""Validate the public standalone Claude goal and model-routing contract."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HEADINGS = [
    "Outcome",
    "Done when",
    "Boundaries",
    "Authoritative context",
    "Non-goals",
    "Known evidence",
    "Required handoff",
]
ROUTES: dict[str, tuple[str, str | None]] = {
    "bounded-executor.md": ("claude-sonnet-5", "high"),
    "codeindexer-explorer.md": ("claude-haiku-4-5-20251001", None),
    "scout.md": ("claude-haiku-4-5-20251001", None),
    "test-runner.md": ("claude-haiku-4-5-20251001", None),
    "reviewer.md": ("claude-opus-5", "medium"),
    "security-reviewer.md": ("claude-opus-5", "xhigh"),
}
SEMVER = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
REVIEW_TOOLS = (
    "Read",
    "Glob",
    "Grep",
    "mcp__codeindexer__search_code",
    "mcp__codeindexer__find_callers",
    "mcp__codeindexer__find_callees",
    "mcp__codeindexer__find_references",
    "mcp__codeindexer__file_deps",
    "mcp__codeindexer__read_chunk",
    "mcp__codeindexer__read_file_range",
)
TOOLS: dict[str, tuple[str, ...]] = {
    "bounded-executor.md": (
        "Bash",
        "Read",
        "Write",
        "Edit",
        "Glob",
        "Grep",
        "mcp__codeindexer__search_code",
        "mcp__codeindexer__find_callers",
        "mcp__codeindexer__find_callees",
        "mcp__codeindexer__find_references",
        "mcp__codeindexer__file_deps",
        "mcp__codeindexer__read_chunk",
        "mcp__codeindexer__read_file_range",
    ),
    "codeindexer-explorer.md": (
        "Read",
        "Glob",
        "Grep",
        "mcp__codeindexer__search_code",
        "mcp__codeindexer__find_callers",
        "mcp__codeindexer__find_callees",
        "mcp__codeindexer__find_references",
        "mcp__codeindexer__file_deps",
        "mcp__codeindexer__read_chunk",
        "mcp__codeindexer__read_file_range",
    ),
    "scout.md": (
        "Bash",
        "Read",
        "Glob",
        "Grep",
        "mcp__codeindexer__search_code",
        "mcp__codeindexer__read_file_range",
    ),
    "test-runner.md": (
        "Bash",
        "Read",
        "Glob",
        "Grep",
        "mcp__codeindexer__search_code",
        "mcp__codeindexer__find_references",
        "mcp__codeindexer__read_file_range",
    ),
    "reviewer.md": REVIEW_TOOLS,
    "security-reviewer.md": REVIEW_TOOLS,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"claude-agent-config validation: FAIL: {message}")


def frontmatter(text: str, path: Path) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    require(match is not None, f"frontmatter missing: {path.relative_to(ROOT)}")
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def validate_agent(path: Path, model: str, effort: str | None) -> None:
    text = path.read_text(encoding="utf-8")
    observed_headings = re.findall(
        r"^\*\*(Outcome|Done when|Boundaries|Authoritative context|Non-goals|Known evidence|Required handoff):\*\*",
        text,
        flags=re.MULTILINE,
    )
    require(observed_headings == HEADINGS, f"goal headings drift: {path.relative_to(ROOT)}")
    require(
        "The parent retains the outer goal and completion verdict." in text,
        f"parent completion authority missing: {path.relative_to(ROOT)}",
    )

    metadata = frontmatter(text, path)
    require(metadata.get("model") == model, f"model route drift: {path.relative_to(ROOT)}")
    if effort is None:
        require("effort" not in metadata, f"unsupported effort override: {path.relative_to(ROOT)}")
    else:
        require(metadata.get("effort") == effort, f"effort route drift: {path.relative_to(ROOT)}")
    observed_tools = tuple(part.strip() for part in metadata.get("tools", "").split(",") if part.strip())
    require(observed_tools == TOOLS[path.name], f"tool route drift: {path.relative_to(ROOT)}")


def main() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(SEMVER.fullmatch(version) is not None, "VERSION is not plain semantic versioning")

    claude_text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    policy_headings = re.findall(
        r"^- `(Outcome|Done when|Boundaries|Authoritative context|Non-goals|Known evidence|Required handoff)`",
        claude_text,
        flags=re.MULTILINE,
    )
    require(policy_headings == HEADINGS, "CLAUDE.md goal contract drift")
    require("persistent outer goal" in claude_text, "outer-goal authority missing from CLAUDE.md")
    require("handoff — evidence" in claude_text, "handoff is not explicitly evidence-only")

    expected_agents = set(ROUTES)
    observed_agents = {path.name for path in (ROOT / "agents").glob("*.md")}
    require(set(TOOLS) == expected_agents, "validator route/tool tables drift")
    require(observed_agents == expected_agents, "agent inventory drift")
    for filename, (model, effort) in ROUTES.items():
        validate_agent(ROOT / "agents" / filename, model, effort)

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    positions = [readme.find(f"`{heading}`") for heading in HEADINGS]
    require(all(position >= 0 for position in positions), "README goal contract incomplete")
    require(positions == sorted(positions), "README goal headings out of order")
    require("busy-worker" in readme and "Codex-orchestrator" in readme, "transport boundary missing")
    require(f"`v{version}`" in readme, "README release version drift")

    settings = json.loads((ROOT / "settings.example.json").read_text(encoding="utf-8"))
    for forbidden in ("model", "fallbackModel", "effortLevel"):
        require(forbidden not in settings, f"standalone main session unexpectedly pins {forbidden}")

    print("claude-agent-config validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
