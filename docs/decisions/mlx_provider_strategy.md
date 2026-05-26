# MLX Provider Strategy

Status: accepted as stub-only strategy
Date: 2026-05-25
Prompt: BRAIN-07

## Context

MLX and MLX-LM can be attractive local runtimes on Apple Silicon, but they are native-package and model-loading sensitive. Making MLX a hard dependency would violate the Brain Runtime Independence goal of preserving the current LM Studio/Qwopus behavior while keeping startup lightweight.

## Decision

Add a disabled-by-default `mlx` BrainProvider stub and documentation before any MLX implementation. The stub participates in provider registry/status diagnostics but cannot generate text or load models.

The stub supports future `server` and `inprocess` modes in config metadata only:

- `server` can later target a user-managed OpenAI-compatible local MLX server.
- `inprocess` can later target an explicitly installed local MLX runtime.

## Boundaries

BRAIN-07 does not:

- install MLX or MLX-LM;
- download models;
- start a server;
- import `mlx` at startup;
- load a native module;
- load a model;
- call a paid/cloud API;
- enable MCP;
- change the default provider away from LM Studio;
- alter ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger behavior.

## Consequences

The registry can now describe MLX as a future provider without making it available. Future MLX implementation must pass a dedicated prompt and release gate before it can generate text, route fallback traffic, or claim live validation.
