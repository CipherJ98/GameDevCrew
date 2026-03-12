from agents import ClaudeAgent, GPTAgent, GeminiAgent
from core.router import Router, AgentType
from utils.formatter import format_response

class SessionMemory:
    def __init__(self):
        self.history = {
            "claude": [],
            "gpt": [],
            "gemini": []
        }

    def add(self, agent: str, role: str, content: str):
        self.history[agent].append({
            "role": role,
            "content": content
        })

    def get(self, agent: str) -> list:
        return self.history[agent]

class Orchestrator:
    def __init__(self):
        self.router = Router()
        self.claude = ClaudeAgent()
        self.gpt = GPTAgent()
        self.gemini = GeminiAgent()
        self.memory = SessionMemory()

        self.agent_map = {
            AgentType.CLAUDE: ("claude", self.claude),
            AgentType.GPT: ("gpt", self.gpt),
            AgentType.GEMINI: ("gemini", self.gemini),
        }

    def run(self, task: str, verbose: bool = True) -> dict:
        agent_type, routing_reason = self.router.route(task)

        if verbose:
            print(f"\n[Router] {routing_reason}")

        results = {}

        if agent_type == AgentType.ALL:
            for atype, (name, agent) in self.agent_map.items():
                if verbose:
                    print(f"[{name.upper()}] Running...")
                self.memory.add(name, "user", task)
                response = agent.run(task, history=self.memory.get(name))
                self.memory.add(name, "assistant", response)
                results[name] = response
        else:
            name, agent = self.agent_map[agent_type]
            if verbose:
                print(f"[{name.upper()}] Running...")
            self.memory.add(name, "user", task)
            response = agent.run(task, history=self.memory.get(name))
            self.memory.add(name, "assistant", response)
            results[name] = response

        return {
            "task": task,
            "routed_to": agent_type.value,
            "routing_reason": routing_reason,
            "results": results
        }