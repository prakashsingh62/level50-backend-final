# core/contracts.py

from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime
import uuid


def new_trace_id() -> str:
    return str(uuid.uuid4())


@dataclass
class TraceContext:
    trace_id: str
    timestamp: str

    @staticmethod
    def create():
        return TraceContext(
            trace_id=new_trace_id(),
            timestamp=datetime.utcnow().isoformat()
        )


@dataclass
class Decision:
    action: str
    reason: str


@dataclass
class AuditEvent:
    trace_id: str
    stage: str
    payload: Dict[str, Any]
    timestamp: str


@dataclass
class PipelineResult:
    status: str
    trace_id: str
    data: Dict[str, Any]
