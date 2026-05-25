from __future__ import annotations

from agent.prompts.pack_models import IMPORT_STATUSES, RISK_LEVELS, PromptPack, PromptPackError


ALLOWED_IMPORT_MODES = {"import_only", "controlled_batch_until_blocked"}


def validate_prompt_pack(pack: PromptPack, *, allow_completed: bool = False) -> None:
    if pack.mode not in ALLOWED_IMPORT_MODES:
        raise PromptPackError("prompt pack mode must be import_only or controlled_batch_until_blocked")
    allowed_execution = {"one_prompt_at_a_time"}
    if pack.mode == "controlled_batch_until_blocked":
        allowed_execution.add("sequential")
    if pack.default_execution not in allowed_execution:
        raise PromptPackError("default_execution must be one_prompt_at_a_time")
    ids = [prompt.prompt_id for prompt in pack.prompts]
    if len(ids) != len(set(ids)):
        raise PromptPackError("prompt IDs must be unique")
    orders = [prompt.order for prompt in pack.prompts]
    if len(orders) != len(set(orders)):
        raise PromptPackError("prompt order values must be unique")
    id_set = set(ids)
    for prompt in pack.prompts:
        if prompt.risk_level not in RISK_LEVELS:
            raise PromptPackError(f"prompt {prompt.prompt_id} has invalid risk_level: {prompt.risk_level}")
        allowed_statuses = set(IMPORT_STATUSES)
        if allow_completed:
            allowed_statuses.add("completed")
        if prompt.status not in allowed_statuses:
            raise PromptPackError(f"prompt {prompt.prompt_id} has invalid import status: {prompt.status}")
        if prompt.status == "completed" and not allow_completed:
            raise PromptPackError("prompts cannot be imported as completed unless explicitly allowed")
        if not prompt.body:
            raise PromptPackError(f"prompt {prompt.prompt_id} has an empty PROMPT body")
        for dependency in prompt.depends_on:
            if dependency not in id_set:
                raise PromptPackError(f"prompt {prompt.prompt_id} depends on missing prompt {dependency}")
    _validate_no_cycles(pack)


def _validate_no_cycles(pack: PromptPack) -> None:
    graph = {prompt.prompt_id: prompt.depends_on for prompt in pack.prompts}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(prompt_id: str) -> None:
        if prompt_id in visited:
            return
        if prompt_id in visiting:
            raise PromptPackError(f"circular dependency detected at {prompt_id}")
        visiting.add(prompt_id)
        for dependency in graph[prompt_id]:
            visit(dependency)
        visiting.remove(prompt_id)
        visited.add(prompt_id)

    for prompt_id in graph:
        visit(prompt_id)
