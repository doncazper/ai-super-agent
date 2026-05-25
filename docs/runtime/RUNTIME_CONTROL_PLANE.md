# Runtime Control Plane

The runtime control plane exposes the read-only and metadata-only runtime surface.

## Commands

```bash
python smart_agent.py runtime status
python smart_agent.py runtime doctor
python smart_agent.py runtime services
python smart_agent.py runtime features
python smart_agent.py runtime health
python smart_agent.py jobs list
python smart_agent.py jobs show <job_id>
python smart_agent.py workflows list
python smart_agent.py workflows run <workflow_id>
python smart_agent.py events tail
```

## Frontend Contract

Future UI clients may request status and snapshots. They may not approve actions, deny actions, change policy, execute tools, or perform sends through the runtime bridge.

## Approval Boundary

Approval remains owned by `ApprovalManager` and Action Center. Runtime events or frontend requests are not approval grants.

