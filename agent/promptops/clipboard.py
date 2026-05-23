from __future__ import annotations

import subprocess


class ClipboardUnavailable(RuntimeError):
    pass


def read_clipboard() -> str:
    try:
        completed = subprocess.run(["pbpaste"], check=True, capture_output=True, text=True, timeout=5)
    except (FileNotFoundError, subprocess.SubprocessError) as exc:
        raise ClipboardUnavailable("clipboard read is unavailable; use --stdin or a file instead") from exc
    return completed.stdout


def write_clipboard(text: str) -> None:
    try:
        subprocess.run(["pbcopy"], input=text, check=True, capture_output=True, text=True, timeout=5)
    except (FileNotFoundError, subprocess.SubprocessError) as exc:
        raise ClipboardUnavailable("clipboard write is unavailable; showing the prompt instead") from exc

