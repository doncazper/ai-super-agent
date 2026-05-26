from __future__ import annotations

from pathlib import Path

from .models import LAUNCHER_VERSION


def launcher_path(install_dir: str | Path, alias: str) -> Path:
    return Path(install_dir).expanduser() / alias


def generate_launcher_script(*, repo_path: str | Path, config_path: str | Path) -> str:
    repo = str(Path(repo_path).expanduser())
    config = str(Path(config_path).expanduser())
    return f"""#!/usr/bin/env bash
set -euo pipefail

SMARTAGENT_LAUNCHER_VERSION="{LAUNCHER_VERSION}"
SMARTAGENT_REPO="{repo}"
SMARTAGENT_CONFIG="{config}"

valid_repo() {{
  local candidate="$1"
  [[ -d "$candidate" ]] || return 1
  [[ -f "$candidate/smart_agent.py" && -f "$candidate/scripts/agent" ]] || return 1
  local markers=0
  [[ -f "$candidate/pyproject.toml" ]] && markers=$((markers + 1))
  [[ -f "$candidate/AGENTS.md" ]] && markers=$((markers + 1))
  [[ -f "$candidate/docs/PROJECT_STATE.md" ]] && markers=$((markers + 1))
  [[ -f "$candidate/docs/COMMAND_REGISTRY.md" ]] && markers=$((markers + 1))
  [[ -d "$candidate/.git" ]] && markers=$((markers + 1))
  [[ "$markers" -ge 2 ]] || return 1
  if [[ -d "$candidate/.git" ]]; then
    local git_root
    git_root="$(git -C "$candidate" rev-parse --show-toplevel 2>/dev/null || true)"
    [[ -n "$git_root" && "$git_root" == "$(cd "$candidate" && pwd)" ]] || return 1
  fi
}}

config_repo() {{
  if [[ -f "$SMARTAGENT_CONFIG" ]]; then
    sed -n 's/.*"repo_path": "\\([^"]*\\)".*/\\1/p' "$SMARTAGENT_CONFIG" | head -n 1
  fi
}}

explicit_repo_arg() {{
  local previous=""
  for arg in "$@"; do
    if [[ "$previous" == "--set-repo" || "$previous" == "--repo" ]]; then
      printf '%s\\n' "$arg"
      return 0
    fi
    previous="$arg"
  done
}}

choose_repo() {{
  local configured
  configured="$(config_repo || true)"
  local explicit
  explicit="$(explicit_repo_arg "$@" || true)"
  if [[ -n "$configured" ]] && valid_repo "$configured"; then
    printf '%s\\n' "$configured"
    return 0
  fi
  if valid_repo "$SMARTAGENT_REPO"; then
    printf '%s\\n' "$SMARTAGENT_REPO"
    return 0
  fi
  local found=()
  local candidates=("$configured" "$PWD" "$HOME/Documents/AI Super Agent" "$HOME/Documents/ai-super-agent" "$HOME/AI Super Agent" "$HOME/ai-super-agent" "$HOME/Desktop/AI Super Agent" "$HOME/Desktop/ai-super-agent" "$explicit")
  for candidate in "${{candidates[@]}}"; do
    if [[ -n "$candidate" ]] && valid_repo "$candidate"; then
      found+=("$candidate")
    fi
  done
  if [[ "${{#found[@]}}" -eq 1 ]]; then
    printf '%s\\n' "${{found[0]}}"
    return 0
  fi
  if [[ "${{#found[@]}}" -gt 1 ]]; then
    echo "Multiple AI Super Agent repos found. Choose one explicitly:" >&2
    for candidate in "${{found[@]}}"; do echo "  $candidate" >&2; done
    echo "Run: smartagent --repair-path --repo \"/path/to/AI Super Agent\"" >&2
    return 2
  fi
  echo "Configured repo not found: $SMARTAGENT_REPO" >&2
  echo "Clone and install:" >&2
  echo "  git clone https://github.com/doncazper/ai-super-agent.git" >&2
  echo "  cd ai-super-agent" >&2
  echo "  ./scripts/install-smartagent-launcher --alias smartagent" >&2
  echo "Or repair an existing clone:" >&2
  echo "  smartagent --set-repo \"/path/to/repo\"" >&2
  return 2
}}

choose_python() {{
  local repo="$1"
  local candidates=("$repo/.venv/bin/python" "python3.12" "python3.11" "/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3" "python3")
  for candidate in "${{candidates[@]}}"; do
    if [[ -x "$candidate" ]] || command -v "$candidate" >/dev/null 2>&1; then
      if "$candidate" - "$candidate" <<'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if sys.version_info[:2] >= (3, 11) else 1)
PY
      then
        command -v "$candidate" 2>/dev/null || printf '%s\\n' "$candidate"
        return 0
      fi
    fi
  done
  echo "AI Super Agent requires Python 3.11 or newer." >&2
  echo "Run: brew install python@3.12" >&2
  return 2
}}

REPO="$(choose_repo "$@")"
PY="$(choose_python "$REPO")"
cd "$REPO"
exec "$PY" -m agent.launcher.cli --config "$SMARTAGENT_CONFIG" --wrapper "$0" "$@"
"""
