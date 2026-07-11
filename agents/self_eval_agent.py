"""
Self Evaluation Agent: takes the draft + reflection critique and produces
a single integer quality score 0-100. This score drives the retry loop
in the orchestrator (score > threshold -> DOCX Generator, else -> Rewrite).
"""
import re
from agents.base import BaseAgent


class SelfEvalAgent(BaseAgent):
    name = "self_eval_agent"
    system_prompt = """
You are a proposal quality evaluator.

Evaluate:

Structure:20

Completeness:20

Clarity:20

Professional Tone:20

Grammar:20

Compute the total.

Return ONLY the final score as an integer between 0 and 100.

Do not explain.

Example:

86
"""

    def score(self, run_id: str, draft: str, critique: str) -> int:
        raw = self.run_llm(
            run_id,
            f"Draft:\n{draft}\n\nCritique:\n{critique}\n\nScore (0-100):",
            max_tokens=10,
        )
        match = re.search(r"\d+", raw)
        return max(0, min(100, int(match.group()))) if match else 0
