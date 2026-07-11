"""
Every agent (Planner, Research, Writer, Reflection, etc.) subclasses this
so LLM calls and audit logging are handled consistently in one place.
"""
from utils.llm_client import complete
from utils.logger import audit


class BaseAgent:
    name: str = "base_agent"
    system_prompt: str = "You are a helpful assistant."

    def run_llm(self, run_id: str, user_prompt: str, max_tokens: int = 1500) -> str:
        audit(run_id, f"{self.name}.call", {"prompt_preview": user_prompt[:200]})
        result = complete(self.system_prompt, user_prompt, max_tokens=max_tokens)
        audit(run_id, f"{self.name}.result", {"result_preview": result[:200]})
        return result
