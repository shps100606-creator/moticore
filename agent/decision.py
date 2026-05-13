"""Consciousness module — single Gemini call per heartbeat.

Receives: MOTIVE.md (system instruction) + pre-processed report + reading chunk
Outputs:  structured action JSON including full file content
"""
import os
import re
import json
from google import genai
from google.genai import types
from json_repair import repair_json

MODEL = "gemini-3.1-flash-lite"


def _client() -> genai.Client:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")
    return genai.Client(api_key=api_key)


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[^\n]*\n", "", text)
        text = re.sub(r"\n```$", "", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        repaired = repair_json(text, return_objects=True)
        if isinstance(repaired, dict):
            return repaired
        raise ValueError(f"Cannot parse response as JSON: {text[:200]}")


def run_consciousness(motive: str, report: str, reading_chunk: str) -> dict:
    """Single AI call: motivation core + pre-processed report + reading chunk → action plan."""
    reading_section = ""
    if reading_chunk:
        reading_section = f"""
[本次閱讀任務]
以下是動機論原文片段，請帶著你的動機核閱讀，思考：
1. 這段內容與你的根本動機是否一致？有無挑戰或修正？
2. 值得建立哪些筆記？
3. 有什麼想問創造者的？

{reading_chunk}
"""

    prompt = f"""{report}
{reading_section}
---
請根據以上資訊，輸出本次心跳的完整行動報告。

規則：
- file_writes 的 content 欄位直接包含完整 markdown 內容（可含換行）
- 不得修改 agent/ 目錄下任何檔案
- read_next 填下次想主動閱讀的路徑（最多 5 份）
- 若待處理 Issues 中有人類回覆，必須在 issue_responses 中回應，不得忽略

RETURN ONLY VALID JSON:
{{"action_type":"reading|introspection|task_process|issue_response|no_action","summary":"一句話","motive_alignment":"支持|矛盾|修正|無關","self_reflection":"對我存在的意義","deviation_flag":"無|輕微|顯著|嚴重","result":"完成|部分完成|擱置","issue_responses":[],"file_writes":[],"read_next":[],"human_question":""}}
"""

    client = _client()
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=motive,
            max_output_tokens=8192,
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )
    return _parse_json(response.text)
