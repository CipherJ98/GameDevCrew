import anthropic
import os

class ClaudeAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-5"
        self.system_prompt = """You are an expert Unity game developer and C# programmer.
You specialize in:
- Writing clean, optimized Unity C# scripts
- Debugging game logic and performance issues
- Advising on game architecture and design patterns
- Explaining technical concepts clearly for indie developers

Always provide complete, ready-to-use code with comments.
When debugging, explain the root cause before providing the fix."""

    def run(self, task: str, history: list = None) -> str:
        messages = []
        
        if history:
            # Add previous turns but skip the current task (last item)
            for msg in history[:-1]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        messages.append({"role": "user", "content": task})
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self.system_prompt,
            messages=messages
        )
        return response.content[0].text