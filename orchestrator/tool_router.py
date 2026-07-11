"""
Tool Router: maps a task node's `tool_name` to an actual function call.
Add real integrations here (web search, calculator, code execution, a
CRM API, etc.) -- this is the single place that decides how a "tool"
task node actually gets executed.
"""
from utils.logger import audit


def _calculator(expression: str) -> str:
    try:
        # NOTE: eval() here is a placeholder for a real, sandboxed math
        # evaluator (e.g. `numexpr` or `asteval`) before production use.
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"Calculator error: {e}"


def _web_search_stub(query: str) -> str:
    return f"[stub] Would search the web for: {query}"


TOOL_REGISTRY = {
    "calculator": _calculator,
    "web_search": _web_search_stub,
}


def run_tool(run_id: str, tool_name: str, task_description: str) -> str:
    audit(run_id, "tool_router.dispatch", {"tool_name": tool_name})
    handler = TOOL_REGISTRY.get(tool_name)
    if handler is None:
        return f"No tool registered for '{tool_name}'. Task description: {task_description}"
    return handler(task_description)
