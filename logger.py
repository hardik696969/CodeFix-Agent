import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path

# ─── Log Directory Setup ─────────────────────────────────────────
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

SESSION_LOG_FILE = LOG_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
MASTER_LOG_FILE = LOG_DIR / "master_log.json"

# ─── Logger Class ────────────────────────────────────────────────
class CodeFixLogger:
    def __init__(self, model: str, session_id: str = None):
        self.model = model
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.session_start = datetime.now().isoformat()
        self.logs = []
        self.stats = {
            "total_requests": 0,
            "successful_fixes": 0,
            "failed_fixes": 0,
            "total_time": 0.0,
            "total_iterations": 0,
            "bugs_fixed": 0
        }

    def log_attempt(
        self,
        buggy_code: str,
        fixed_code: str,
        success: bool,
        error: str,
        explanation: str,
        iteration: int,
        elapsed_time: float,
        category: str = "unknown"
    ):
        entry = {
            "id": str(uuid.uuid4())[:8],
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "category": category,
            "iteration": iteration,
            "elapsed_time": elapsed_time,
            "success": success,
            "buggy_code": buggy_code,
            "fixed_code": fixed_code,
            "error": error,
            "explanation": explanation
        }

        self.logs.append(entry)

        # Update stats
        self.stats["total_requests"] += 1
        self.stats["total_time"] += elapsed_time
        self.stats["total_iterations"] += iteration

        if success:
            self.stats["successful_fixes"] += 1
        else:
            self.stats["failed_fixes"] += 1

        # Save to file
        self._save()

        return entry

    def _save(self):
        session_data = {
            "session_id": self.session_id,
            "model": self.model,
            "session_start": self.session_start,
            "stats": self.stats,
            "logs": self.logs
        }

        # Save session log
        with open(SESSION_LOG_FILE, "w") as f:
            json.dump(session_data, f, indent=2)

        # Update master log
        master_data = []
        if MASTER_LOG_FILE.exists():
            with open(MASTER_LOG_FILE, "r") as f:
                try:
                    master_data = json.load(f)
                except Exception:
                    master_data = []

        # Update or append session
        session_found = False
        for i, s in enumerate(master_data):
            if s.get("session_id") == self.session_id:
                master_data[i] = session_data
                session_found = True
                break

        if not session_found:
            master_data.append(session_data)

        with open(MASTER_LOG_FILE, "w") as f:
            json.dump(master_data, f, indent=2)

    def get_summary(self):
        total = self.stats["total_requests"]
        if total == 0:
            return self.stats

        summary = self.stats.copy()
        summary["accuracy"] = round(
            (self.stats["successful_fixes"] / total) * 100, 1
        )
        summary["avg_time"] = round(
            self.stats["total_time"] / total, 2
        )
        summary["avg_iterations"] = round(
            self.stats["total_iterations"] / total, 2
        )
        return summary