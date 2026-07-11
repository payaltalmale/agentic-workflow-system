"""
Reflection Agent: critiques the current draft, pointing out weaknesses
(structure, clarity, missing evidence, tone). Its output feeds directly
into the Self Evaluation Agent's scoring and the Rewrite Agent's fixes.
"""
from agents.base import BaseAgent


class ReflectionAgent(BaseAgent):

    name = "reflection_agent"

    system_prompt = """
You are a senior proposal reviewer.

Review the proposal using these criteria:

1. Structure

2. Clarity

3. Completeness

4. Professional Tone

5. Grammar

For each criterion:

- mention strengths

- mention weaknesses

Finally give a numbered list of improvements.

Do not rewrite the proposal.
"""

    def critique(self, run_id: str, draft: str) -> str:
        return self.run_llm(run_id, f"Draft to critique:\n\n{draft}")
