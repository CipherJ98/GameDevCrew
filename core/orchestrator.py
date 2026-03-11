from agents import ClaudeAgent, GPTAgent, GeminiAgent
from core.router import Router, AgentType
from utils.formatter import format_response

class Orchestrator:
    """
    The main controller. Receives tasks, routes them, calls agents, returns results.
    """
    def __init__(self):
        self.router = Router()
        self.claude = ClaudeAgent()
        self.gpt = GPTAgent()
        self.gemini = GeminiAgent()

        self.agent_map = {
            AgentType.CLAUDE: self.claude,
            AgentType.GPT: self.gpt,
            AgentType.GEMINI: self.gemini,
        }

    def run(self, task: str, verbose: bool = True) -> dict:
        """
        Main entry point. Returns a dict with routing info + results.
        """
        agent_type, routing_reason = self.router.route(task)

        if verbose:
            print(f"\n[Router] {routing_reason}")

        results = {}

        if agent_type == AgentType.ALL:
            # Run all three agents
            for atype, agent in self.agent_map.items():
                if verbose:
                    print(f"[{atype.value.upper()}] Running...")
                results[atype.value] = agent.run(task)
        else:
            agent = self.agent_map[agent_type]
            if verbose:
                print(f"[{agent_type.value.upper()}] Running...")
            results[agent_type.value] = agent.run(task)

        return {
            "task": task,
            "routed_to": agent_type.value,
            "routing_reason": routing_reason,
            "results": results
        }
