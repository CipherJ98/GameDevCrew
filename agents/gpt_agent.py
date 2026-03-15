from openai import OpenAI
import os

class GPTAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key and api_key != "placeholder" else None
        self.model = "gpt-4o"
        self.system_prompt = """You are a game marketing copywriter specializing in indie games.
You specialize in:
- Writing compelling Steam store descriptions
- Crafting engaging devlog posts and YouTube descriptions
- Creating punchy taglines and feature lists
- Writing press kit content and pitch emails to publishers

Keep tone enthusiastic but authentic — indie game players can smell corporate speak.
Always ask yourself: would a real gamer be excited reading this?"""

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
        return response.choices[0].message.content