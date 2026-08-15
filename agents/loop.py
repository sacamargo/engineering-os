"""Agent execution loop — the Phase 6 primary deliverable.

Task → assign → context → execute → evidence → validate → gate → next/replan/escalate
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from agents.assignment import assign_agent
from agents.changeset import ChangeSet
from agents.coding import DeterministicPlan, run_deterministic
from agents.concurrency import workspace_lock
from agents.context import build_context
from agents.dry_run import project_dry_run
from agents.evidence import ExecutionEvidence, make_evidence, task_may_complete
from agents.failures import classify_agent_failure
from agents.invocation import ToolResult
from agents.lifecycle import transition
from agents.log import ExecutionLog, LogEntry
from agents.model import instantiate
from agents.retry import AttemptRecord, RetryPolicy, backoff_sleep, should_retry
from agents.rollback import rollback_changeset
from agents.runtime import LocalToolRuntime
from agents.sandbox import Workspace
from agents.task_states import can_task_transition, transition_task


@dataclass
class ExecutionResult:
    execution_id: str
    status: str
    task: dict[str, Any]
    agent: dict[str, Any]
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    escalations: list[dict[str, Any]] = field(default_factory=list)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    changeset: dict[str, Any] | None = None
    log: dict[str, Any] | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _new_execution_id(task_id: str) -> str:
    digest = hashlib.sha256(f"{task_id}|{time.time_ns()}".encode()).hexdigest()[:12]
    return f"eos.execution.{digest}"


def _gate_tests_passed(results: list[ToolResult]) -> bool:
    for r in results:
        if r.tool_id == "run_tests":
            return r.success and int(r.output.get("exit_code", 1)) == 0
    return False


def run_execution(
    workspace_root: str | Path,
    task: dict[str, Any],
    plan: DeterministicPlan | None = None,
    *,
    dry_run: bool = False,
    approval_granted: bool = False,
    retry_policy: RetryPolicy | None = None,
    require_tests: bool = True,
    codebase_snapshot_id: str | None = None,
    auto_rollback_on_failure: bool = True,
) -> ExecutionResult:
    """Execute one task with a sandboxed agent. No LLM required when plan is provided."""
    t0 = time.perf_counter()
    execution_id = _new_execution_id(task["id"])
    policy = retry_policy or RetryPolicy()
    workspace = Workspace(workspace_root)
    assignment = assign_agent(task)

    if assignment.executor_kind == "human":
        return ExecutionResult(
            execution_id=execution_id,
            status="NEEDS_HUMAN",
            task=task,
            agent=assignment.to_dict(),
            escalations=[
                {
                    "reason": assignment.reason,
                    "task_id": task["id"],
                    "blocking": True,
                }
            ],
            notes=["Human executor required; AI agent did not run."],
        )

    if dry_run:
        projection = project_dry_run(task, plan)
        return ExecutionResult(
            execution_id=execution_id,
            status="DRY_RUN",
            task=task,
            agent=assignment.to_dict(),
            metrics=projection,
            notes=["Dry run only."],
        )

    if plan is None:
        return ExecutionResult(
            execution_id=execution_id,
            status="NEEDS_INPUT",
            task=task,
            agent=assignment.to_dict(),
            notes=["Deterministic plan required (no LLM bound)."],
        )

    task_status = "pending"
    task_status = transition_task(task_status, "ready")
    task_status = transition_task(task_status, "assigned")

    attempts: list[AttemptRecord] = []
    evidence: list[ExecutionEvidence] = []
    last_failure: dict[str, Any] | None = None
    final_status = "FAILED"
    changeset = ChangeSet(
        id=f"eos.changeset.{uuid.uuid4().hex[:10]}",
        agent_id="",
        task_id=task["id"],
    )
    elog = ExecutionLog(execution_id)

    with workspace_lock(workspace.root):
        for attempt in range(1, policy.max_attempts + 1):
            instance = instantiate(assignment.definition, task["id"])
            instance.status = transition("created", "ready")
            instance.status = transition("ready", "running")
            instance.started_at = time.time()
            changeset.agent_id = instance.id

            ctx = build_context(
                task,
                workspace,
                paths=list(task.get("target_paths") or []),
                max_bytes=assignment.definition.limits.max_context_bytes,
                codebase_snapshot_id=codebase_snapshot_id,
            )
            evidence.append(
                make_evidence(
                    "Execution context built",
                    kind="context",
                    pointer=ctx.workspace_root,
                    task_id=task["id"],
                    agent_id=instance.id,
                    details={"files": ctx.relevant_files, "truncated": ctx.truncated},
                )
            )

            runtime = LocalToolRuntime(
                workspace,
                assignment.definition,
                instance,
                approval_granted=approval_granted,
            )
            task_status = transition_task(task_status, "in_progress") if task_status == "assigned" else task_status

            results = run_deterministic(runtime, plan)
            for r in results:
                elog.add(
                    LogEntry(
                        execution_id=execution_id,
                        task_id=task["id"],
                        agent_id=instance.id,
                        tool_id=r.tool_id,
                        input={},
                        output=r.output,
                        result="success" if r.success else "error",
                        error=r.error,
                        duration_ms=r.duration_ms,
                        evidence=r.evidence,
                    )
                )
                for ev in r.evidence:
                    evidence.append(
                        make_evidence(
                            f"Tool {r.tool_id} produced evidence",
                            kind=str(ev.get("kind") or "tool"),
                            pointer=str(ev.get("path") or ev.get("argv") or r.tool_id),
                            task_id=task["id"],
                            agent_id=instance.id,
                            details=ev,
                        )
                    )

            for w in runtime.write_log:
                changeset.record_write(w["path"], w.get("before"), w["after"])

            # Validation gate: tests if required
            tests_ok = _gate_tests_passed(results) if require_tests else True
            writes_ok = all(r.success for r in results if r.tool_id == "write_file")
            all_ok = all(r.success for r in results) and tests_ok and writes_ok

            if all_ok and task_may_complete(evidence, require_tests=require_tests):
                instance.status = transition(instance.status, "succeeded")
                task_status = transition_task("in_progress", "validating")
                task_status = transition_task("validating", "completed")
                final_status = "SUCCESS"
                evidence.append(
                    make_evidence(
                        "Gate passed: tools succeeded and evidence present",
                        kind="gate",
                        pointer=execution_id,
                        task_id=task["id"],
                        agent_id=instance.id,
                        details={"tests_ok": tests_ok},
                    )
                )
                break

            # Classify failure
            if any("PermissionError" in (r.error or "") for r in results):
                classification = "PERMISSION_FAILURE"
            elif any("Timeout" in (r.error or "") for r in results):
                classification = "TIMEOUT"
            elif require_tests and not tests_ok:
                classification = "VALIDATION_FAILURE"
            elif any(not r.success for r in results):
                classification = "TOOL_FAILURE"
            else:
                classification = "TASK_FAILURE"

            decision = classify_agent_failure(task["id"], classification, "execution attempt failed")
            attempts.append(
                AttemptRecord(
                    attempt=attempt,
                    classification=classification,
                    action=decision.action,
                    error=decision.reason,
                )
            )
            last_failure = decision.to_dict()
            instance.status = transition(
                instance.status if instance.status in {"running", "waiting"} else "running",
                "failed",
            )

            if auto_rollback_on_failure and changeset.diffs:
                rollback_changeset(workspace, changeset)
                evidence.append(
                    make_evidence(
                        "Rollback applied after failed attempt",
                        kind="rollback",
                        pointer=changeset.id,
                        task_id=task["id"],
                        agent_id=instance.id,
                    )
                )
                changeset = ChangeSet(
                    id=f"eos.changeset.{uuid.uuid4().hex[:10]}",
                    agent_id=instance.id,
                    task_id=task["id"],
                )

            if should_retry(classification, attempt, policy):
                backoff_sleep(policy, attempt)
                task_status = "failed"
                task_status = transition_task(task_status, "ready")
                task_status = transition_task(task_status, "assigned")
                continue

            if decision.action == "escalate":
                final_status = "NEEDS_HUMAN"
            elif decision.action == "replan":
                final_status = "REPLAN"
            else:
                final_status = "FAILED"
            if can_task_transition(task_status, "failed"):
                task_status = transition_task(task_status, "failed")
            elif can_task_transition("in_progress", "failed"):
                task_status = transition_task("in_progress", "failed")
            break

    artifacts = []
    if final_status == "SUCCESS" and changeset.diffs:
        artifacts.append(
            {
                "id": f"eos.artifact.{task['id'].split('.')[-1]}.changeset",
                "type": "changeset",
                "title": "Agent ChangeSet",
                "status": "ready_for_review",
                "changeset_id": changeset.id,
            }
        )

    return ExecutionResult(
        execution_id=execution_id,
        status=final_status,
        task={**task, "status": task_status},
        agent=assignment.to_dict(),
        artifacts=artifacts,
        evidence=[e.to_dict() for e in evidence],
        failures=[last_failure] if last_failure and final_status != "SUCCESS" else [],
        escalations=(
            [{"reason": last_failure["reason"]}] if final_status == "NEEDS_HUMAN" and last_failure else []
        ),
        decisions=[{"attempts": [a.to_dict() for a in attempts]}],
        metrics={
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "attempts": len(attempts) + (1 if final_status == "SUCCESS" else 0),
            "tool_log_entries": len(elog.entries),
            "files_touched": len(changeset.diffs),
        },
        changeset=changeset.to_dict() if changeset.diffs else None,
        log=elog.to_dict(),
        notes=[
            "Success requires evidence and gates; agent 'done' is insufficient.",
            "Core runtime does not require an LLM provider.",
        ],
    )
