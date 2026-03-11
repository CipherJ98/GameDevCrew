import google.genai as genai
import os

class GeminiAgent:
    """
    Gemini handles: research, Unity docs lookup, asset recommendations, market trends
    """
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

    def run(self, task: str, context: str = "") -> str:
        full_prompt = f"{self.system_prompt}\n\nResearch task: {task}"
        if context:
            full_prompt = f"{self.system_prompt}\n\nContext: {context}\n\nResearch task: {task}"
        
        response = self.client.models.generate_content(
            model="models/gemini-2.0-flash",
            contents=full_prompt
        )
        return response.text