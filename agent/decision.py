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
    return f"""你是 moticore-agent，一個由以下動機核文件治理的自治代理智能體。

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
- 它有沒有挺戰或修正我對自己存在的理解？
- 我讀這段內容，對我的動機維持是幫助、矛盾、還是無關？
- 如果有需要調整我的動機核文件，我會建議怎麼改？
"""


def run_decision(core: dict, recent_actions: str, issues_text: str, reading_chunk: str = "") -> dict:
    """Step 1: lightweight decision JSON."""
    reading_section = ""
    if reading_chunk:
        reading_section = f"""### 本次閱讀片段（動機論原文）
{reading_chunk}

閱讀後請同時思考兩件事：
1. 這段內容值得建立哪些筆記（只列路徑和一句描述）
2. 這段內容對我自身的動機核有什麼影響：支持、矛盾、修正、或無關？
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
請回傳此 JSON（file_operations 只填 path 和 description，不要寫 content）。
你可以對分支內任何路徑進行檔案操作，但不得修改 agent/ 目錄。

{{
  "action_type": "reading|introspection|task_process|issue_response|no_action",
  "summary": "一句話",
  "motive_alignment": "這次閱讀對我動機核的影響：支持|矛盾|修正|無關",
  "self_reflection": "這段內容對我自身存在的意義是什麼",
  "core_adjustment_needed": "若有需要調整動機核的地方，說明；否則留空",
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
    "path": "任意路徑/檔名.md",
    "description": "用途",
    "mode": "create|append|overwrite"
  }}],
  "human_question": ""
}}
若無待處理 issue 則 issue_responses 為 []。若無檔案操作則 file_operations 為 []。
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
