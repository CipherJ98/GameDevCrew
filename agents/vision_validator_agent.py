import anthropic
import os
import json
import base64
from pathlib import Path

class VisionValidatorAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-5"

    def _encode_image(self, image_path: str) -> tuple[str, str]:
        """把图片转成base64"""
        ext = Path(image_path).suffix.lower()
        media_type_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg"
        }
        media_type = media_type_map.get(ext, "image/png")
        with open(image_path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")
        return data, media_type

    def run(self, image_path: str, brief: dict) -> dict:
        if not os.path.exists(image_path):
            return {"success": False, "error": f"图片不存在: {image_path}"}

        image_data, media_type = self._encode_image(image_path)

        # 从brief提取关键检查项
        style_tags = brief.get("style_tags", [])
        color_palette = brief.get("color_palette", [])
        material_keywords = brief.get("material_keywords", [])
        personality_cues = brief.get("personality_visual_cues", [])
        reference_keywords = brief.get("reference_keywords", [])

        prompt = f"""你是游戏美术内容审核员。请对照以下美术brief检查这张图片。

## 美术Brief
- 风格标签: {', '.join(style_tags)}
- 色调要求: {', '.join(color_palette)}
- 材质关键词: {', '.join(material_keywords)}
- 人设视觉特征: {', '.join(personality_cues)}
- 参考风格: {', '.join(reference_keywords)}

## 请检查以下四项，每项给出 pass/fail 和简短理由：

1. **色调匹配**: 图片主色调是否符合brief要求？
2. **视觉元素**: 图片是否包含brief中描述的关键视觉特征？
3. **风格一致性**: 整体风格是否符合brief的风格标签？
4. **是否偏题**: 图片内容是否与brief描述明显不符？

## 输出格式（只输出JSON，不要其他文字）：
{{
  "color_match": {{"result": "pass/fail", "reason": "简短说明"}},
  "visual_elements": {{"result": "pass/fail", "reason": "简短说明"}},
  "style_consistency": {{"result": "pass/fail", "reason": "简短说明"}},
  "off_topic": {{"result": "pass/fail", "reason": "简短说明，pass表示没有偏题"}},
  "overall": "pass/fail",
  "summary": "一句话总结"
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]
        )

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

        try:
            result = json.loads(raw)
            return {"success": True, "data": result, "file": os.path.basename(image_path)}
        except json.JSONDecodeError as e:
            return {"success": False, "error": str(e), "raw": raw}