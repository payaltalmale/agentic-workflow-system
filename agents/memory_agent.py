"""
Memory Agent

Phase 1

Uses SQLite only.

Responsibilities:
- Store completed node outputs.
- Retrieve previous workflow context.
- Summarize it before the next task.
"""

from agents.base import BaseAgent

from memory.sqlite_memory import (
    save_memory,
    get_run_memories,
)


class MemoryAgent(BaseAgent):

    name = "memory_agent"

    system_prompt = """
You summarize previous workflow results.

Only include information that helps complete
the current task.

Ignore unrelated information.
"""

    def recall(
        self,
        run_id: str,
        task_description: str,
    ) -> str:

        memories = get_run_memories(run_id)

        if not memories:
            return "No previous workflow memory."

        context = "\n\n".join(memories)

        prompt = f"""
Current Task

{task_description}

Previous Workflow Results

{context}

Summarize only the information useful
for completing the current task.
"""

        return self.run_llm(run_id, prompt)

    def store(
        self,
        run_id: str,
        node_id: str,
        task: str,
        result: str,
    ) -> None:

        save_memory(
            run_id=run_id,
            node_id=node_id,
            task=task,
            result=result,
        )