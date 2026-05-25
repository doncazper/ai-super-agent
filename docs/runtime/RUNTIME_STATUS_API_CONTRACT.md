# Runtime Status API Contract

Runtime status payloads are metadata-only.

Required fields:

- `status`
- `mode`
- service count or services list
- feature count or feature list
- workflow count or workflow list
- job count or jobs list
- `lmstudio_checked`
- `personal_data_accessed`
- `background_persistence`

Status endpoints must not call LM Studio, read personal connector data, execute tools, or mutate permissions.

