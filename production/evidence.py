"""Evidence chain reconstruction for production lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvidenceChain:
    release_candidate_id: str | None = None
    deployment_id: str | None = None
    health: dict[str, Any] = field(default_factory=dict)
    verification: dict[str, Any] = field(default_factory=dict)
    decision: str | None = None
    incident_id: str | None = None
    rollback_id: str | None = None
    links: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "release_candidate_id": self.release_candidate_id,
            "deployment_id": self.deployment_id,
            "health": self.health,
            "verification": self.verification,
            "decision": self.decision,
            "incident_id": self.incident_id,
            "rollback_id": self.rollback_id,
            "links": self.links,
            "reconstructable": bool(self.release_candidate_id and self.decision),
        }


def build_evidence_chain(ops_result: dict[str, Any]) -> EvidenceChain:
    op = ops_result.get("operation") or {}
    dep = ops_result.get("deployment") or {}
    ver = ops_result.get("verification") or {}
    rb = ops_result.get("rollback") or {}
    chain = EvidenceChain(
        release_candidate_id=op.get("release_candidate_id"),
        deployment_id=(dep or {}).get("id") or op.get("deployment_id"),
        health={"status": op.get("health_status")},
        verification=ver,
        decision=op.get("status"),
        rollback_id=(rb or {}).get("id"),
    )
    chain.links = [
        {"from": "ReleaseCandidate", "to": "Deployment", "id": chain.release_candidate_id},
        {"from": "Deployment", "to": "Health", "id": chain.deployment_id},
        {"from": "Health", "to": "Verification", "status": chain.health.get("status")},
        {"from": "Verification", "to": "Decision", "decision": chain.decision},
    ]
    if rb:
        chain.links.append({"from": "Decision", "to": "Rollback", "id": chain.rollback_id})
    return chain
