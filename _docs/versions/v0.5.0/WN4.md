# v0.5.0 WN4 — 技術債（action-log 截斷 + 外部 URL + ROADMAP）

## 文件狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.5.0
- **WN 識別**：WN4
- **對應 VP**：`_docs/versions/v0.5.0/VP.md`
- **WN 狀態**：done
- **建立者（PM）**：PM agent
- **建立時間**：2026-06-23
- **封版處理**：delete

---

## 任務看板

| 任務ID | 屬性 | 重要性 | 狀態 | 負責代理 | 目標檔案 | 驗證方式 |
|--------|------|--------|------|----------|----------|----------|
| WN4-1 | AX | PR | ✅ done | Worker agent | `agent/memory.py` | `_truncate_action_log_if_needed` 已在 WN2 一併實作 |
| WN4-2 | PJ | PR | ✅ done | Worker agent | `agent/preprocessor.py`, `agent/decision.py` | PR #39 開立 |
| WN4-3 | AX | PR | ✅ done | Worker agent | `_docs/strategy/ROADMAP.md` | v0.5.0/v0.6.0 已更新 |

---

## Worker 回報

### WN4-1：action-log 截斷機制
- **完成內容**：已在 WN2 的 memory.py 修改中一併實作 `_truncate_action_log_if_needed(log_path, keep=100, archive_threshold=200)`。>200 筆時封存最舊 (total-100) 筆至 action-log-archive-YYYYMM.md，主 log 保留最新 100 筆。append_action() 末尾自動呼叫。
- **修改檔案**：`agent/memory.py`（feat/v0.5.0-pole-insight-cleanup → merged）

### WN4-2：§READ_REQUEST 支援外部 URL
- **完成內容**：
  1. `decision.py` REMARKS_INSTRUCTIONS 新增 urls 欄位說明與示例
  2. `preprocessor.py` 新增 `_fetch_url()` 函式（GET only, https:// 限制, timeout=15s）
  3. `_load_requested_files()` 回傳 3-tuple `(notes, dialogues, urls)`
  4. `_layer4_knowledge()` 處理 `requested_urls[:2]`，附加至知識背景區
- **修改檔案**：`agent/decision.py`、`agent/preprocessor.py`（branch: feat/v0.5.0-external-url）
- **PR**：#39
- **安全設計**：只接受 https://、GET only、最多 2 個、失敗此確降級

### WN4-3：ROADMAP.md 更新
- **完成內容**：v0.5.0 標題改為「動機論 2.0 太極覺醒」，狀態改為🚧進行中，列出 T1–T10；v0.6.0 改為「太極自動化（結晶/溶解機制）」；版本歷程表新增 v0.5.0
- **修改檔案**：`_docs/strategy/ROADMAP.md`（main）

---

## 執行回報總表

| 任務ID | 回報時間 | 負責代理 | 結果 | 摘要 |
|--------|----------|----------|------|------|
| WN4-1 | 2026-06-23 | Worker agent | ✅ done | 已在 WN2 一併實作 |
| WN4-2 | 2026-06-23 | Worker agent | ✅ done | PR #39 開立，安全外部 URL 支援 |
| WN4-3 | 2026-06-23 | Worker agent | ✅ done | ROADMAP 更新完成 |

---

## PM 吸收檢查

| 項目 | 狀態 | VP 回寫位置 / 處理方式 |
|------|------|------------------------|
| Worker 完成內容已回寫 VP | ⬜ | T7/T8/T10 |
| 驗證結果已回寫 VP | ⬜ | |
| blocked / review 項目已處理 | ✅ N/A | PR #39 待 merge |
| 技術債已回寫 VP | ✅ N/A | |
| WN 封版處理決定已填寫 | ⬜ | delete（PR #39 merge 後） |
