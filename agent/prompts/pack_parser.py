from __future__ import annotations

import ast
import re

from agent.prompts.pack_models import PackedPrompt, PromptPack, PromptPackError


PACK_START = "<<<PROMPT_PACK_START>>>"
PACK_END = "<<<PROMPT_PACK_END>>>"
PROMPT_RE = re.compile(r'<<<PROMPT_START\s+id="([^"]+)"\s+order="([0-9]+)">>')


def parse_prompt_pack(text: str) -> PromptPack:
    if text.count(PACK_START) != 1:
        raise PromptPackError("prompt pack must contain exactly one PROMPT_PACK_START")
    if text.count(PACK_END) != 1:
        raise PromptPackError("prompt pack must contain exactly one PROMPT_PACK_END")
    start_index = text.index(PACK_START) + len(PACK_START)
    end_index = text.index(PACK_END)
    if end_index <= start_index:
        raise PromptPackError("PROMPT_PACK_END appears before pack body")
    pack_body = text[start_index:end_index]
    starts = list(PROMPT_RE.finditer(pack_body))
    if not starts:
        raise PromptPackError("prompt pack contains no prompts")
    header = pack_body[: starts[0].start()]
    pack_metadata = _parse_key_values(header)
    prompts: list[PackedPrompt] = []
    for index, match in enumerate(starts):
        prompt_id = match.group(1)
        order = int(match.group(2))
        content_start = match.end()
        next_start = starts[index + 1].start() if index + 1 < len(starts) else len(pack_body)
        block = pack_body[content_start:next_start]
        end_marker = f'<<<PROMPT_END id="{prompt_id}">>'
        if end_marker not in block:
            raise PromptPackError(f"prompt {prompt_id} is missing matching PROMPT_END")
        prompt_content, trailing = block.split(end_marker, 1)
        if trailing.strip():
            raise PromptPackError(f"unexpected content after PROMPT_END for {prompt_id}")
        prompts.append(_parse_prompt(prompt_id, order, prompt_content))
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
