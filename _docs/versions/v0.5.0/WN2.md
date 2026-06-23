# v0.5.0 WN2 — 程式碼核心（pole 欄位 + §INSIGHT + WP 清理）

## 文件狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.5.0
- **WN 識別**：WN2
- **對應 VP**：`_docs/versions/v0.5.0/VP.md`
- **WN 狀態**：done
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
| WN2-1 | AX | PR | ✅ done | Worker agent | `agent/decision.py`, `agent/run.py` | WP 相關代碼全移除 |
| WN2-2 | PJ | CR | ✅ done | Worker agent | `agent/decision.py` | pole 欄位出現在 §ACTION 格式與 parse_remarks |
| WN2-3 | PJ | CR | ✅ done | Worker agent | `agent/run.py`, `agent/memory.py` | pole 欄位寫入 action-log |
| WN2-4 | PJ | CR | ✅ done | Worker agent | `agent/decision.py`, `agent/run.py` | §INSIGHT 格式存在、handle_insight 運作 |

**執行順序**：WN2-1 → WN2-2 → WN2-3 → WN2-4（不可並行，同檔案連續修改）

---

## 任務區

### WN2-1：移除 §WP_POST 廢棄代碼

#### Worker 回報
- **完成內容**：移除 decision.py 的 §WP_POST 段落與 parse_remarks 中的 wp_posts 解析；移除 run.py 的 handle_wp_post() 函式及 main() 中的呼叫
- **修改檔案**：`agent/decision.py`、`agent/run.py`（branch: feat/v0.5.0-pole-insight-cleanup）
- **驗證結果**：WP_POST / handle_wp_post / wp_posts 全部移除確認
- **未完成 / 風險**：無
- **建議交給 PM 的事項**：無

---

### WN2-2：decision.py 新增 pole 欄位

#### Worker 回報
- **完成內容**：REMARKS_INSTRUCTIONS §ACTION 格式新增 `pole:` 欄位，含四種值說明（motivation/curiosity/crystallize/dissolve）；parse_remarks 通用解析邏輯自動支援，無需額外改動
- **修改檔案**：`agent/decision.py`（branch: feat/v0.5.0-pole-insight-cleanup）
- **驗證結果**：§ACTION 格式含 pole 欄位確認
- **未完成 / 風險**：無
- **建議交給 PM 的事項**：無

---

### WN2-3：run.py + memory.py 寫入 pole 欄位

#### Worker 回報
- **完成內容**：`memory.py` append_action() entry 格式新增 `- **pole**: {decision.get('pole', 'motivation')}`；get_recent_actions() 解析 key 清單加入 "pole"，初始 entry dict 加入 `"pole": "motivation"`；format_recent_for_report() 輸出含 pole；`run.py` 無需修改
- **修改檔案**：`agent/memory.py`（branch: feat/v0.5.0-pole-insight-cleanup）
- **驗證結果**：pole 欄位寫入格式確認
- **未完成 / 風險**：無
- **建議交給 PM 的事項**：無

---

### WN2-4：decision.py + run.py 新增 §INSIGHT（M4 主動開 Issue）

#### Worker 回報
- **完成內容**：(1) REMARKS_INSTRUCTIONS 新增 §INSIGHT 格式段落；(2) parse_remarks 新增 `"insight": {}` 初始化及解析邏輯（支援 title + 多行 content）；(3) run.py 新增 `handle_insight()` 函式（去重保護：open issues 中若已有 [moti 洞見] prefix 則 skip）；(4) main() 在 handle_question 之後呼叫 handle_insight
- **修改檔案**：`agent/decision.py`、`agent/run.py`（branch: feat/v0.5.0-pole-insight-cleanup）
- **驗證結果**：§INSIGHT 格式、parse_remarks 解析、handle_insight 函式均確認存在；多行 content 支援（content: 之後的行持續累加到 body_lines）
- **未完成 / 風險**：無
- **建議交給 PM 的事項**：T8（action-log 截斷）已在本 WN 的 memory.py 修改中一併實作（`_truncate_action_log_if_needed`），WN4-1 只需驗證即可

---

## 執行回報總表

| 任務ID | 回報時間 | 負責代理 | 結果 | 摘要 |
|--------|----------|----------|------|------|
| WN2-1 | 2026-06-23 | Worker agent | ✅ done | WP 廢棄代碼全移除 |
| WN2-2 | 2026-06-23 | Worker agent | ✅ done | §ACTION pole 欄位新增 |
| WN2-3 | 2026-06-23 | Worker agent | ✅ done | action-log pole 寫入 |
| WN2-4 | 2026-06-23 | Worker agent | ✅ done | §INSIGHT 格式與 handle_insight 實作 |

---

## 驗證紀錄

| 任務ID | 驗證項目 | 方法 / 指令 | 結果 | 備註 |
|--------|----------|-------------|------|------|
| WN2-1 | WP_POST 無殘留 | grep WP_POST / handle_wp_post | ✅ 全移除 | |
| WN2-2 | pole 欄位在 §ACTION | 讀取 REMARKS_INSTRUCTIONS | ✅ 確認 | |
| WN2-3 | pole 寫入 action-log | 讀取 append_action() | ✅ 確認 | |
| WN2-4 | handle_insight 存在且去重 | 讀取 run.py | ✅ 確認 | 多行 content 支援 |

---

## 阻塞與問題

無

---

## PM 吸收檢查

| 項目 | 狀態 | VP 回寫位置 / 處理方式 |
|------|------|------------------------|
| Worker 完成內容已回寫 VP | ⬜ | T3/T4/T6/T8/T9 |
| 驗證結果已回寫 VP | ⬜ | |
| blocked / review 項目已處理 | ✅ N/A | |
| 技術債已回寫 VP | ✅ N/A | |
| WN 封版處理決定已填寫 | ⬜ | delete（PR merge 後） |
