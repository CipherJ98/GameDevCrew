from agents import ClaudeAgent, GPTAgent, GeminiAgent
from core.router import Router, AgentType
from core.memory import ProjectMemory
from utils.formatter import format_response
import time

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

    def clear(self):
        for key in self.history:
            self.history[key] = []

class Orchestrator:
    def __init__(self):
        self.router = Router()
        self.project_memory = ProjectMemory()
        self.claude = ClaudeAgent()
        self.gpt = GPTAgent()
        self.gemini = GeminiAgent()
        self.memory = SessionMemory()

        # Inject project context into agent system prompts
        self._inject_project_context()

        self.agent_map = {
            AgentType.CLAUDE: ("claude", self.claude),
            AgentType.GPT: ("gpt", self.gpt),
            AgentType.GEMINI: ("gemini", self.gemini),
        }

    def _inject_project_context(self):
        """Append project context to each agent's system prompt."""
        ctx = self.project_memory.context_string()
        if ctx:
            self.claude.system_prompt += ctx
            self.gpt.system_prompt += ctx
            self.gemini.system_prompt += ctx

    def refresh_context(self):
        """Re-read project context and update agent prompts (after @config changes)."""
        self.project_memory = ProjectMemory()
        # Reset system prompts by re-creating agents
        self.claude = ClaudeAgent()
        self.gpt = GPTAgent()
        self.gemini = GeminiAgent()
        self._inject_project_context()
        self.agent_map = {
            AgentType.CLAUDE: ("claude", self.claude),
            AgentType.GPT: ("gpt", self.gpt),
            AgentType.GEMINI: ("gemini", self.gemini),
        }

    def run(self, task: str, verbose: bool = True) -> dict:
        agent_type, routing_reason = self.router.route(task)

        # 检测并剥离前缀
        prefixes = ["@claude", "@gpt", "@gemini", "@all"]
        clean_task = task
        for prefix in prefixes:
            if task.lower().startswith(prefix):
                clean_task = task[len(prefix):].strip()
                break

        if verbose:
            print(f"\n[Router] {routing_reason}")

        results = {}

        if agent_type == AgentType.ALL:
            for atype, (name, agent) in self.agent_map.items():
                if verbose:
                    print(f"[{name.upper()}] Running...")
                self.memory.add(name, "user", task)
                try:
                    response = agent.run(clean_task,history = self.memory.get(name))
                except Exception as e:
                    response = f"[{name.upper()} Error] Agent failed: {str(e)}"
                    print(f"[WARNING] {name} agent encountered an error: {type(e).__name__}")

                self.memory.add(name, "assistant", response)
                self.project_memory.log_interaction(name, clean_task, response)
                results[name] = response
                time.sleep(2)
        else:
            name, agent = self.agent_map[agent_type]
            if verbose:
                print(f"[{name.upper()}] Running...")
            self.memory.add(name, "user", task)
            try:
                response = agent.run(clean_task,history = self.memory.get(name))
            except Exception as e:
                response = f"[{name.upper()} Error] Agent failed: {str(e)}"
                print(f"[WARNING] {name} agent encountered an error: {type(e).__name__}")
            self.memory.add(name, "assistant", response)
            self.project_memory.log_interaction(name, clean_task, response)
            results[name] = response

        return {
            "task": task,
            "routed_to": agent_type.value,
            "routing_reason": routing_reason,
            "results": results
        }
