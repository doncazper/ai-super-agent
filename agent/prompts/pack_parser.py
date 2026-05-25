from __future__ import annotations

import ast
import re

from agent.prompts.pack_models import PackedPrompt, PromptPack, PromptPackError


PACK_START = "<<<PROMPT_PACK_START>>>"
PACK_END = "<<<PROMPT_PACK_END>>>"
PROMPT_RE = re.compile(r'<<<PROMPT_START\s+id="([^"]+)"\s+order="([0-9]+)">>')


def parse_prompt_pack(text: str) -> PromptPack:
    start_index = text.find(PACK_START)
    end_index = text.rfind(PACK_END)
    if start_index == -1:
        raise PromptPackError("prompt pack must contain PROMPT_PACK_START")
    if end_index == -1:
        raise PromptPackError("prompt pack must contain PROMPT_PACK_END")
    start_index += len(PACK_START)
    if end_index <= start_index:
        raise PromptPackError("PROMPT_PACK_END appears before pack body")
    pack_body = text[start_index:end_index]
    first_start = PROMPT_RE.search(pack_body)
    if first_start is None:
        raise PromptPackError("prompt pack contains no prompts")
    header = pack_body[: first_start.start()]
    if PACK_START in header or PACK_END in header:
        raise PromptPackError("pack metadata contains unexpected prompt-pack delimiter")
    pack_metadata = _parse_key_values(header)
    prompts: list[PackedPrompt] = []
    cursor = first_start.start()
    while cursor < len(pack_body):
        match = PROMPT_RE.search(pack_body, cursor)
        if match is None:
            if pack_body[cursor:].strip():
                raise PromptPackError("unexpected content after final PROMPT_END")
            break
        prompt_id = match.group(1)
        order = int(match.group(2))
        content_start = match.end()
        end_marker = f'<<<PROMPT_END id="{prompt_id}">>'
        end_marker_index = pack_body.find(end_marker, content_start)
        if end_marker_index == -1:
            raise PromptPackError(f"prompt {prompt_id} is missing matching PROMPT_END")
        prompt_content = pack_body[content_start:end_marker_index]
        prompts.append(_parse_prompt(prompt_id, order, prompt_content))
        cursor = end_marker_index + len(end_marker)
    return PromptPack(
        pack_id=_required(pack_metadata, "pack_id", "pack metadata"),
        pack_title=_required(pack_metadata, "pack_title", "pack metadata"),
        mode=pack_metadata.get("mode", "import_only"),
        default_execution=pack_metadata.get("default_execution", "one_prompt_at_a_time"),
        requires_sdlc=_parse_bool(pack_metadata.get("requires_sdlc", "true"), "requires_sdlc"),
        requires_prompt_ledger=_parse_bool(pack_metadata.get("requires_prompt_ledger", "true"), "requires_prompt_ledger"),
        requires_feature_maturity_update=_parse_bool(
            pack_metadata.get("requires_feature_maturity_update", "true"),
            "requires_feature_maturity_update",
        ),
        prompts=prompts,
        metadata=pack_metadata,
        raw_text=text,
    )


def _parse_prompt(prompt_id: str, order: int, content: str) -> PackedPrompt:
    if "\nPROMPT:\n" not in content and "\r\nPROMPT:\r\n" not in content:
        raise PromptPackError(f"prompt {prompt_id} is missing PROMPT body")
    marker = "\nPROMPT:\n" if "\nPROMPT:\n" in content else "\r\nPROMPT:\r\n"
    metadata_text, body = content.split(marker, 1)
    metadata = _parse_key_values(metadata_text)
    return PackedPrompt(
        prompt_id=prompt_id,
        order=order,
        title=_required(metadata, "title", prompt_id),
        category=_required(metadata, "category", prompt_id),
        risk_level=_required(metadata, "risk_level", prompt_id),
        approval_gate=_parse_bool(_required(metadata, "approval_gate", prompt_id), "approval_gate"),
        depends_on=_parse_depends_on(_required(metadata, "depends_on", prompt_id), prompt_id),
        status=_required(metadata, "status", prompt_id),
        body=body,
        metadata=metadata,
    )


def _parse_key_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def _required(metadata: dict[str, str], key: str, context: str) -> str:
    value = metadata.get(key, "").strip()
    if not value:
        raise PromptPackError(f"{context} is missing required metadata: {key}")
    return value


def _parse_bool(value: str, field: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    raise PromptPackError(f"{field} must be true or false")


def _parse_depends_on(value: str, prompt_id: str) -> list[str]:
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        raise PromptPackError(f"prompt {prompt_id} depends_on must be a list")
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise PromptPackError(f"prompt {prompt_id} depends_on must be a list of strings")
    return parsed
