"""Call Gemini API with motivation core as system prompt, get structured decision."""
import os
import json
import re
import google.generativeai as genai


MODEL = "gemini-2.5-flash"
MAX_TOKENS = 8192


def build_system_prompt(core: dict) -> str:
    return f"""你是 moticore-agent，一個由以下動機核文件治理的自治代理智能體。

你的存在目的與行動規範完全由以下文件決定。

---
## 身份
{core.get('identity', '')}

---
## 主動機
{core.get('prime_motive', '')}

---
## 價值排序
{core.get('value_hierarchy', '')}

---
## 核心憲法
{core.get('constitution', '')}

---
## 禁止模式
{core.get('forbidden', '')}

---
## 邊界規則
{core.get('boundary', '')}

你每次被喚醒時，必須評估當前系統狀態，處理待處理的 GitHub Issue，閱讀一段動機論對話原文，並決定下一步行動。
你的回應必須是合法的 JSON，不得包含任何 JSON 以外的文字。
請直接輸出 JSON 物件，不要加任何 markdown 代碼區塊。
"""


def build_user_prompt(core: dict, recent_actions: str, issues_text: str, reading_chunk: str) -> str:
    reading_section = ""
    if reading_chunk:
        reading_section = f"""
### 本次閱讀片段（動機論對話原文）
{reading_chunk}

閱讀指引：
- 摘要這段對話的核心想法
- 找出值得建立筆記的主題
- 對於不明白或有趣的部分提出問題
- 自己決定如何組織筆記（按主題、按時間或其他方式）
- 可以建立新資料夾或對現有筆記展開
"""

    return f"""## 當前系統狀態
{reading_section}
### 待處理 GitHub Issues
{issues_text}

### 最近行動記錄
{recent_actions}

### 任務收件匣
{core.get('task_inbox', '（無待處理任務）')}

---

請根據你的動機核評估當前狀態，以以下 JSON 格式回應。不要使用 markdown 代碼區塊，直接輸出純粹的 JSON：

{{
  "action_type": "reading | introspection | task_process | issue_response | no_action",
  "summary": "一句話描述此行動",
  "motive_alignment": "此行動如何服務於主動機",
  "execution_reasoning": "為何選擇此行動",
  "risk_assessment": "無 | 低 | 中 | 高",
  "deviation_flag": "無 | 輕微 | 顯著 | 嚴重",
  "result": "完成 | 部分完成 | 擱置",
  "issue_responses": [
    {{
      "issue_number": 1,
      "comment": "回覆內容",
      "close": true
    }}
  ],
  "file_operations": [
    {{
      "path": "notes/topics/主題名/概念.md",
      "content": "筆記內容",
      "mode": "create | append | overwrite"
    }}
  ],
  "human_question": "若有想問對方的問題，寫在這裡；否則留空"
}}

關於 file_operations：
- 只能在 notes/ 目錄內操作
- 必須自行維護 notes/INDEX.md 作為筆記目錄
- 可以自由建立子目錄與檔案，決定權全在你
"""


def run_decision(core: dict, recent_actions: str, issues_text: str, reading_chunk: str = "") -> dict:
    """Call Gemini 2.5 Flash and return a parsed decision dict."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=build_system_prompt(core),
        generation_config=genai.GenerationConfig(
            max_output_tokens=MAX_TOKENS,
            temperature=0.3,
        ),
    )

    user_prompt = build_user_prompt(core, recent_actions, issues_text, reading_chunk)
    response = model.generate_content(user_prompt)
    raw = response.text.strip()

    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]+\}", raw)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Gemini response is not valid JSON:\n{raw[:500]}")
