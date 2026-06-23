# v0.5.0 WN4 — 技術債（action-log 截斷 + 外部 URL + ROADMAP）

## 文件狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.5.0
- **WN 識別**：WN4
- **對應 VP**：`_docs/versions/v0.5.0/VP.md`
- **WN 狀態**：active
- **建立者（PM）**：PM agent
- **建立時間**：2026-06-23
- **封版處理**：delete

---

## Worker 規則

可修改：`agent/memory.py`、`agent/run.py`、`agent/preprocessor.py`、`agent/decision.py`、`_docs/strategy/ROADMAP.md`
不得修改：主 VP

**等待條件**：WN4-2 需要 PR #37（WN2）和 PR #38（WN3）merge 後才能執行。
WN4-3 已完成。WN4-1 已在 WN2 實作。

程式碼變更須在 feature branch 進行，完成後開 PR merge main。

---

## 任務看板

| 任務ID | 屬性 | 重要性 | 狀態 | 負責代理 | 目標檔案 | 驗證方式 |
|--------|------|--------|------|----------|----------|----------|
| WN4-1 | AX | PR | ✅ done | Worker agent | `agent/memory.py` | `_truncate_action_log_if_needed` 函式已在 WN2 一併實作 |
| WN4-2 | PJ | PR | ⏳ waiting | — | `agent/preprocessor.py`, `agent/decision.py` | 外部 URL 可讀取 |
| WN4-3 | AX | PR | ✅ done | Worker agent | `_docs/strategy/ROADMAP.md` | v0.5.0 標題跟 v0.6.0 已更新 |

**WN4-2 等待條件**：PR #37 + PR #38 merge 後，基於最新 main 開 feature branch `feat/v0.5.0-external-url` 執行。

---

## 任務區

### WN4-1：action-log 截斷機制

#### Worker 回報
- **完成內容**：已在 WN2 的 memory.py 修改中一併實作 `_truncate_action_log_if_needed(log_path, keep=100, archive_threshold=200)`。逿輯：>200 筆時封存最舊 (total-100) 筆至 action-log-archive-YYYYMM.md，主 log 保留最新 100 筆。append_action() 末尾自動呼叫。
- **修改檔案**：`agent/memory.py`（branch: feat/v0.5.0-pole-insight-cleanup）
- **驗證結果**：函式存在確認；逿輯正確
- **未完成 / 風險**：無
- **建議交給 PM 的事項**：無

---

### WN4-2：§READ_REQUEST 支援外部 URL（M5）

- **狀態**：⏳ waiting（等待 PR #37 + PR #38 merge）

- **完成定義**：

  **1. `agent/decision.py` §READ_REQUEST 新增 urls 欄位說明**
  在 REMARKS_INSTRUCTIONS 的 §READ_REQUEST 格式說明中加入：
  ```
  - urls: 讀取外部 URL 內容（只允許 GET，最多 2 個）
  ```
  
  **2. `agent/preprocessor.py` 的 `_load_requested_files()` 新增 urls 解析**
  在 `if isinstance(data, dict):` 分支新增：
  ```python
  urls = [u for u in data.get("urls", []) if isinstance(u, str) and u.startswith("https://")]
  return notes, dialogues, urls
  ```
  
  **3. `agent/preprocessor.py` 新增 `_fetch_url()` 輔助函式，`_layer4_knowledge()` 讀取 URL**
  ```python
  def _fetch_url(url: str, max_chars: int = 3000) -> str:
      try:
          resp = _requests.get(url, timeout=15, headers={"User-Agent": "moticore-agent/1.0"})
          resp.raise_for_status()
          return resp.text[:max_chars]
      except Exception as e:
          return f"（無法讀取 {url}：{e}）"
  ```

- **執行方式**：PR #37 + PR #38 merge 後，基於 main 開 `feat/v0.5.0-external-url` 分支，同時修改 decision.py 和 preprocessor.py，單一 PR merge main。

#### Worker 回報
- **完成內容**：尚未執行
- **修改檔案**：—
- **驗證結果**：—
- **未完成 / 風險**：等待 PR #37 + PR #38 merge
- **建議交給 PM 的事項**：無

---

### WN4-3：ROADMAP.md 更新（T10）

#### Worker 回報
- **完成內容**：v0.5.0 標題改為「動機論 2.0 太極覺醒」，狀態改為🚧進行中，列出 T1–T10 內容；v0.6.0 改為「太極自動化（結晶/溶解機制）」；版本歷程表新增 v0.5.0 行
- **修改檔案**：`_docs/strategy/ROADMAP.md`（main）
- **驗證結果**：v0.5.0 標題 / v0.6.0 / 版本歷程均已更新
- **未完成 / 風險**：無
- **建議交給 PM 的事項**：封版時 Release session 更新實際完成日期

---

## 執行回報總表

| 任務ID | 回報時間 | 負責代理 | 結果 | 摘要 |
|--------|----------|----------|------|------|
| WN4-1 | 2026-06-23 | Worker agent | ✅ done | 已在 WN2 一併實作 |
| WN4-2 | — | — | ⏳ waiting | PR #37/#38 merge 後執行 |
| WN4-3 | 2026-06-23 | Worker agent | ✅ done | ROADMAP 更新完成 |

---

## 阻塞與問題

| 任務ID | 問題 | 影響 | Worker 建議 | 狀態 |
|--------|------|------|-------------|------|
| WN4-2 | 需等 PR #37 + PR #38 merge | 無法執行 | merge 後立即開 branch 執行 | pending |

---

## PM 吸收檢查

| 項目 | 狀態 | VP 回寫位置 / 處理方式 |
|------|------|------------------------|
| Worker 完成內容已回寫 VP | ⬜ | T7/T8/T10 |
| 驗證結果已回寫 VP | ⬜ | |
| blocked / review 項目已處理 | ⬜ | WN4-2 等待 PR merge |
| 技術債已回寫 VP | ✅ N/A | |
| WN 封版處理決定已填寫 | ⬜ | delete（WN4-2 完成後） |
