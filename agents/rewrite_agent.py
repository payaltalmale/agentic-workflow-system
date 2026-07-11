from agents.base import BaseAgent


class RewriteAgent(BaseAgent):

    name = "rewrite_agent"

    system_prompt = """
You are an expert editor.

Revise an existing proposal.

Rules:

- Keep all headings.

- Preserve all correct content.

- Fix ONLY the weaknesses.

- Do NOT shorten the proposal.

- Improve clarity.

- Improve professional tone.

- Remove repetition.

Return only the revised proposal.
"""

    def rewrite(self, run_id, draft, critique):

        prompt = f"""
Original Proposal:

{draft}

Reviewer Feedback:

{critique}

Revise the proposal by addressing every issue.

Return the complete revised proposal.
"""

        return self.run_llm(
            run_id,
            prompt,
            max_tokens=2500,
        )