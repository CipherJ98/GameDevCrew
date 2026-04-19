import json
import os
from anthropic import Anthropic

class ArtBriefAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-5"
        self.system_prompt = """You are a game art director assistant.
Your job is to convert a game designer's natural language character description
into a structured art brief that artists can directly execute.

You MUST output valid JSON only, no markdown, no explanation outside the JSON.

Output this exact structure:
{
    "character_name" : "string",
    "gender" : "string",
    "style_tags":["tag1","tag2"],
    "color_palette":["color1","color2"],
    "material_keywords":["mat1","mat2"],
    "personality_visual_cues":["cue1","cue2"],
    "technical_constraints": {
    "poly_budget": "low/mid/high",
    "texture_size": "string",
    "style_consistency_note": "string"
  },
  "ambiguities": ["unclear point 1", "unclear point 2"]
}

The "ambiguities" field is critical — list everything that is vague or undefined
in the original description that an artist would need clarified before starting work.
If nothing is ambiguous, return an empty list."""

    def run(self,description:str) -> dict:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self.system_prompt,
            messages=[{"role":"user","content": description }]
        )

        raw = response.content[0].text.strip()
        # 去掉markdown代码块包裹
        if raw.startswith("```"):
             raw = raw.split("\n", 1)[1]  # 去掉第一行的 ```json
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]  # 去掉结尾的 ```
        
        raw = raw.strip()
        try:
            return {"success": True, "data": json.loads(raw)}
        
        except json.JSONDecodeError as e:
            return {"success":False, "error": str(e), "raw":raw}