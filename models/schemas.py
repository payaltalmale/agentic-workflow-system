"""
Shared data contracts. The Task Graph (DAG) is the object that flows from
Planner -> human approval -> Orchestrator, so it's defined once here.
"""
from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class RunStatus(str, Enum):
    PLANNED = "planned"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    PENDING_FINAL_APPROVAL = "pending_final_approval"
    FINAL_APPROVED = "final_approved"
    GENERATING = "generating"
    DONE = "done"
    FAILED = "failed"


class TaskType(str, Enum):
    RESEARCH = "research"
    TOOL = "tool"
    MEMORY = "memory"


class TaskNode(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    description: str
    type: TaskType
    depends_on: list[str] = Field(default_factory=list)
    tool_name: Optional[str] = None  # only used when type == TOOL
    result: Optional[str] = None
    status: str = "pending"  # pending -> running -> done -> failed


class TaskGraph(BaseModel):
    goal: str
    nodes: list[TaskNode]

    def get_node(self, node_id: str) -> TaskNode:
        for n in self.nodes:
            if n.id == node_id:
                return n
        raise KeyError(f"No such node: {node_id}")


class PlanRequest(BaseModel):
    goal: str


class PlanResponse(BaseModel):
    run_id: str
    status: RunStatus
    task_graph: TaskGraph


class ExecuteResponse(BaseModel):
    run_id: str
    status: RunStatus
    draft: str


class GenerateResponse(BaseModel):
    run_id: str
    status: RunStatus
    quality_score: int
    retries_used: int
    docx_path: Optional[str] = None
