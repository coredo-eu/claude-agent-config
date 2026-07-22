#!/bin/bash
set -u

input=$(cat)
cwd=$(printf '%s' "$input" | /usr/bin/jq -r '.cwd // empty')
registry="${CODEINDEXER_PROJECTS_REGISTRY:-$HOME/.config/codeindexer/projects.json}"
checked_at=$(/bin/date -u '+%Y-%m-%dT%H:%M:%SZ')

if [ -z "$cwd" ] || [ ! -r "$registry" ]; then
  exit 0
fi

rows=$(/usr/bin/jq -r --arg home "$HOME" \
  '.projections[] | [.name, (.path | sub("^\\$\\{HOME\\}"; $home))] | @tsv' \
  "$registry" 2>/dev/null) || exit 0

project=""
matched_path=""
while IFS=$'\t' read -r name path; do
  case "$cwd" in
    "$path"|"$path"/*)
      if [ "${#path}" -gt "${#matched_path}" ]; then
        project="$name"
        matched_path="$path"
      fi
      ;;
  esac
done <<EOF
$rows
EOF

[ -n "$project" ] || exit 0

response=$(/usr/bin/curl -fsS -m 2 "http://127.0.0.1:8978/api/playground/projects" 2>/dev/null || true)
if [ -n "$response" ] && printf '%s' "$response" | /usr/bin/jq -e '.projects | type == "array"' >/dev/null 2>&1; then
  if printf '%s' "$response" | /usr/bin/jq -e --arg project "$project" 'any(.projects[]?; .name == $project and .indexing_complete == true)' >/dev/null 2>&1; then
    projection="ready"
  else
    projection="not_ready_or_missing"
  fi
  index_api="reachable"
else
  index_api="unreachable"
  projection="unknown"
fi

context="[codeindexer-state] registered_project=$project; index_api=$index_api; projection=$projection; checked_at=$checked_at. REST readiness does not prove MCP transport availability or projection freshness; the governing discovery and tracking contract is in CLAUDE.md."
/usr/bin/jq -cn --arg context "$context" \
  '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$context}}'
