import json
from agents.base import BaseAgent
from models.schemas import TaskGraph, TaskNode, TaskType


class PlannerAgent(BaseAgent):
    name = "planner_agent"

    system_prompt = """
You are an expert workflow planning agent.

Your job is to convert a user's goal into a Task Graph (DAG).

Rules:
- Return ONLY valid JSON.
- No markdown.
- No explanation.
- Each node must contain:
    id
    description
    type
    depends_on
    tool_name

Allowed task types:
- research
- tool
- memory

Create between 8 and 12 tasks.

For a business proposal ALWAYS include tasks covering:

1. Project Overview
2. Objectives
3. Current Challenges
4. Proposed AI Solution
5. Benefits
6. Risks
7. Implementation Plan
8. Timeline
9. Budget
10. ROI / Expected Outcomes

Output format:

{
  "nodes":[
    {
      "id":"t1",
      "description":"...",
      "type":"research",
      "depends_on":[],
      "tool_name":null
    }
  ]
}
"""

    def plan(self, run_id: str, goal: str) -> TaskGraph:

        raw = self.run_llm(
            run_id,
            f"Goal:\n{goal}\n\nGenerate the task graph.",
            max_tokens=800
        )

        raw = (
            raw.strip()
            .removeprefix("```json")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )

        data = json.loads(raw)

        nodes = [
            TaskNode(
                id=n["id"],
                description=n["description"],
                type=TaskType(n["type"]),
                depends_on=n.get("depends_on", []),
                tool_name=n.get("tool_name"),
            )
            for n in data["nodes"]
        ]

        return TaskGraph(goal=goal, nodes=nodes)