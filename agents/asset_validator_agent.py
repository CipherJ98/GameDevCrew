import json
import re
import os
from anthropic import Anthropic
from PIL import Image
from PIL.PngImagePlugin import PngInfo

class AssetValidatorAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-5"

        self.rules = {
            "allowed_formats": ["PNG"],
            "allowed_color_modes": ["RGBA"],
            "power_of_two": True,
            "max_size_kb": 2048,
            "naming_pattern": r"^[a-z0-9_]+\.png$",
            "metadata_required": ["prompt", "seed"]
        }

    def _is_power_of_two(self, n: int) -> bool:
        return n > 0 and (n & (n - 1)) == 0

    def _check_single(self, filepath: str) -> dict:
        filename = os.path.basename(filepath)
        issues = []
        info = {}

        #format validation
        ext = filename.rsplit(".", 1)[-1].upper() if "." in filename else ""
        if ext not in self.rules["allowed_formats"]:
            issues.append(f"格式错误: {ext}，需要PNG")

        #naming validation
        if not re.match(self.rules["naming_pattern"], filename):
            issues.append(f"命名不规范: '{filename}'，只允许小写字母/数字/下划线")

        #file_size validation
        size_kb = os.path.getsize(filepath) / 1024
        info["size_kb"] = round(size_kb, 1)
        if size_kb > self.rules["max_size_kb"]:
            issues.append(f"文件过大: {size_kb:.0f}KB，上限{self.rules['max_size_kb']}KB")
        
        #image_properties
        try:
            with Image.open(filepath) as img:
                w, h = img.size
                info["width"] = w
                info["height"] = h
                info["color_mode"] = img.mode

                # 色彩模式
                if img.mode not in self.rules["allowed_color_modes"]:
                    issues.append(f"色彩模式错误: {img.mode}，需要RGBA")

                # 2的幂次
                if self.rules["power_of_two"]:
                    if not self._is_power_of_two(w):
                        issues.append(f"宽度{w}不是2的幂次（64/128/256/512/1024/2048）")
                    if not self._is_power_of_two(h):
                        issues.append(f"高度{h}不是2的幂次")

                # metadata检查
                meta = img.info or {}
                missing_meta = [
                    k for k in self.rules["metadata_required"]
                    if k not in meta
                ]
                if missing_meta:
                    issues.append(f"缺少metadata字段: {', '.join(missing_meta)}")
                else:
                    info["metadata"] = {k: meta[k] for k in self.rules["metadata_required"]}

        except Exception as e:
            issues.append(f"无法读取图像: {str(e)}")

        return {
            "file": filename,
            "passed": len(issues) == 0,
            "issues": issues,
            "info": info
        }

    def run(self, folder_path: str) -> dict:
        if not os.path.isdir(folder_path):
            return {"success": False, "error": f"路径不存在: {folder_path}"}

        files = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".tga", ".psd"))
        ]

        if not files:
            return {"success": False, "error": "文件夹里没有图片文件"}

        results = []
        for f in files:
            full_path = os.path.join(folder_path, f)
            results.append(self._check_single(full_path))

        passed = [r for r in results if r["passed"]]
        failed = [r for r in results if not r["passed"]]

        # LLM生成修改建议
        suggestion = ""
        if failed:
            failed_summary = json.dumps(failed, ensure_ascii=False, indent=2)
            response = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                system="你是游戏美术技术规范专家，用简洁中文给美术同学写修改建议，每条问题一句话说清楚怎么改。",
                messages=[{
                    "role": "user",
                    "content": f"以下资产校验失败，请给出修改建议：\n{failed_summary}"
                }]
            )
            suggestion = response.content[0].text

        return {
            "success": True,
            "summary": {
                "total": len(results),
                "passed": len(passed),
                "failed": len(failed)
            },
            "results": results,
            "suggestions": suggestion
        }