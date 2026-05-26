# Smartagent Global Launcher

`smartagent` is a user-level launcher for AI Super Agent. It lets you start the repo-local `./scripts/agent` wrapper from any Terminal directory without sudo, system path writes, background services, or model/provider calls during launcher diagnostics.

## Install

Fresh clone:

```bash
git clone https://github.com/doncazper/ai-super-agent.git
cd ai-super-agent
./scripts/install-smartagent-launcher --alias smartagent
```

Default alias:

```bash
./scripts/install-smartagent-launcher
```

Custom alias:

```bash
./scripts/install-smartagent-launcher --alias sa
```

Dry run:

```bash
./scripts/install-smartagent-launcher --dry-run
```

The default install directory is `$HOME/bin`. If it is not in `PATH`, the installer prints zsh instructions. It does not edit shell profiles unless `--write-shell-profile` is explicitly passed.

When the installer is run from inside a Git clone, it saves the current Git repo root from `git rev-parse --show-toplevel`. If Git is unavailable, it uses the current working directory only when the directory passes repo verification.

Sam's local path is a valid example:

```text
/Users/sambehdjou/Documents/AI Super Agent
```

It is not hardcoded as the only valid repo path; cloned repos under other user-owned paths are supported when they pass verification.

## Behavior

```bash
smartagent
smartagent doctor
smartagent status
smartagent qa dashboard
smartagent --doctor
smartagent --repair
smartagent --repair-and-launch
smartagent --repair-venv
smartagent --repo
smartagent --repo-status
smartagent --find-repos
smartagent --set-repo "/path/to/repo"
smartagent --repair-path
smartagent --launcher-version
smartagent --uninstall-help
```

- `smartagent` launches `./scripts/agent --interactive`.
- `smartagent <args>` passes arguments exactly to `./scripts/agent`.
- `smartagent doctor` runs the agent doctor.
- `smartagent --doctor` runs launcher-only diagnostics and does not call LM Studio.

## Repo Discovery And Switching

Repo discovery is bounded. The launcher checks only:

- configured `repo_path`
- `last_known_good_repo_path`
- current working directory
- `$HOME/Documents/AI Super Agent`
- `$HOME/Documents/ai-super-agent`
- `$HOME/AI Super Agent`
- `$HOME/ai-super-agent`
- `$HOME/Desktop/AI Super Agent`
- `$HOME/Desktop/ai-super-agent`
- an explicit `--repo` or `--set-repo` path

It never scans the whole home directory, never uses recursive `find`, and never silently chooses when multiple valid repos exist.

Repo verification requires:

- `smart_agent.py`
- `scripts/agent`
- at least two of `pyproject.toml`, `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/COMMAND_REGISTRY.md`, or `.git`

When `.git` exists, `git rev-parse --show-toplevel` must succeed and the resolved Git root must match the candidate repo path. Verification does not require LM Studio, live providers, package installs, or external services.

Repo inspection and switching:

```bash
smartagent --repo
smartagent --repo-status
smartagent --find-repos
smartagent --set-repo "/path/to/repo"
smartagent --repair-path
smartagent --repair-path --repo "/path/to/repo"
```

- `--repo` prints the configured repo path.
- `--repo-status` verifies the configured repo and returns marker evidence.
- `--find-repos` lists safe likely candidates and their verification status.
- `--set-repo PATH` verifies `PATH` before saving it.
- `--repair-path` updates `repo_path` only when exactly one valid safe candidate exists.
- If multiple repos are valid, the launcher stops and prints choices.
- If no repos are valid, it prints clone/setup instructions.

## Config

The launcher config lives at:

```text
$HOME/.config/ai-super-agent/launcher.json
```

It stores repo path, alias, install directory, timestamps, launcher version, last known good repo/Python, the last repair result, and safe repair preferences.

Required config fields:

- `repo_path`
- `last_known_good_repo_path`
- `alias`
- `install_dir`
- `created_at`
- `updated_at`
- `launcher_version`
- `last_repo_verification_status`
- `last_known_good_python`

## Safe Self-Repair

Level 1 repairs may run during normal launch or `--repair`:

- update the config repo path if exactly one valid repo is found
- update `last_known_good_python`
- choose a Python 3.11+ runtime instead of Apple Python 3.9
- `chmod +x scripts/agent`
- `chmod +x` the launcher wrapper
- create/update the launcher config directory/file
- print PATH setup instructions

Level 2 repairs require explicit commands:

```bash
smartagent --repair-and-launch
smartagent --repair-venv
./scripts/install-smartagent-launcher --repair-wrapper --update
./scripts/install-smartagent-launcher --repair-path --repo "/Users/sambehdjou/Documents/AI Super Agent"
./scripts/install-smartagent-launcher --write-shell-profile
```

Level 3 repairs are never automatic. The launcher prints manual instructions for sudo/system-path writes, Homebrew installs, deleting/rebuilding `.venv`, removing conflicting commands, resetting repo files, or `git clean`.

## Python Selection

The launcher prefers:

1. repo `.venv/bin/python` if Python 3.11+
2. `python3.12`
3. `python3.11`
4. Codex bundled Python runtime if present
5. `python3` only if Python 3.11+

If `.venv` is missing, normal launch can still use a valid Python 3.11+ runtime and prints `smartagent --repair-venv` as the stronger repair command. Existing broken `.venv` directories are not deleted automatically.

## Update And Uninstall

```bash
./scripts/install-smartagent-launcher --update
./scripts/install-smartagent-launcher --alias sa --update
./scripts/install-smartagent-launcher --uninstall
./scripts/install-smartagent-launcher --alias sa --uninstall
```

The installer rejects unsafe aliases, shell metacharacters, slashes, spaces, empty aliases, and aliases that start with a non-letter. Existing PATH command conflicts require `--update`.
