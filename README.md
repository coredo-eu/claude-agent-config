# Claude agent configuration

## Project family

- [codex-agent-config](https://github.com/coredo-eu/codex-agent-config) — Codex instructions and native specialist profiles.
- [claude-agent-config](https://github.com/coredo-eu/claude-agent-config) — standalone Claude Code instructions and specialist agents.
- [codex-claude-orchestrator](https://github.com/coredo-eu/codex-claude-orchestrator) — Codex plugin that delegates local tasks to Claude Code and returns results for Codex verification.

Together, these projects form the **COREDO agent tools family**: two
configuration packages and one installable Codex plugin. Use each on its own
or combine them. The orchestrator requires Claude Code, but does not require
`claude-agent-config`; it supplies its own worker instructions and roles.

## What it does

This package gives standalone Claude Code shared working instructions, seven
specialist agents, example permissions, and an optional CodeIndexer session
hook. It helps Claude delegate work, check results, and keep one editor in
charge of each worktree.

The main Claude session manages the task and decides when it is complete.
Specialists handle bounded assignments and return their results for review.
They are used when they help, rather than as a required sequence of steps.
External actions remain decisions for the main session. The full rules are in
[`CLAUDE.md`](CLAUDE.md).

This package does not include credentials, conversations, or local runtime
state. Codex-orchestrator controls such as PTY-worker admission and the
busy-worker limit belong to the separate orchestrator plugin.

## What's included

Current version: `v0.4.0` (see [`VERSION`](VERSION)). This version provides
seven roles, including separate agents for direct source inspection and
CodeIndexer discovery, with model routes aligned to the orchestrator's
Claude worker roster. Its versioning is independent of the orchestrator.

| Path | Purpose |
| --- | --- |
| [`VERSION`](VERSION) | Standalone package version used for Git tags and releases. |
| [`CLAUDE.md`](CLAUDE.md) | Global delegation, ownership, evidence, and tracking policy. |
| [`agents/`](agents) | Seven standalone Claude agent definitions. |
| [`settings.example.json`](settings.example.json) | Sanitized permission, UI, and hook configuration. |
| [`hooks/codeindexer-session-facts.sh`](hooks/codeindexer-session-facts.sh) | Active read-only SessionStart hook for CodeIndexer readiness context. |
| [`scripts/validate.py`](scripts/validate.py) | Deterministic goal-contract, model-route, and settings validation. |

### Agent roles

| Role | Model | Effort | Access | Intended use |
| --- | --- | --- | --- | --- |
| `bounded-executor` | `claude-sonnet-5` | `high` | local read/write | One coherent implementation inside an explicitly owned worktree. |
| `source-explorer` | `claude-haiku-4-5-20251001` | not supported by Haiku | read-only | Direct inspection of current source, configuration, schemas, and tests. |
| `codeindexer-explorer` | `claude-sonnet-5` | `low` | read-only | Semantic discovery, call/dependency reconstruction, and impact evidence. |
| `scout` | `claude-haiku-4-5-20251001` | not supported by Haiku | read-only observation | Current local runtime, logs, health, queue, and service-state evidence. |
| `test-runner` | `claude-haiku-4-5-20251001` | not supported by Haiku | verification outputs only | Tests, builds, linters, and smoke checks after edit custody returns. |
| `reviewer` | `claude-opus-5-5` | `high` | read-only | Independent adversarial correctness and regression review. |
| `security-reviewer` | `claude-opus-5-5` | `xhigh` | read-only | Security, privacy, credential, and authorization review. |

Choose the agent that matches the work:

| Canonical semantic role | Standalone Claude agent | Selection boundary |
| --- | --- | --- |
| Direct-source exploration | `source-explorer` | Inspect current local source when direct evidence is sufficient. |
| CodeIndexer exploration | `codeindexer-explorer` | Use semantic search and reconstruction when indexed evidence adds value. |
| Local operational scouting | `scout` | Observe a bounded current runtime or operational-state question. |
| Bounded implementation | `bounded-executor` | Make one coherent change only with isolated edit custody. |
| Independent verification | `test-runner` | Run relevant checks after edit custody returns or in an isolated root. |
| Correctness review | `reviewer` | Falsify a result when consequence or uncertainty warrants it. |
| Security review | `security-reviewer` | Review materially implicated security or privacy concerns. |

Each agent receives the bounded seven-field goal contract, chooses its own
method, and returns concise evidence to the main session; agent definitions
never grant external-action authority. Every independently owned delegation
uses these headings in order: `Outcome`, `Done when`, `Boundaries`,
`Authoritative context`, `Non-goals`, `Known evidence`, and `Required handoff`.
Keep the values as short as the task allows.

### Settings snapshot

[`settings.example.json`](settings.example.json) records these current
choices:

- no top-level `model`, `fallbackModel`, or `effortLevel` override: the main
  session inherits the model and effort selected by the user;
- specialized agents override that inheritance intentionally with exact model
  IDs: Haiku 4.5 handles direct discovery, runtime observation, and routine
  verification, Sonnet 5 handles CodeIndexer discovery and implementation,
  and Opus 5.5 handles independent correctness and security review;
- supported agents also set role-specific effort: `low` for CodeIndexer
  discovery, `high` for bounded execution and correctness review, and
  `xhigh` for security review; the three Haiku roles omit the effort field;
- no `defaultMode`, `autoMode`, or `skipAutoPermissionPrompt`: automatic mode
  remains under the user's local Claude settings;
- permission bypass disabled as a shared safety boundary;
- an allowlist of read-only CodeIndexer MCP tools: this only permits using an
  MCP connection that is already configured elsewhere in your Claude
  settings, it does not itself configure or start one;
- explicit confirmation for commit, push, PR mutation, container/service
  control, `sudo`, process termination, and recursive deletion;
- denial rules protecting local settings, Claude project histories, and
  common credential-export patterns;
- fullscreen dark TUI with the workflow usage warning suppressed;
- one active SessionStart hook.

The remaining settings fields may require adjustment for another Claude
release channel.

## Installation

Requirements:

- Claude Code with support for `CLAUDE.md`, custom agents, hooks, and
  permission rules;
- Python 3 for repository validation;
- the hook script invokes `/usr/bin/jq`, `/bin/date`, and `/usr/bin/curl` by
  absolute path — review
  [`hooks/codeindexer-session-facts.sh`](hooks/codeindexer-session-facts.sh)
  and adjust those paths first if your platform installs them elsewhere;
- CodeIndexer only when hook context or MCP discovery is wanted. Installing
  this package does not configure an MCP connection or start CodeIndexer for
  you; any MCP server must be registered separately in your Claude settings.

Clone and review the repository before installing it. For an existing setup,
compare and merge local changes first; the copy commands replace matching
files:

```bash
git clone https://github.com/coredo-eu/claude-agent-config.git
cd claude-agent-config

mkdir -p ~/.claude/agents ~/.claude/hooks
install -m 0644 CLAUDE.md ~/.claude/CLAUDE.md
install -m 0644 agents/*.md ~/.claude/agents/
install -m 0755 hooks/codeindexer-session-facts.sh ~/.claude/hooks/
```

Replace `__HOME__` in `settings.example.json` with the absolute home path,
then merge the result into `~/.claude/settings.json`. Do not overwrite
unrelated local permissions, hooks, or plugin settings wholesale. For updates,
pull the checkout and review the diff before copying files again. Start a new
Claude Code session after installation or an update.

## Usage

Start Claude Code normally and describe the task. The installed `CLAUDE.md`
and agent definitions guide delegation and verification. For example:

```text
Investigate this bug, delegate a bounded fix if useful, and verify the result.
```

When the example hook is enabled, it runs on session start and:

1. reads the session working directory;
2. finds the longest matching registered project path;
3. checks the loopback CodeIndexer readiness endpoint with a two-second
   timeout;
4. injects one compact context line describing registry and index
   availability.

It performs no writes, starts no service, reads no credentials, and exits
silently when no registry or matching project exists. The registry defaults
to `~/.config/codeindexer/projects.json`; set `CODEINDEXER_PROJECTS_REGISTRY`
to use another location. Expected registry shape:

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

## Validation

```bash
jq empty settings.example.json
bash -n hooks/codeindexer-session-facts.sh
printf '{"cwd":"/tmp"}' | hooks/codeindexer-session-facts.sh
python3 scripts/validate.py
```

The hook smoke command should exit successfully and produce no output when no
matching registry entry exists. The contract validator prints
`claude-agent-config validation: PASS` on success.

## Further reading

- [`CLAUDE.md`](CLAUDE.md): the complete delegation, ownership, evidence, and
  tracking policy.
- [codex-claude-orchestrator](https://github.com/coredo-eu/codex-claude-orchestrator): runs Claude workers under Codex and returns results for verification.
- [codex-agent-config](https://github.com/coredo-eu/codex-agent-config): portable Codex instructions and native specialist profiles.
