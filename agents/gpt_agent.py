from openai import OpenAI
import os

class GPTAgent:
    """
    GPT handles: copywriting, Steam descriptions, devlog drafts, marketing content
    """
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"
        self.system_prompt = """You are a game marketing copywriter specializing in indie games.
You specialize in:
- Writing compelling Steam store descriptions
- Crafting engaging devlog posts and YouTube descriptions
- Creating punchy taglines and feature lists
- Writing press kit content and pitch emails to publishers

Keep tone enthusiastic but authentic — indie game players can smell corporate speak.
Always ask yourself: would a real gamer be excited reading this?"""

    def run(self, task: str, context: str = "") -> str:
        full_prompt = f"{context}\n\nTask: {task}" if context else task
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=2048
        )
        return response.choices[0].message.content
