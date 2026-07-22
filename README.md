# Claude agent configuration

## Repository family

- [Codex Claude Orchestrator](https://github.com/coredo-eu/codex-claude-orchestrator) — local Codex-to-Claude worker transport, ownership policy, and lifecycle controls.
- [Codex agent configuration](https://github.com/coredo-eu/codex-agent-config) — portable Codex guidance, native-agent roles, and configuration template.
- [Claude agent configuration](https://github.com/coredo-eu/claude-agent-config) — portable standalone Claude guidance, agents, permissions, and CodeIndexer hook.

This repository is a portable, public snapshot of a standalone Claude agent
setup. It captures the main-session policy, six specialized agent definitions,
guarded permission choices, and a read-only CodeIndexer SessionStart hook. It
does not contain Claude authentication, conversations, or runtime state.

## Operating model

- Standalone Claude is its own principal. Its main session owns the requested
  outcome, architectural decisions, integration, conflict resolution, and final
  verification.
- Agents are optional bounded workers, not an obligatory pipeline. Delegation
  is used when context isolation, parallel discovery, or independent review
  materially improves the result.
- A worktree has one active edit-capable stream. Parallel writers require
  isolated worktrees and explicit custody transfer.
- External, destructive, credential, service-control, commit, push, and deploy
  actions remain decisions for the owning main session.
- CodeIndexer provides discovery evidence, not authority. Indexed conclusions
  are checked against source, configuration, schema, or observed runtime.
- Roadmap/card tracking is used only for genuinely continued or coordinated
  outcomes, not as ceremony for routine work.

The complete policy is in [`CLAUDE.md`](CLAUDE.md).

## Repository contents

| Path | Purpose |
| --- | --- |
| [`CLAUDE.md`](CLAUDE.md) | Global delegation, ownership, evidence, and tracking policy. |
| [`agents/`](agents) | Six standalone Claude agent definitions. |
| [`settings.example.json`](settings.example.json) | Sanitized model, permission, UI, and hook configuration. |
| [`hooks/codeindexer-session-facts.sh`](hooks/codeindexer-session-facts.sh) | Active read-only SessionStart hook for CodeIndexer readiness context. |

## Agent roles

| Role | Access | Intended use |
| --- | --- | --- |
| `bounded-executor` | local read/write | One coherent implementation inside an explicitly owned worktree. |
| `codeindexer-explorer` | read-only | Semantic discovery, call/dependency reconstruction, and impact evidence. |
| `scout` | read-only observation | Current local runtime, logs, health, queue, and service-state evidence. |
| `test-runner` | verification outputs only | Tests, builds, linters, and smoke checks after edit custody returns. |
| `reviewer` | read-only | Independent adversarial correctness and regression review. |
| `security-reviewer` | read-only | Security, privacy, credential, and authorization review. |

Each agent receives an outcome and boundaries, chooses its own method, and
returns concise evidence to the main session. Agent definitions never grant
external-action authority.

## Settings snapshot

[`settings.example.json`](settings.example.json) records these current choices:

- primary model `opus[1m]` with `xhigh` effort;
- fallbacks `claude-opus-4-8[1m]` and `claude-sonnet-5`;
- automatic shell classification with permission bypass disabled;
- allowlisted read-only CodeIndexer MCP discovery tools;
- explicit confirmation for commit, push, PR mutation, container/service
  control, `sudo`, process termination, and recursive deletion;
- denial rules protecting local settings, Claude project histories, and common
  credential-export patterns;
- fullscreen dark TUI;
- one active SessionStart hook.

Model identifiers and settings fields follow the source Claude installation and
may require adjustment for another release channel.

## CodeIndexer SessionStart hook

The hook receives Claude's SessionStart JSON on stdin and:

1. reads the session working directory;
2. finds the longest matching registered project path;
3. checks the loopback CodeIndexer readiness endpoint with a two-second timeout;
4. injects one compact context line describing registry and index availability.

It performs no writes, starts no service, reads no credentials, and exits
silently when no registry or matching project exists. The registry defaults to
`~/.config/codeindexer/projects.json`; set `CODEINDEXER_PROJECTS_REGISTRY` to
use another location.

Expected registry shape:

```json
{
  "projections": [
    {
      "name": "example-project",
      "path": "${HOME}/src/example-project"
    }
  ]
}
```

## Installation

Requirements:

- Claude Code with support for `CLAUDE.md`, custom agents, hooks, and permission
  rules;
- `jq` and `curl` for the CodeIndexer hook;
- CodeIndexer only when hook context or MCP discovery is wanted.

Clone and review the repository before installing it:

```bash
git clone https://github.com/coredo-eu/claude-agent-config.git
cd claude-agent-config

mkdir -p ~/.claude/agents ~/.claude/hooks
install -m 0644 CLAUDE.md ~/.claude/CLAUDE.md
install -m 0644 agents/*.md ~/.claude/agents/
install -m 0755 hooks/codeindexer-session-facts.sh ~/.claude/hooks/
```

Replace `__HOME__` in `settings.example.json` with the absolute home path, then
merge the result into `~/.claude/settings.json`. Do not overwrite unrelated
local permissions, hooks, or plugin settings wholesale.

## Validation

```bash
jq empty settings.example.json
bash -n hooks/codeindexer-session-facts.sh
printf '{"cwd":"/tmp"}' | hooks/codeindexer-session-facts.sh
```

The final command should exit successfully and produce no output when no
matching registry entry exists.

## Deliberate exclusions

This repository does not contain credentials, licenses, local overrides,
conversation or project histories, sessions, caches, downloads, file history,
plugin caches, marketplace state, or absolute machine paths. Those remain owned
by each local standalone Claude installation.
