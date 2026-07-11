"""
Audit logging. Every agent call, approval, and retry gets one line here
and one row in SQLite (see memory/sqlite_memory.py::log_audit_event) so
the whole run can be reconstructed after the fact.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from config import settings

Path(settings.audit_log_path).parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("audit")
logger.setLevel(logging.INFO)
_handler = logging.FileHandler(settings.audit_log_path)
_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(_handler)
logger.addHandler(logging.StreamHandler())  # also print to console


def audit(run_id: str, step: str, detail: dict | str = "") -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "step": step,
        "detail": detail,
    }
    logger.info(json.dumps(entry))
