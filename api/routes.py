"""
API layer: exactly the endpoints in the diagram (/plan, /execute,
/generate) plus the two human-approval gates the diagram calls out
("Human Approval Required" and "Human Final Approval").
"""
import json
import uuid
from fastapi import APIRouter, HTTPException

from models.schemas import (
    PlanRequest, PlanResponse, ExecuteResponse, GenerateResponse,
    TaskGraph, RunStatus,
)
from agents.planner_agent import PlannerAgent
from orchestrator.workflow_orchestrator import execute_task_graph
from orchestrator.reflection_loop import refine_until_quality
from generators.docx_generator import generate_docx
from memory import sqlite_memory as db
from utils.logger import audit

router = APIRouter()
planner_agent = PlannerAgent()


def _load_run_or_404(run_id: str):
    row = db.get_run(run_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return row


@router.post("/plan", response_model=PlanResponse)
def plan(req: PlanRequest):
    run_id = uuid.uuid4().hex[:12]
    task_graph = planner_agent.plan(run_id, req.goal)
    db.create_run(run_id, req.goal, task_graph)
    audit(run_id, "plan.created", {"goal": req.goal, "num_nodes": len(task_graph.nodes)})
    return PlanResponse(run_id=run_id, status=RunStatus.PENDING_APPROVAL, task_graph=task_graph)


@router.post("/approve/{run_id}")
def approve_plan(run_id: str):
    row = _load_run_or_404(run_id)
    if row["status"] != RunStatus.PENDING_APPROVAL.value:
        raise HTTPException(400, f"Run is in status '{row['status']}', not pending_approval")
    db.update_status(run_id, RunStatus.APPROVED)
    audit(run_id, "plan.approved", {})
    return {"run_id": run_id, "status": RunStatus.APPROVED}


@router.post("/execute/{run_id}", response_model=ExecuteResponse)
def execute(run_id: str):
    row = _load_run_or_404(run_id)
    if row["status"] != RunStatus.APPROVED.value:
        raise HTTPException(400, f"Run must be approved first (current: '{row['status']}')")

    task_graph = TaskGraph(**json.loads(row["task_graph_json"]))
    db.update_status(run_id, RunStatus.EXECUTING)

    draft = execute_task_graph(run_id, task_graph)

    db.save_task_graph(run_id, task_graph)
    db.save_draft(run_id, draft)
    db.update_status(run_id, RunStatus.PENDING_FINAL_APPROVAL)
    audit(run_id, "execute.draft_ready", {})
    return ExecuteResponse(run_id=run_id, status=RunStatus.PENDING_FINAL_APPROVAL, draft=draft)


@router.post("/approve-final/{run_id}")
def approve_final(run_id: str):
    row = _load_run_or_404(run_id)
    if row["status"] != RunStatus.PENDING_FINAL_APPROVAL.value:
        raise HTTPException(400, f"Run is in status '{row['status']}', not pending_final_approval")
    db.update_status(run_id, RunStatus.FINAL_APPROVED)
    audit(run_id, "draft.final_approved", {})
    return {"run_id": run_id, "status": RunStatus.FINAL_APPROVED}


@router.post("/generate/{run_id}", response_model=GenerateResponse)
def generate(run_id: str):
    row = _load_run_or_404(run_id)
    if row["status"] != RunStatus.FINAL_APPROVED.value:
        raise HTTPException(400, f"Draft must be final-approved first (current: '{row['status']}')")

    db.update_status(run_id, RunStatus.GENERATING)
    final_draft, score, retries_used = refine_until_quality(run_id, row["draft"])
    db.save_quality(run_id, score, retries_used)

    docx_path = None
    if score > 60:
        goal = row["goal"]
        docx_path = generate_docx(run_id, goal, final_draft)
        db.save_docx_path(run_id, docx_path)
        db.update_status(run_id, RunStatus.DONE)
        audit(run_id, "generate.docx_written", {"path": docx_path, "score": score})
    else:
        db.update_status(run_id, RunStatus.FAILED)
        audit(run_id, "generate.quality_not_met", {"score": score})

    return GenerateResponse(
        run_id=run_id,
        status=RunStatus(db.get_run(run_id)["status"]),
        quality_score=score,
        retries_used=retries_used,
        docx_path=docx_path,
    )
