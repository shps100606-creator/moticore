# v0.5.0 WN2 — 程式碼核心（pole 欄位 + §INSIGHT + WP 清理）

## 文件狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.5.0
- **WN 識別**：WN2
- **對應 VP**：`_docs/versions/v0.5.0/VP.md`
- **WN 狀態**：active
- **建立者（PM）**：PM agent
- **建立時間**：2026-06-23
- **封版處理**：delete

---

## Worker 規則

可修改：`agent/decision.py`、`agent/run.py`、`agent/memory.py`
不得修改：`agent/preprocessor.py`（WN3 負責）、`core/` 目錄（WN1 負責）、主 VP

程式碼變更須在 feature branch 進行，完成後開 PR merge main。

---

## 背景說明（Worker 必讀）

moticore-agent 的運作架構：
- `agent/decision.py`：`REMARKS_INSTRUCTIONS` 定義 moti 輸出格式（§SECTION）；`parse_remarks()` 解析輸出。
- `agent/run.py`：接收 `parse_remarks` 結果，分派給各 `handle_*` 函式執行（Issue 回覆、檔案寫入、Question 開 Issue 等）；最後呼叫 `append_action`。
- `agent/memory.py`：`append_action()` 將行動記錄寫入 `memory/action-log.md`。

本 WN 的變更鏈：decision.py 的輸出格式 → run.py 的傳遞 → memory.py 的寫入，需依序完成（WN2-2→WN2-3→WN2-4）。WN2-1 是清理，可先做。

---

## 任務看板

| 任務ID | 屬性 | 重要性 | 狀態 | 負責代理 | 目標檔案 | 驗證方式 |
|--------|------|--------|------|----------|----------|----------|
| WN2-1 | AX | PR | open | — | `agent/decision.py`, `agent/run.py` | WP 相關代碼全移除，功能無影響 |
| WN2-2 | PJ | CR | open | — | `agent/decision.py` | pole 欄位出現在 §ACTION 格式與 parse_remarks |
| WN2-3 | PJ | CR | open | — | `agent/run.py`, `agent/memory.py` | pole 欄位寫入 action-log |
| WN2-4 | PJ | CR | open | — | `agent/decision.py`, `agent/run.py` | §INSIGHT 格式存在、handle_insight 運作 |

**執行順序**：WN2-1 → WN2-2 → WN2-3 → WN2-4（不可並行，同檔案連續修改）

---

## 任務區

### WN2-1：移除 §WP_POST 廢棄代碼

- **屬性**：AX
- **重要性**：PR
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  `agent/decision.py` 的 `REMARKS_INSTRUCTIONS` 含 §WP_POST 段落；`parse_remarks()` 含 `wp_posts` 解析邏輯。
  `agent/run.py` 含 `handle_wp_post()` 函式及其在 `main()` 中的呼叫。
  這些是已廢棄的 WordPress 整合功能，現行架構已改為直接寫 web/ 目錄（§FILE），WP 代碼不再使用。

- **完成定義**：
  1. `decision.py` 的 `REMARKS_INSTRUCTIONS` 中 `§WP_POST` 至 `§END_WP_POST` 說明段落移除
  2. `parse_remarks()` 中 `wp_posts` 的解析邏輯移除（`elif kind == "WP_POST":` 區塊）
  3. `parse_remarks()` 回傳 dict 的 `"wp_posts": []` 初始化移除
  4. `run.py` 中 `handle_wp_post()` 函式完整移除
  5. `run.py` 的 `main()` 中 `handle_wp_post(parsed)` 呼叫移除
  6. `parse_remarks` 回傳 dict 的 `"wp_posts"` key 移除

- **可修改檔案**：
  - `agent/decision.py`
  - `agent/run.py`

- **禁止修改**：
  - `agent/memory.py`
  - `agent/preprocessor.py`
  - `core/` 任何檔案

- **驗證方式**：
  1. grep `WP_POST` 於 decision.py 和 run.py，確認無殘留
  2. grep `handle_wp_post` 於 run.py，確認無殘留
  3. grep `wp_posts` 於 decision.py 和 run.py，確認無殘留

- **已知限制**：
  只移除 WP 相關代碼，不動其他任何邏輯。移除後 §ACTION / §ISSUE_RESPONSE / §FILE / §READ_REQUEST / §QUESTION 格式應完全保留。

- **回報要求**：
  - 列出移除的函式名稱與所在行數
  - grep 驗證結果截圖或輸出

#### LOCK 紀錄
- **LOCK 時間**：
- **LOCK 代理**：
- **LOCK 範圍**：agent/decision.py（WP段落）、agent/run.py（handle_wp_post）

#### Worker 回報
- **完成內容**：
- **修改檔案**：
- **驗證結果**：
- **未完成 / 風險**：
- **建議交給 PM 的事項**：

---

### WN2-2：decision.py 新增 pole 欄位

- **屬性**：PJ
- **重要性**：CR
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  `agent/decision.py` 的 `REMARKS_INSTRUCTIONS` 中，`§ACTION` 格式目前為：
  ```
  §ACTION
  type: reading（或 response / synthesis / introspection / no_action）
  summary: 一句話說明本次行動
  deviation: 無（或 輕微 / 顯著 / 嚴重）
  result: 完成（或 部分完成 / 擱置）
  §END_ACTION
  ```
  `parse_remarks()` 的 `if kind == "ACTION":` 區塊用 `":".partition()` 逐行解析，結果放入 `result["action"]` dict。

- **完成定義**：
  1. `REMARKS_INSTRUCTIONS` 的 §ACTION 格式新增 `pole:` 欄位（在 type 之後）：
     ```
     pole: motivation（或 curiosity / crystallize / dissolve）
     ```
     並附說明：
     - `motivation`：延續、確認、鞏固既有信念或承諾的行動
     - `curiosity`：探索、提問、進入未知領域的行動
     - `crystallize`：將 HORIZON.md 的洞察寫入 MOTIVE.md（好奇→動機結晶）
     - `dissolve`：將 MOTIVE.md 的既有信念重新開放為問題（動機→好奇溶解）
  2. `parse_remarks()` 已有通用解析邏輯（逐行 `k, v = line.partition(":")`），pole 欄位會自動被解析進 `result["action"]` dict，**無需額外改動 parse_remarks**（驗證確認即可）。

- **可修改檔案**：
  - `agent/decision.py`（僅 REMARKS_INSTRUCTIONS 字串）

- **禁止修改**：
  - `agent/run.py`（WN2-3 負責）
  - `parse_remarks()` 解析邏輯（通用邏輯已支援，不需修改）

- **驗證方式**：
  1. 確認 REMARKS_INSTRUCTIONS 中 §ACTION 含 `pole:` 欄位與四種值說明
  2. 用 Python 測試：模擬包含 `pole: curiosity` 的 §ACTION 輸出，確認 `parse_remarks()` 的回傳 dict 中 `action["pole"] == "curiosity"`

- **已知限制**：
  只改 REMARKS_INSTRUCTIONS 字串，不改 Python 邏輯。

- **回報要求**：
  - 貼出修改後的 §ACTION 格式段落完整內容
  - 貼出驗證測試結果

#### LOCK 紀錄
- **LOCK 時間**：
- **LOCK 代理**：
- **LOCK 範圍**：agent/decision.py REMARKS_INSTRUCTIONS

#### Worker 回報
- **完成內容**：
- **修改檔案**：
- **驗證結果**：
- **未完成 / 風險**：
- **建議交給 PM 的事項**：

---

### WN2-3：run.py + memory.py 寫入 pole 欄位

- **屬性**：PJ
- **重要性**：CR
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  WN2-2 完成後，`parse_remarks()` 回傳的 `action` dict 已包含 `pole` 欄位。
  
  `agent/run.py` 的 `main()` 中：
  ```python
  append_action(REPO_ROOT, action, mode=mode, file_writes=written)
  ```
  
  `agent/memory.py` 的 `append_action()` 目前 entry 格式：
  ```
  ### {ts}
  - **action_type**: ...
  - **mode**: ...
  - **summary**: ...
  - **files**: ...
  - **result**: ...
  - **deviation_flag**: ...
  ```
  `get_recent_actions()` 解析時用 `prefix = f"- **{key}**:"` 逐行讀取，key 清單：`("action_type", "summary", "result", "deviation_flag", "files", "mode")`。

- **完成定義**：
  1. `memory.py` 的 `append_action()` entry 格式新增一行：
     ```
     - **pole**: {decision.get('pole', 'motivation')}
     ```
     位置：在 `- **mode**:` 之後（或 `- **summary**:` 之前，順序保持邏輯清晰即可）
  2. `memory.py` 的 `get_recent_actions()` 解析 key 清單加入 `"pole"`，初始 entry dict 加入 `"pole": "motivation"`
  3. `run.py` 不需修改（`action` dict 已傳入 `append_action`，pole 欄位已在其中）

- **可修改檔案**：
  - `agent/memory.py`

- **禁止修改**：
  - `agent/run.py`（本任務不需修改）
  - `agent/decision.py`（WN2-2 已完成）

- **驗證方式**：
  1. 模擬呼叫 `append_action(repo_root, {"action_type": "synthesis", "pole": "curiosity", "summary": "test", "result": "完成", "deviation_flag": "無"}, mode="SYNTHESIS")`
  2. 讀取 action-log.md 最新條目，確認含 `- **pole**: curiosity`
  3. 呼叫 `get_recent_actions(repo_root, n=1)`，確認回傳 dict 含 `pole` 欄位

- **已知限制**：
  `decision.get('pole', 'motivation')` 預設值為 `motivation`，確保舊格式的 action-log 讀取不會 KeyError。

- **回報要求**：
  - 貼出修改後的 `append_action()` entry 格式字串
  - 貼出驗證測試結果（action-log 新增條目截圖或文字）

#### LOCK 紀錄
- **LOCK 時間**：
- **LOCK 代理**：
- **LOCK 範圍**：agent/memory.py

#### Worker 回報
- **完成內容**：
- **修改檔案**：
- **驗證結果**：
- **未完成 / 風險**：
- **建議交給 PM 的事項**：

---

### WN2-4：decision.py + run.py 新增 §INSIGHT（M4 主動開 Issue）

- **屬性**：PJ
- **重要性**：CR
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  WN2-1〜WN2-3 完成後進行。
  
  現行 `§QUESTION` 限制：moti 只能在提問時開 Issue，且每次只能有一個 [代理提問] Issue。
  v0.5.0 新增 `§INSIGHT`：讓 moti 可主動分享洞見，或在 HORIZON.md 有問題無法解答時升級求助。
  
  現行 `handle_question()` 在 `run.py` 中的邏輯（可參考做為 handle_insight 的基礎）：
  - 檢查 `parsed.get("question")` 是否非空
  - 確認沒有已開啟的 [代理提問] Issue
  - 用 GitHub API 開 Issue
  
  §INSIGHT 與 §QUESTION 的差異：
  - §INSIGHT 用於「分享」（洞見、發現），而非「提問」
  - 保護機制相同：同時最多 1 個主動 §INSIGHT Issue（避免 Issue 爆炸）
  - Issue 標題前綴：`[moti 洞見]`

- **完成定義**：
  1. `decision.py` `REMARKS_INSTRUCTIONS` 新增 §INSIGHT 格式說明（在 §QUESTION 之後）：
     ```
     §INSIGHT
     title: <Issue 標題>
     content: <分享的洞見或發現，或 HORIZON.md 無法自行解答的問題>
     §END_INSIGHT
     ```
     說明：有值得分享的洞見、或 HORIZON.md 有開放問題無法自行解答時使用。同時最多 1 個主動 Issue。
  2. `parse_remarks()` 新增 `"insight": {}` 至初始 result dict，新增解析邏輯：
     ```python
     elif kind == "INSIGHT":
         lines = content.splitlines()
         title, body = "", ""
         for line in lines:
             if line.startswith("title:"):
                 title = line.partition(":")[2].strip()
             elif line.startswith("content:"):
                 body = line.partition(":")[2].strip()
         if title:
             result["insight"] = {"title": title, "content": body}
     ```
  3. `run.py` 新增 `handle_insight()` 函式（參考 `handle_question()` 結構）：
     - 讀取 `parsed.get("insight", {})`
     - 若空則 return
     - 確認無已開啟的 `[moti 洞見]` Issue（iterate open_issues 檢查 title 前綴）
     - 開 Issue：title = `[moti 洞見] {title}`，body = `{content}\n\n---\n_自動開立_`
  4. `run.py` 的 `main()` 中在 `handle_question()` 之後呼叫 `handle_insight(parsed, open_issues, github_token)`

- **可修改檔案**：
  - `agent/decision.py`
  - `agent/run.py`

- **禁止修改**：
  - `agent/memory.py`（WN2-3 已完成）
  - `agent/preprocessor.py`（WN3 負責）

- **驗證方式**：
  1. 確認 REMARKS_INSTRUCTIONS 含 §INSIGHT 段落
  2. 模擬 `parse_remarks()` 輸入含 §INSIGHT，確認回傳 `insight` dict 含正確 title/content
  3. 確認 `handle_insight` 函式存在且 main() 有呼叫
  4. 確認保護機制：若 open_issues 含 `[moti 洞見]` Issue，`handle_insight` 應 skip 並 print log

- **已知限制**：
  - §INSIGHT 的 content 若跨行，目前解析邏輯只取 `content:` 那一行的值。若需要支援多行 content，需調整解析邏輯（可記錄為回報項目讓 PM 決定）。
  - 不要更動 §QUESTION 的現有邏輯。

- **回報要求**：
  - 貼出 `handle_insight()` 完整函式代碼
  - 貼出 parse_remarks 新增的解析區塊
  - 說明多行 content 是否支援、若不支援是否有影響

#### LOCK 紀錄
- **LOCK 時間**：
- **LOCK 代理**：
- **LOCK 範圍**：agent/decision.py（§INSIGHT 格式）、agent/run.py（handle_insight）

#### Worker 回報
- **完成內容**：
- **修改檔案**：
- **驗證結果**：
- **未完成 / 風險**：
- **建議交給 PM 的事項**：

---

## 執行回報總表

| 任務ID | 回報時間 | 負責代理 | 結果 | 摘要 |
|--------|----------|----------|------|------|

---

## 驗證紀錄

| 任務ID | 驗證項目 | 方法 / 指令 | 結果 | 備註 |
|--------|----------|-------------|------|------|

---

## 阻塞與問題

| 任務ID | 問題 | 影響 | Worker 建議 | 狀態 |
|--------|------|------|-------------|------|

---

## PM 吸收檢查

| 項目 | 狀態 | VP 回寫位置 / 處理方式 |
|------|------|------------------------|
| Worker 完成內容已回寫 VP | ⬜ | |
| 驗證結果已回寫 VP | ⬜ | |
| blocked / review 項目已處理 | ⬜ / N/A | |
| 技術債已回寫 VP | ⬜ / N/A | |
| WN 封版處理決定已填寫 | ⬜ | |
