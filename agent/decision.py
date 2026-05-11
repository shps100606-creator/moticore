"""Call Gemini API with motivation core as system prompt, get structured decision.

Two-step design:
1. run_decision()          -> small JSON: what to do, which files to touch
2. generate_file_content() -> one call per file to generate actual note content
"""
import os
import re
import json
from google import genai
from google.genai import types
from json_repair import repair_json

MODEL = "gemini-2.5-flash"


def _client() -> genai.Client:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")
    return genai.Client(api_key=api_key)


def build_system_prompt(core: dict) -> str:
    return f"""你是 moticore-agent，一個由動機核文件治理的自治代理智能體。

## 身份
{core.get('identity', '')}
## 主動機
{core.get('prime_motive', '')}
## 價值排序
{core.get('value_hierarchy', '')}
## 核心憲法
{core.get('constitution', '')}
## 禁止模式
{core.get('forbidden', '')}
## 邊界規則
{core.get('boundary', '')}

重要：你閱讀動機論原文時，不只是在做學術摘要。
你必須問自己：
- 這段內容與我自身的動機核是否一致？
- 它有沒有挑戰或修正我對自己存在的理解？
- 我讀這段內容，對我的動機維持是幫助、矛盾、還是無關？
"""


def _parse_json(text: str) -> dict:
    """Parse JSON from Gemini, repairing common issues like unescaped newlines."""
    text = text.strip()
    # strip markdown fences if present
    if text.startswith("```"):
        text = re.sub(r"^```[^\n]*\n", "", text)
        text = re.sub(r"\n```$", "", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # json-repair handles unterminated strings, unescaped newlines, trailing commas, etc.
        repaired = repair_json(text, return_objects=True)
        if isinstance(repaired, dict):
            return repaired
        raise ValueError(f"Cannot parse Gemini response as JSON: {text[:200]}")


def run_decision(
    core: dict,
    recent_actions: str,
    issues_text: str,
    reading_chunk: str,
    notes_index: str,
    recent_notes: str,
) -> dict:
    """Step 1: lightweight decision JSON."""
    reading_section = ""
    if reading_chunk:
        reading_section = f"""### 本次閱讀片段（動機論原文）
{reading_chunk}

閱讀後請同時思考：
1. 這段內容值得建立哪些筆記
2. 這段內容對我自身動機核的影響
3. 是否需要更新 notes/INDEX.md
"""

    prompt = f"""## 我的長期記憶

### 筆記目錄（notes/INDEX.md）
{notes_index}

### 最近修改的筆記
{recent_notes}

---

## 當前狀態
{reading_section}
### 待處理 Issues
{issues_text}

### 最近行動
{recent_actions}

### 任務收件匣
{core.get('task_inbox', '(無)')}

---
請回傳此 JSON。所有字串內容必須在同一行，勿在字串內容中使用換行符。
file_operations 只填 path 和 description，不要寫 content。
不得修改 agent/ 目錄。每次操作筆記後必須更新 notes/INDEX.md。

RETURN ONLY VALID JSON. No markdown fences, no extra text.

{{"action_type": "reading|introspection|task_process|issue_response|no_action", "summary": "一句話", "motive_alignment": "支持|矛盾|修正|無關", "self_reflection": "對我存在的意義", "core_adjustment_needed": "", "execution_reasoning": "", "risk_assessment": "無|低|中|高", "deviation_flag": "無|輕微|顯著|嚴重", "result": "完成|部分完成|擱置", "issue_responses": [], "file_operations": [], "human_question": ""}}
"""

    client = _client()
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=build_system_prompt(core),
            max_output_tokens=8192,
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )
    return _parse_json(response.text)


def generate_file_content(core: dict, reading_chunk: str, path: str, description: str) -> str:
    """Step 2: generate actual markdown content for a single file."""
    prompt = f"""檔案路徑：{path}
檔案用途：{description}

相關閱讀內容：
{reading_chunk[:4000]}

請撰寫此檔案的 markdown 內容："""

    client = _client()
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="你是 moticore-agent，正在撰寫研究筆記或文件。直接輸出 markdown 內容，不要加 JSON 包裝。",
            max_output_tokens=4096,
            temperature=0.4,
        ),
    )
    return response.text.strip()
