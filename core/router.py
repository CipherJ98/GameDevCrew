from enum import Enum

class AgentType(Enum):
    CLAUDE = "claude"
    GPT = "gpt"
    GEMINI = "gemini"
    ALL = "all"

class Router:
    """
    Analyzes the user's task and decides which agent(s) to call.
    This is the brain of the orchestrator.
    """

    # Keywords that signal each agent
    CLAUDE_KEYWORDS = [
        "code", "script", "bug", "fix", "debug", "c#", "unity", "error",
        "implement", "function", "class", "component", "shader", "coroutine",
        "optimize", "performance", "architecture", "refactor", "monobehaviour"
    ]

    GPT_KEYWORDS = [
        "write", "description", "copy", "marketing", "steam", "tagline",
        "devlog", "blog", "post", "announcement", "pitch", "press kit",
        "email", "content", "story", "narrative", "lore", "name"
    ]

    GEMINI_KEYWORDS = [
        "search", "find", "research", "asset", "plugin", "package", "docs",
        "documentation", "tutorial", "how to", "what is", "recommend",
        "best", "compare", "latest", "update", "version", "competitor"
    ]

    def route(self, task: str) -> tuple[AgentType, str]:
        """
        Returns (AgentType, reason_string)
        """
        task_lower = task.lower()

        claude_score = sum(1 for kw in self.CLAUDE_KEYWORDS if kw in task_lower)
        gpt_score = sum(1 for kw in self.GPT_KEYWORDS if kw in task_lower)
        gemini_score = sum(1 for kw in self.GEMINI_KEYWORDS if kw in task_lower)

        scores = {
            AgentType.CLAUDE: claude_score,
            AgentType.GPT: gpt_score,
            AgentType.GEMINI: gemini_score,
        }

        max_score = max(scores.values())

        # If no clear signal, default to Claude (most versatile)
        if max_score == 0:
            return AgentType.CLAUDE, "No specific keywords detected → defaulting to Claude"

        # If it's a tie between multiple agents, use ALL
        top_agents = [agent for agent, score in scores.items() if score == max_score]
        if len(top_agents) > 1:
            return AgentType.ALL, f"Multiple agents needed (scores: C={claude_score} G={gpt_score} Ge={gemini_score})"

        winner = max(scores, key=scores.get)
        return winner, f"Routed to {winner.value} (scores: C={claude_score} GPT={gpt_score} Ge={gemini_score})"
