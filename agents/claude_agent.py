import anthropic
import os

class ClaudeAgent:
    """
    Claude handles: code writing, debugging, Unity architecture, C# scripts
    """
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

    def run(self, task: str, context: str = "") -> str:
        full_prompt = f"{context}\n\nTask: {task}" if context else task
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self.system_prompt,
            messages=[{"role": "user", "content": full_prompt}]
        )
        return message.content[0].text
