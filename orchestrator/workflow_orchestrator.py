"""
Workflow Orchestrator: the piece labeled "Workflow Orchestrator" in the
diagram. Walks the Task Graph wave by wave (respecting dependencies),
dispatches each node to Research Agent / Tool Router / Memory Agent
based on its type, fills in `result`, then hands the completed graph to
the Writer Agent for the draft.
"""
from models.schemas import TaskGraph, TaskType
from orchestrator.task_graph import topological_waves
from orchestrator.tool_router import run_tool
from agents.research_agent import ResearchAgent
from agents.memory_agent import MemoryAgent
from agents.writer_agent import WriterAgent
from utils.logger import audit

research_agent = ResearchAgent()
memory_agent = MemoryAgent()
writer_agent = WriterAgent()


def _execute_node(run_id: str, task_graph: TaskGraph, node_id: str) -> None:
    node = task_graph.get_node(node_id)
    node.status = "running"
    audit(run_id, "orchestrator.node_start", {"node_id": node_id, "type": node.type.value})

    if node.type == TaskType.RESEARCH:
        node.result = research_agent.research(run_id, node.description)
    elif node.type == TaskType.TOOL:
        node.result = run_tool(run_id, node.tool_name or "", node.description)
    elif node.type == TaskType.MEMORY:
        node.result = memory_agent.recall(run_id, node.description)

    #memory_agent.store(run_id, node.id, node.result or "")
    memory_agent.store(
    run_id=run_id,
    node_id=node.id,
    task=node.description,
    result=node.result or "",
    )
    node.status = "done"
    audit(run_id, "orchestrator.node_done", {"node_id": node_id})


def execute_task_graph(run_id: str, task_graph: TaskGraph) -> str:
    """Run every node in dependency order, then produce the draft via Writer Agent."""
    waves = topological_waves(task_graph)
    audit(run_id, "orchestrator.waves_planned", {"waves": waves})

    for wave in waves:
        # Nodes within a wave have no interdependency, so in a real deployment
        # these could be dispatched with asyncio.gather / a thread pool.
        for node_id in wave:
            _execute_node(run_id, task_graph, node_id)

    draft = writer_agent.write(run_id, task_graph)
    audit(run_id, "orchestrator.draft_ready", {"length": len(draft)})
    return draft
