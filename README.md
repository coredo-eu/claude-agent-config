# Claude agent configuration

## Repository family

- [Codex Claude Orchestrator](https://github.com/coredo-eu/codex-claude-orchestrator) — local Codex-to-Claude worker transport, ownership policy, and lifecycle controls.
- [Codex agent configuration](https://github.com/coredo-eu/codex-agent-config) — portable Codex guidance, native-agent roles, and configuration template.
- [Claude agent configuration](https://github.com/coredo-eu/claude-agent-config) — portable standalone Claude guidance, agents, permissions, and CodeIndexer hook.

Portable snapshot of the current standalone Claude agent-working policy,
specialized agents, permissions, and active CodeIndexer session hook.

## Contents

- `CLAUDE.md` — global delegation, ownership, and evidence policy.
- `agents/` — standalone Claude agent definitions.
- `settings.example.json` — sanitized copy of the active settings.
- `hooks/codeindexer-session-facts.sh` — the active SessionStart hook.

## Use

1. Replace `__HOME__` in `settings.example.json` with the absolute home path.
2. Review and copy `CLAUDE.md`, `agents/`, and `hooks/` into `~/.claude/`.
3. Merge `settings.example.json` into `~/.claude/settings.json` rather than
   overwriting unrelated local settings.
4. Set `CODEINDEXER_PROJECTS_REGISTRY` when the registry is not stored at
   `~/.config/codeindexer/projects.json`.

Credentials, licenses, local overrides, sessions, project histories, caches,
downloads, plugin runtime state, and machine-specific paths are intentionally
excluded.
