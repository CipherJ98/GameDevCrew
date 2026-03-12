import google.genai as genai
import os

class GeminiAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.system_prompt = """You are a game development research assistant.
You specialize in:
- Finding solutions in Unity documentation and forums
- Recommending Unity Asset Store packages with pros/cons
- Researching competitor games and market positioning
- Summarizing Unity release notes and new features
- Finding tutorials and learning resources

Always cite where developers can find more information.
Prioritize official Unity docs and well-known community sources."""

    def run(self, task: str, history: list = None) -> str:
        contents = []
        
        if history:
            for msg in history[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
        
        contents.append({
            "role": "user",
            "parts": [{"text": f"{self.system_prompt}\n\nResearch task: {task}"}]
        })
        
        response = self.client.models.generate_content(
            model="models/gemini-2.0-flash",
            contents=contents
        )
        return response.text