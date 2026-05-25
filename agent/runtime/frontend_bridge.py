from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import RuntimePolicyBlockedError
from .kernel import RuntimeKernel


@dataclass(frozen=True)
class FrontendBridgeRequest:
    request_id: str
    request_type: str
    payload: dict[str, Any]
    trust_level: str = "LOCAL_PRIVATE_DATA metadata"


@dataclass(frozen=True)
class FrontendBridgeResponse:
    request_id: str
    status: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"request_id": self.request_id, "status": self.status, "payload": self.payload}


class FrontendBridge:
    def __init__(self, kernel: RuntimeKernel | None = None) -> None:
        self.kernel = kernel or RuntimeKernel()

    def handle(self, request: FrontendBridgeRequest) -> FrontendBridgeResponse:
        if request.request_type in {"approval.approve", "approval.deny", "tool.execute", "policy.change"}:
            raise RuntimePolicyBlockedError("frontend bridge cannot approve, deny, execute tools, or change policy directly")
        if request.request_type == "runtime.status":
            return FrontendBridgeResponse(request.request_id, "ok", self.kernel.status())
        if request.request_type == "runtime.snapshot":
            return FrontendBridgeResponse(request.request_id, "ok", self.kernel.snapshot().to_dict())
        return FrontendBridgeResponse(request.request_id, "unsupported", {"reason": "unsupported frontend bridge request in v1"})

