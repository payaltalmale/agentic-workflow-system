"""
DAG utilities: given a TaskGraph, produce execution "waves" -- groups of
node ids whose dependencies are all satisfied, so independent nodes
(e.g. two research tasks with no shared dependency) can run concurrently.
"""
from models.schemas import TaskGraph


def topological_waves(task_graph: TaskGraph) -> list[list[str]]:
    """Return a list of waves; each wave is a list of node ids safe to run in parallel."""
    remaining = {n.id: set(n.depends_on) for n in task_graph.nodes}
    done: set[str] = set()
    waves: list[list[str]] = []

    while remaining:
        ready = [nid for nid, deps in remaining.items() if deps.issubset(done)]
        if not ready:
            raise ValueError(f"Cycle detected or unresolved dependency among: {list(remaining)}")
        waves.append(ready)
        for nid in ready:
            done.add(nid)
            del remaining[nid]

    return waves
