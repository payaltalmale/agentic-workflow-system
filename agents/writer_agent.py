from agents.base import BaseAgent
from models.schemas import TaskGraph


class WriterAgent(BaseAgent):

    name = "writer_agent"

    system_prompt = """
You are a senior business proposal writer.

Write a professional proposal.

Requirements:

- Use markdown headings.

- Formal language.

- No repetition.

- Use bullet points where appropriate.

- Do not invent statistics.

Include:

# Executive Summary

# Objectives

# Scope

# Current Challenges

# Proposed Solution

# Benefits

# Implementation Plan

# Timeline

# Budget

# Risks

# Conclusion

Return only the proposal.
"""

    def write(self, run_id, task_graph):

        material = "\n\n".join(
            f"{node.description}\n{node.result}"
            for node in task_graph.nodes
        )

        prompt = f"""
Project Goal:

{task_graph.goal}

Research Notes:

{material}

Write the final proposal.
"""

        return self.run_llm(
            run_id,
            prompt,
            max_tokens=2200,
        )