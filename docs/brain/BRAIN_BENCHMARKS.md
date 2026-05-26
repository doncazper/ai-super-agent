# Brain Benchmarks

Status: mock-first v1.

Brain benchmarks provide lightweight provider comparison data without changing the default provider. The safe path uses deterministic mock providers and records latency, success/fail/skip status, provider ID, model ID, and setup errors.

## Commands

```bash
python smart_agent.py brain benchmark --safe
python smart_agent.py brain benchmark --provider mock
python smart_agent.py brain report
```

Live provider benchmarks remain opt-in. The benchmark layer must not install runtimes, download models, start providers, call paid/cloud APIs by default, execute tools directly, access personal data, or bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.

## Report Fields

- `provider`
- `model`
- `latency_ms`
- `status`
- `success`
- `error`
- `personal_data_used=false`
- `high_risk_tools_used=false`

Generated reports are local evidence for maturity tracking; they are not proof that an unconfigured provider is user-ready.
