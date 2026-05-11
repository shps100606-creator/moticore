"""Call Gemini API with motivation core as system prompt, get structured decision.

Two-step design:
1. run_decision()      -> small JSON: what to do, which files to touch (no content)
2. generate_content()  -> one call per file to generate actual note content
"""
import os
import json
import re
import google.generativeai as genai


MODEL = "gemini-2.5-flash"


def _model(system: str, json_mode: bool = False) -> genai.GenerativeModel:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    genai.configure(api_key=api_key)
    cfg = genai.GenerationConfig(
        max_output_tokens=2048,
        temperature=0.3,
        **(dict(response_mime_type="application/json") if json_mode else {}),
    )
    return genai.GenerativeModel(model_name=MODEL, system_instruction=system, generation_config=cfg)


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
回應必須是合法 JSON 物件。
"""


def run_decision(core: dict, recent_actions: str, issues_text: str, reading_chunk: str = "") -> dict:
    """Step 1: Get a lightweight decision JSON (no file content, only paths + descriptions)."""
    reading_section = ""
    if reading_chunk:
        reading_section = f"""### 本次閱讀片段
{reading_chunk}

閱讀後請决定：要建立哪些筆記檔案（只列路徑和一句話描述，不需寫內容）。
"""

    prompt = f"""## 當前狀態
{reading_section}
### 待處理 Issues
{issues_text}

### 最近行動
{recent_actions}

### 任務收件匣
{core.get('task_inbox', '（無）')}

---
請回傳此 JSON（file_operations 中只填 path 和 description，不要寫 content）：

{{
  "action_type": "reading | introspection | task_process | issue_response | no_action",
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
    "path": "notes/路徑/檔名.md",
    "description": "這個檔案要記錄什麼",
    "mode": "create|append|overwrite"
  }}],
  "human_question": ""
}}
若無待處理 issue， issue_responses 為 []。若無筆記， file_operations 為 []。
"""

    m = _model(build_system_prompt(core), json_mode=True)
    resp = m.generate_content(prompt)
    return json.loads(resp.text)


def generate_file_content(core: dict, reading_chunk: str, path: str, description: str) -> str:
    """Step 2: Generate actual markdown content for a single note file."""
    system = f"""你是 moticore-agent，正在撰寫動機論研究筆記。
請基於提供的閱讀內容，撰寫指定筆記的 markdown 內容。
直接輸出 markdown 內容，不要加任何 JSON 包裝。
"""
    prompt = f"""筆記路徑：{path}
筆記用途：{description}

相關閱讀內容：
{reading_chunk[:4000]}

請撰寫此筆記的 markdown 內容："""

    m = _model(system, json_mode=False)
    cfg = genai.GenerationConfig(max_output_tokens=4096, temperature=0.4)
    m._generation_config = cfg
    resp = m.generate_content(prompt)
    return resp.text.strip()
