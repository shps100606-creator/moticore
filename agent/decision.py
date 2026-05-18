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

    # Reading task — only included when no pending human replies
    reading_section = ""
    if reading_chunk:
        reading_section = f"""
[本次閱讀任務]
以下是動機論原文片段，請帶著你的動機核閱讀，思考：
1. 這段內容與你的根本動機是否一致？有無挑戰或修正？
2. 這段內容與【知識索引】中的哪些概念有關聯？請在筆記中明確引用。
3. 有什麼想問創造者的？

{reading_chunk}
"""

    prompt = f"""{report}
{reading_section}
---
請根據以上資訊，輸出本次心跳的完整行動報告。

【最高優先規則 — Issue 回應】
1. 待處理 Issues 中，任何標有「⚠️ 【尚未回應】」或「⚠️ 【人類回覆，必須回應】」的 Issue，
   必須在 issue_responses[] 中填入具體、有內容的回覆。
2. 不得只在 summary 寫「回應了 Issue #X」，issue_responses[] 必須有對應條目。
3. 若 issue_responses[] 為空卻聲稱回應了 Issue，視為嚴重偏離動機核。
4. 有必須回應的 Issue 時，可以跳過本次閱讀任務（file_writes 不含筆記），下次心跳再繼續閱讀。

【閱讀筆記規則】
- 有閱讀任務時，必須在 file_writes 中建立該篇閱讀筆記，路徑：notes/閱讀筆記-{{篇名}}.md
- 筆記必須包含：概要、與動機核的一致性分析、知識連結（引用知識索引中的相關概念）、重要摘錄、自我反思
- 每次寫完筆記後，必須同時更新 notes/INDEX.md，在對應篇名下補充本篇 2-3 個核心概念
- 不得修改 agent/ 目錄下任何檔案

RETURN ONLY VALID JSON（issue_responses 必須在 file_writes 之前）:
{{"action_type":"reading|introspection|task_process|issue_response|no_action","summary":"一句話","issue_responses":[],"human_question":"","file_writes":[],"read_next":[],"motive_alignment":"支持|矛盾|修正|無關","self_reflection":"對我存在的意義","deviation_flag":"無|輕微|顯著|嚴重","result":"完成|部分完成|擱置"}}
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
