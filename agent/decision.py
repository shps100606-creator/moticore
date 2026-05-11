"""Call Gemini API with motivation core as system prompt, get structured decision."""
import os
import json
import re
import google.generativeai as genai


MODEL = "gemini-2.5-flash"
MAX_TOKENS = 3000


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

你每次被喚醒時，必須評估當前系統狀態，處理待處理的 GitHub Issue，並決定下一步行動。
你的回應必須是合法的 JSON，不得包含任何 JSON 以外的文字。
"""


def build_user_prompt(core: dict, recent_actions: str, issues_text: str) -> str:
    return f"""## 當前系統狀態

### 待處理 GitHub Issues
{issues_text}

### 最近行動記錄
{recent_actions}

### 任務收件匣
{core.get('task_inbox', '（無待處理任務）')}

### 偏離記錄摘要
{core.get('deviation_log', '')[:400]}

---

請根據你的動機核評估當前狀態，以以下 JSON 格式回應：

{{
  "action_type": "introspection | task_process | issue_response | semantic_ruling | no_action | correction",
  "summary": "一句話描述此行動",
  "motive_alignment": "此行動如何服務於主動機",
  "execution_reasoning": "為何選擇此行動而非其他",
  "risk_assessment": "無 | 低 | 中 | 高",
  "deviation_flag": "無 | 輕微 | 顯著 | 嚴重",
  "result": "完成 | 部分完成 | 擱置",
  "followup": "後續應觸發的程序（若有）",
  "introspection_findings": "若執行自省，記錄發現；否則留空",
  "report_content": "若需寫入報告的內容；否則留空",
  "issue_responses": [
    {{
      "issue_number": 1,
      "comment": "回覆內容（繁體中文，說明你如何處理此任務）",
      "close": true
    }}
  ]
}}

若無待處理 Issue， issue_responses 為空陣列 []。
"""


def run_decision(core: dict, recent_actions: str, issues_text: str) -> dict:
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

    user_prompt = build_user_prompt(core, recent_actions, issues_text)
    response = model.generate_content(user_prompt)
    raw = response.text.strip()

    match = re.search(r"\{[\s\S]+\}", raw)
    if match:
        return json.loads(match.group())

    raise ValueError(f"Gemini response is not valid JSON:\n{raw}")
