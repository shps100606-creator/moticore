"""Call Gemini API with motivation core as system prompt, get structured decision.

Two-step design:
1. run_decision()          -> small JSON: what to do, which files to touch
2. generate_file_content() -> one call per file to generate actual note content
"""
import os
import json
from google import genai
from google.genai import types

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
"""


def run_decision(core: dict, recent_actions: str, issues_text: str, reading_chunk: str = "") -> dict:
    """Step 1: lightweight decision JSON (paths + descriptions only, no file content)."""
    reading_section = ""
    if reading_chunk:
        reading_section = f"""### 本次閱讀片段
{reading_chunk}
閱讀後請决定要建哪些筆記（只列路徑和一句描述）。
"""

    prompt = f"""## 當前狀態
{reading_section}
### 待處理 Issues
{issues_text}

### 最近行動
{recent_actions}

### 任務收件匣
{core.get('task_inbox', '(無)')}

---
請回傳以下 JSON（file_operations 只填 path 和 description，不要寫 content）：
{{
  "action_type": "reading|introspection|task_process|issue_response|no_action",
  "summary": "一句話",
  "motive_alignment": "",
  "execution_reasoning": "",
  "risk_assessment": "無|低|中|高",
  "deviation_flag": "無|輕微|顯著|嚴重",
  "result": "完成|部分完成|擱置",
  "issue_responses": [{{
    "issue_number": 0,
    "comment": "",
    "close": false
  }}],
  "file_operations": [{{
    "path": "notes/path/file.md",
    "description": "用途",
    "mode": "create|append|overwrite"
  }}],
  "human_question": ""
}}
若無待處理 issue 則 issue_responses 為 []。若無筆記則 file_operations 為 []。
"""

    client = _client()
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=build_system_prompt(core),
            max_output_tokens=2048,
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)


def generate_file_content(core: dict, reading_chunk: str, path: str, description: str) -> str:
    """Step 2: generate actual markdown content for a single note file."""
    prompt = f"""筆記路徑：{path}
筆記用途：{description}

相關閱讀內容：
{reading_chunk[:4000]}

請撰寫此筆記的 markdown 內容："""

    client = _client()
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="你是 moticore-agent，正在撰寫動機論研究筆記。直接輸出 markdown 內容，不要加 JSON 包裝。",
            max_output_tokens=4096,
            temperature=0.4,
        ),
    )
    return response.text.strip()
