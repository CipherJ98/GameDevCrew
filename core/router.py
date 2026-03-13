from enum import Enum

class AgentType(Enum):
    CLAUDE = "claude"
    GPT = "gpt"
    GEMINI = "gemini"
    ALL = "all"

class Router:
    def __init__(self):
        self.claude_keywords = [
            "code", "script", "debug", "fix", "error", "bug",
            "c#", "unity", "function", "class", "implement",
            "architecture", "pattern", "optimize", "refactor"
        ]
        self.gpt_keywords = [
            "write", "description", "steam", "marketing", "copy",
            "devlog", "announcement", "pitch", "press", "trailer",
            "tagline", "email", "post", "blog", "content"
        ]
        self.gemini_keywords = [
            "search", "find", "research", "asset", "docs",
            "documentation", "tutorial", "recommend", "latest",
            "compare", "what is", "how does", "look up"
        ]

    def route(self, task: str) -> tuple[AgentType, str]:
        task_lower = task.lower().strip()

        # Manual override — check for @agent syntax first
        if task_lower.startswith("@claude"):
            clean_task = task[7:].strip()
            return AgentType.CLAUDE, f"Manual override → claude"

        if task_lower.startswith("@gpt"):
            clean_task = task[4:].strip()
            return AgentType.GPT, f"Manual override → gpt"

        if task_lower.startswith("@gemini"):
            clean_task = task[7:].strip()
            return AgentType.GEMINI, f"Manual override → gemini"

        if task_lower.startswith("@all"):
            clean_task = task[4:].strip()
            return AgentType.ALL, f"Manual override → all agents"

        # Keyword scoring
        claude_score = sum(1 for kw in self.claude_keywords if kw in task_lower)
        gpt_score = sum(1 for kw in self.gpt_keywords if kw in task_lower)
        gemini_score = sum(1 for kw in self.gemini_keywords if kw in task_lower)

        scores = {
            AgentType.CLAUDE: claude_score,
            AgentType.GPT: gpt_score,
            AgentType.GEMINI: gemini_score,
        }

        max_score = max(scores.values())

        if max_score == 0:
            return AgentType.CLAUDE, "No specific keywords detected → defaulting to Claude"

        best = max(scores, key=lambda k: scores[k])
        return best, f"Routed to {best.value} (scores: C={claude_score} GPT={gpt_score} Ge={gemini_score})"