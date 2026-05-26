# Command QA Result Schema

Every command run result uses this schema.

| Field | Required | Description |
|---|---|---|
| `run_id` | yes | Stable run id for the QA batch. |
| `command_id` | yes | Command registry id. |
| `command_string` | yes | Redacted command string. |
| `qa_tier` | yes | QA tier number. |
| `risk_level` | yes | Command risk level. |
| `start_time` | yes | UTC ISO timestamp. |
| `duration_ms` | yes | Bounded run duration. |
| `exit_code` | yes | Process exit code, if executed. |
| `redacted_stdout_excerpt` | yes | Short redacted stdout excerpt. |
| `redacted_stderr_excerpt` | yes | Short redacted stderr excerpt. |
| `full_log_path` | yes | Path under `reports/qa/` for the redacted full log. |
| `status` | yes | `passed`, `failed`, `skipped`, `blocked`, or `setup_required`. |
| `failure_type` | no | Normalized failure type. |
| `severity` | no | `P0` through `P4`. |
| `suspected_area` | no | Feature, command group, or module suspected. |
| `linked_bug_id` | no | Bug id generated from this result. |
| `regression_test_path` | no | Regression stub generated from this result. |
| `feature_id` | no | Related feature id. |
| `maturity_impact` | no | Conservative maturity implication. |
| `audit_ids` | no | Audit ids seen or expected, if applicable. |
| `notes` | no | Redacted notes. |

## Failure Types

Allowed failure types include `command_not_found`, `import_error`, `usage_error`, `bad_help`, `bad_output`, `timeout`, `exception`, `policy_failure`, `approval_failure`, `audit_failure`, `redaction_failure`, `provider_missing_bad_error`, `docs_mismatch`, `command_registry_mismatch`, `test_gap`, `flaky`, and `unknown`.

Raw stdout/stderr must not be stored in bug reports. Full logs are redacted before writing.
