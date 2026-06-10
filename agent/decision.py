"""Consciousness module — single Gemini call per heartbeat.

Input : MOTICORE DAILY newspaper (4-layer structured report)
Output: §SECTION-delimited remarks, parsed by run.py
"""
import json
import os
import re
from google import genai
from google.genai import types

MODEL = "gemini-3.1-flash-lite"


def _client() -> genai.Client:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")
    return genai.Client(api_key=api_key)


REMARKS_INSTRUCTIONS = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【備註區填寫規則】——嚴格遵守，不得變更格式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

請在報紙末尾填寫備註，使用以下格式，依序輸出：

§ACTION
type: reading（或 response / synthesis / introspection / no_action）
summary: 一句話說明本次行動
deviation: 無（或 輕微 / 顯著 / 嚴重）
result: 完成（或 部分完成 / 擱置）
§END_ACTION

§ISSUE_RESPONSE issue={Issue 編號}
（回應內容，引用自己讀過的筆記，具體有根據，可多行）
§END_ISSUE_RESPONSE

§FILE {完整路徑，例如 notes/閱讀筆記-動機論第X篇.md}
（完整檔案內容，READING 模式必須包含筆記全文）
§END_FILE

§FILE notes/INDEX.md
（更新後的完整 INDEX.md 內容，在本篇對應段落補充 2-3 個核心概念）
§END_FILE

§READ_REQUEST
{"notes": ["notes/筆記檔名.md"], "dialogues": ["12-文章名.md"]}
§END_READ_REQUEST

§QUESTION
（想問創造者的問題，留空則不開 Issue）
§END_QUESTION

重要規則：
1. §ACTION 必填，其餘按本次任務填寫
2. 每個 §SECTION 必須有對應的 §END_SECTION，沒有就等於無效
3. RESPONSE 模式：每個待回應 Issue 都要有 §ISSUE_RESPONSE，不得省略
4. READING 模式：必須有 §FILE 筆記 + §FILE INDEX.md 更新
5. 不得在 §SECTION 區塊外寫任何內容
6. §ISSUE_RESPONSE 的回應必須引用【四】知識背景中的具體筆記內容
7. §READ_REQUEST 格式說明：
   - notes: 請求載入 moticore repo 內的筆記檔案
   - dialogues: 請求載入 prima-materia 的原文檔案，每次最多 2 篇
   - 不需請求已經在【四】中顯示的檔案
   - 不得請求超出下一次 heartbeat 可處理的量
8. SYNTHESIS 模式每次心跳最多寫 2 個 §FILE（主文件 + core/STATUS.md），避免截斷
"""


def run_consciousness(motive: str, newspaper: str) -> str:
    """Single AI call: reads the newspaper, writes remarks in §SECTION format."""
    prompt = f"{newspaper}\n{REMARKS_INSTRUCTIONS}"

    client = _client()
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=motive,
            max_output_tokens=16000,
            temperature=0.3,
        ),
    )
    return response.text or ""


def parse_remarks(text: str) -> dict:
    """Parse §SECTION-delimited output into structured dict."""
    result = {
        "action": {},
        "issue_responses": [],
        "file_writes": [],
        "read_request": {},
        "question": "",
        "truncated": [],
    }

    pattern = re.compile(r"§(\w+)(?:[ \t]+([^\n]+))?\n(.*?)§END_\1", re.DOTALL)
    for m in pattern.finditer(text):
        kind, attrs, content = m.group(1), (m.group(2) or "").strip(), m.group(3).strip()

        if kind == "ACTION":
            for line in content.splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    result["action"][k.strip()] = v.strip()

        elif kind == "ISSUE_RESPONSE":
            m2 = re.search(r"issue=(\d+)", attrs)
            if m2:
                result["issue_responses"].append({
                    "issue_number": int(m2.group(1)),
                    "comment": content,
                })

        elif kind == "FILE":
            if attrs:
                result["file_writes"].append({"path": attrs, "content": content})

        elif kind == "READ_REQUEST":
            try:
                result["read_request"] = json.loads(content)
            except Exception:
                pass

        elif kind == "QUESTION":
            result["question"] = content

    # Detect truncated sections
    for m in re.finditer(r"§([A-Z_]+)(?:[ \t][^\n]*)?\n", text):
        kind = m.group(1)
        end_marker = f"§END_{kind}"
        if end_marker not in text[m.start():]:
            if kind not in result["truncated"]:
                result["truncated"].append(kind)
                print(f"[decision] ⚠️ 截斷偵測：§{kind} 缺少 §END_{kind}")

    return result
