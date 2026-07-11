"""
The "Reflection Agent -> Self Evaluation Agent -> Quality Score > 60? ->
Rewrite Agent (retry loop)" portion of the diagram, isolated from the
main orchestrator since it's a distinct retry loop with its own exit
condition (score threshold or max retries).
"""
from agents.reflection_agent import ReflectionAgent
from agents.self_eval_agent import SelfEvalAgent
from agents.rewrite_agent import RewriteAgent
from config import settings
from utils.logger import audit

reflection_agent = ReflectionAgent()
self_eval_agent = SelfEvalAgent()
rewrite_agent = RewriteAgent()


def refine_until_quality(run_id: str, draft: str) -> tuple[str, int, int]:
    """
    Returns (final_draft, final_score, retries_used).
    Loops: critique -> score -> (rewrite -> repeat) until score clears
    settings.quality_threshold or settings.max_rewrite_retries is hit.
    """
    current_draft = draft
    retries_used = 0

    for attempt in range(settings.max_rewrite_retries + 1):
        critique = reflection_agent.critique(run_id, current_draft)
        score = self_eval_agent.score(run_id, current_draft, critique)
        audit(run_id, "reflection_loop.scored", {"attempt": attempt, "score": score})

        if score > settings.quality_threshold:
            return current_draft, score, retries_used

        if attempt == settings.max_rewrite_retries:
            # Out of retries -- return best effort rather than looping forever.
            audit(run_id, "reflection_loop.max_retries_hit", {"final_score": score})
            return current_draft, score, retries_used

        current_draft = rewrite_agent.rewrite(run_id, current_draft, critique)
        retries_used += 1
        audit(run_id, "reflection_loop.rewritten", {"retry_number": retries_used})

    return current_draft, 0, retries_used
