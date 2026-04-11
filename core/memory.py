import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

class ProjectMemory:
    """Persistent memory layer for GameDevCrew."""

    def __init__(self):
        _ensure_data_dir()
        self.context_path = os.path.join(DATA_DIR, "project_context.json")
        self.log_path = os.path.join(DATA_DIR, "conversation_log.jsonl")
        self.decisions_path = os.path.join(DATA_DIR, "decisions.json")
        self._context = self._load_context()

    # ── Project Context ──────────────────────────────────────

    def _load_context(self) -> dict:
        if os.path.exists(self.context_path):
            with open(self.context_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "project_name": "",
            "engine": "",
            "platform": "",
            "genre": "",
            "art_style": "",
            "core_gameplay": "",
        }

    def _save_context(self):
        with open(self.context_path, "w", encoding="utf-8") as f:
            json.dump(self._context, f, indent=2, ensure_ascii=False)

    def get_context(self) -> dict:
        return dict(self._context)

    def set_context(self, key: str, value: str):
        self._context[key] = value
        self._save_context()

    def context_string(self) -> str:
        """One-liner injected into agent system prompts."""
        ctx = self._context
        parts = []
        if ctx.get("project_name"):
            parts.append(f"Project: {ctx['project_name']}")
        if ctx.get("engine"):
            parts.append(f"Engine: {ctx['engine']}")
        if ctx.get("platform"):
            parts.append(f"Platform: {ctx['platform']}")
        if ctx.get("genre"):
            parts.append(f"Genre: {ctx['genre']}")
        if ctx.get("art_style"):
            parts.append(f"Art style: {ctx['art_style']}")
        if ctx.get("core_gameplay"):
            parts.append(f"Gameplay: {ctx['core_gameplay']}")
        if not parts:
            return ""
        return "\n\nCurrent project: " + ", ".join(parts)

    # ── Conversation Log ─────────────────────────────────────

    def log_interaction(self, agent: str, task: str, response: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "task": task,
            "response": response,
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_history(self, n: int = 10) -> list[dict]:
        """Return last n interactions from the log."""
        if not os.path.exists(self.log_path):
            return []
        entries = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries[-n:]

    # ── Decision Log ─────────────────────────────────────────

    def _load_decisions(self) -> list[dict]:
        if os.path.exists(self.decisions_path):
            with open(self.decisions_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def add_decision(self, topic: str, decision: str, reasoning: str, agent_source: str):
        decisions = self._load_decisions()
        decisions.append({
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "decision": decision,
            "reasoning": reasoning,
            "agent_source": agent_source,
        })
        with open(self.decisions_path, "w", encoding="utf-8") as f:
            json.dump(decisions, f, indent=2, ensure_ascii=False)

    def get_decisions(self) -> list[dict]:
        return self._load_decisions()
