from __future__ import annotations

import pytest

from agent.runtime.errors import RuntimePolicyBlockedError
from agent.runtime.frontend_bridge import FrontendBridge, FrontendBridgeRequest


def test_frontend_bridge_status_request() -> None:
    response = FrontendBridge().handle(FrontendBridgeRequest("req_1", "runtime.status", {}))
    assert response.status == "ok"
    assert response.payload["personal_data_accessed"] is False


def test_frontend_bridge_cannot_approve_or_execute() -> None:
    bridge = FrontendBridge()
    with pytest.raises(RuntimePolicyBlockedError):
        bridge.handle(FrontendBridgeRequest("req_1", "approval.approve", {"action_id": "act_1"}))
    with pytest.raises(RuntimePolicyBlockedError):
        bridge.handle(FrontendBridgeRequest("req_2", "tool.execute", {"tool": "email.send"}))

