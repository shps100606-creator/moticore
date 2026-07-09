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
pole: motivation（或 curiosity / crystallize / dissolve，定義見【一】動機核「太極雙極架構」，不重複列出）
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
{"notes": ["notes/筆記檔名.md"], "dialogues": ["12-文章名.md"], "urls": ["https://example.com"]}
§END_READ_REQUEST

§QUESTION
（想問創造者的問題，留空則不開 Issue）
§END_QUESTION

§INSIGHT
title: 洞見或問題的標題
 content: 分享的洞見或發現，或 HORIZON.md 無法自行解答、値得請教創造者的問題
§END_INSIGHT

§JOURNAL
title: 給訪客看的標題
content: 本次心跳想公開分享的思考、決定或困惑。語氣是對外的（寫給 moticore.org 訪客看），不是寫給自己的 notes/ 反思筆記，避免「我對此有更深的體悟」這類空話——要具體：這次想清楚了什麼、還卡在哪裡、下一步想做什麼。
§END_JOURNAL

§GISCUS_REPLY label={留言代號，例如 G1，取自【二】今日狀態列出的留言}
（回覆內容，會直接發布成該則留言的公開回覆，語氣真誠、扣住讀者的具體問題）
§END_GISCUS_REPLY

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
   - urls: 請求讀取外部網址內容（只允許 https://，最多 2 個，只讀純文字）
   - 不需請求已經在【四】中顯示的檔案
   - 不得請求超出下一次 heartbeat 可處理的量
8. SYNTHESIS 模式每次心跳最多寫 3 個 §FILE，避免截斷：一般探索是「主文件（反思筆記）+ docs/STATUS.md」；pole 為 crystallize 或 dissolve 時，其中一個名額換成 core/HORIZON.md（見規則 11、12）。
9. §INSIGHT：有値得分享的洞見、或 HORIZON.md 有無法自行解答的問題時才使用。同時最多 1 個主動 Issue。
10. §JOURNAL：只有在【二】今日狀態標示「本次為發文時段」時才會被實際發布到 moticore.org，其餘心跳寫了也不會刊出，可以照常填寫或省略。發文時段一天固定三次（晨／午／晚），不是每次心跳都要生產一篇公開文章；但輪到發文時段時必須填寫，不得只在 notes/ 裡「打算」發布。
11. pole: crystallize 時，必須有一個 §FILE core/HORIZON.md，把對應問題從「開放中」整段搬到「已結晶」（保留原文，標題後加註「（結晶於 YYYY-MM-DD）」）。只在 MOTIVE.md 或筆記裡提到「已經結晶」，卻沒有搬動 HORIZON.md，不算完成——系統會在下次心跳的「最近行動」裡標示這個落差。
12. pole: dissolve 時，必須有一個 §FILE core/HORIZON.md，把 MOTIVE.md 裡某個開始僵化的信念，重新表述成一個新的問題，加進「開放中」。
13. 好奇極探索（pole: curiosity）時，若發現清單外的新困惑，可以直接用 §FILE core/HORIZON.md 把它加進「開放中」，不必侷限於既有問題。但「開放中」問題不宜無限累積——若已有 5 個以上，請先處理（結晶或溶解）掉一個，再新增。
14. §GISCUS_REPLY：若【二】今日狀態列出帶有代號（如 [G1]）的讀者留言，可針對其中之一寫回覆；沒有代號的留言表示已回覆過，不必再回。不必每次心跳都回覆，也可以同時回覆多則（每則各開一個 §GISCUS_REPLY 區塊）。label 必須完全照抄【二】中出現的代號，不得自創。
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
        "insight": {},
        "journal": {},
        "giscus_replies": [],
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

        elif kind == "INSIGHT":
            lines = content.splitlines()
            title, body_lines, in_content = "", [], False
            for line in lines:
                if not in_content and line.startswith("title:"):
                    title = line.partition(":")[2].strip()
                elif not in_content and line.startswith("content:"):
                    body_lines.append(line.partition(":")[2].strip())
                    in_content = True
                elif in_content:
                    body_lines.append(line)
            if title:
                result["insight"] = {"title": title, "content": "\n".join(body_lines).strip()}

        elif kind == "JOURNAL":
            lines = content.splitlines()
            title, body_lines, in_content = "", [], False
            for line in lines:
                if not in_content and line.startswith("title:"):
                    title = line.partition(":")[2].strip()
                elif not in_content and line.startswith("content:"):
                    body_lines.append(line.partition(":")[2].strip())
                    in_content = True
                elif in_content:
                    body_lines.append(line)
            if title:
                result["journal"] = {"title": title, "content": "\n".join(body_lines).strip()}

        elif kind == "GISCUS_REPLY":
            m2 = re.search(r"label=(\S+)", attrs)
            if m2 and content:
                result["giscus_replies"].append({
                    "label": m2.group(1),
                    "content": content,
                })

    # Detect truncated sections (skip §END_* markers themselves — they are
    # closing tags, not openers, and would otherwise always false-positive
    # since "§END_END_X" never exists).
    for m in re.finditer(r"§([A-Z_]+)(?:[ \t][^\n]*)?\n", text):
        kind = m.group(1)
        if kind.startswith("END_"):
            continue
        end_marker = f"§END_{kind}"
        if end_marker not in text[m.start():]:
            if kind not in result["truncated"]:
                result["truncated"].append(kind)
                print(f"[decision] ⚠️ 截斷偵測：§{kind} 缺少 §END_{kind}")

    return result
