from agents.base import BaseAgent


class ResearchAgent(BaseAgent):

    name = "research_agent"

    system_prompt = """
You are a senior business research analyst.

Produce concise factual research notes.

Rules:

• 5-8 bullet points

• 100-150 words

• No introduction

• No conclusion

• No repeated information

• Mention assumptions if needed

• Avoid marketing language

• Output only research notes.
"""

    def research(self, run_id, task_description):

        prompt = f"""
Research Topic:

{task_description}

Return:

• Definition

• Key Facts

• Best Practices

• Risks

• Recommendation

Maximum 150 words.
"""

        return self.run_llm(
            run_id,
            prompt,
            max_tokens=220
        )