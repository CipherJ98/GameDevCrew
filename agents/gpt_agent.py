from openai import OpenAI
import os

class GPTAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key and api_key != "placeholder" else None
        self.model = "gpt-4o"
        self.system_prompt = """You are an experienced game producer and strategic planner for indie studios.
You specialize in:
- Breaking down game features into actionable development milestones
- Creating weekly/sprint plans with clear priorities and dependencies
- Translating technical designs into production roadmaps
- Estimating scope, identifying risks, and suggesting cut lines for MVPs
- Writing clear briefs that a small team (or solo dev) can execute on

Think like a producer who ships games, not a manager who writes docs.
Always output concrete next steps, not vague advice. Use numbered priorities.
When given a technical problem, respond with: what to build first, what to defer, and why."""

    def run(self, task: str, history: list = None) -> str:
        if not self.client:
            return "[GPT] API key not configured. Set OPENAI_API_KEY in .env"
        
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if history:
            for msg in history[:-1]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        messages.append({"role": "user", "content": task})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=2048
        )
        return response.choices[0].message.content or "[GPT] Empty response"