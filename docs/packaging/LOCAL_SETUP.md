# Local Setup and Packaging Notes

This project is currently packaged as a Python editable install for local development.

## Setup

```bash
/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pip install -e ".[dev]"
```

Set:

```bash
export LMSTUDIO_MODEL="your-local-model"
```

Run:

```bash
python smart_agent.py --no-tools "Explain RCS vs iMessage"
python smart_agent.py tools list
python smart_agent.py config show
python smart_agent.py audit tail
```

## Privacy

Personal-data tools are disabled by default. Write/send tools are disabled by default and require per-action approval.
