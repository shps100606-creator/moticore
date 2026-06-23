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

可修改：`agent/memory.py`、`agent/run.py`、`agent/reader.py`（若存在）、`_docs/strategy/ROADMAP.md`
不得修改：`agent/decision.py`（WN2 負責）、`agent/preprocessor.py`（WN3 負責）、主 VP

**等待條件**：WN2 全部完成後再執行（WN4-1 修改 memory.py 和 run.py，與 WN2 同檔案）。
WN4-3（ROADMAP）可在任何時候獨立執行。

程式碼變更須在 feature branch 進行，完成後開 PR merge main。

---

## 任務看板

| 任務ID | 屬性 | 重要性 | 狀態 | 負責代理 | 目標檔案 | 驗證方式 |
|--------|------|--------|------|----------|----------|----------|
| WN4-1 | AX | PR | open | — | `agent/memory.py`, `agent/run.py` | action-log 超 200 筆時自動截斷並封存 |
| WN4-2 | PJ | PR | open | — | `agent/run.py`（或 reader.py） | 外部 URL §READ_REQUEST 可正常讀取 |
| WN4-3 | AX | PR | open | — | `_docs/strategy/ROADMAP.md` | v0.5.0 條目完整、v0.6.0 更新 |

WN4-1 → WN4-2 有 run.py 衝突，建議依序執行。WN4-3 獨立，可任何時候進行。

---

## 任務區

### WN4-1：action-log 截斷機制

- **屬性**：AX
- **重要性**：PR
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  `memory/action-log.md` 目前無限增長。從 2026-06-16 起有 70+ 筆重複條目。
  
  `agent/memory.py` 的 `append_action()` 目前只追加，無截斷邏輯。
  
  現行 action-log 格式：每個條目以 `\n### {timestamp}\n` 開頭，可用 `split("\n### ")` 分割。

- **完成定義**：
  在 `agent/memory.py` 的 `append_action()` 函式末尾（追加後）加入截斷邏輯：
  
  ```python
  def _truncate_action_log_if_needed(log_path: Path, keep: int = 100, archive_threshold: int = 200) -> None:
      """If log exceeds archive_threshold entries, archive oldest (total - keep) to dated file."""
      if not log_path.exists():
          return
      text = log_path.read_text(encoding="utf-8")
      # split on entry boundaries (### timestamp headers)
      raw_blocks = text.strip().split("\n### ")
      # first block may be empty or pre-header text
      blocks = [b for b in raw_blocks if b.strip()]
      if len(blocks) <= archive_threshold:
          return
      
      archive_count = len(blocks) - keep
      to_archive = blocks[:archive_count]
      to_keep = blocks[archive_count:]
      
      # Write archive file
      archive_month = datetime.utcnow().strftime("%Y%m")
      archive_path = log_path.parent / f"action-log-archive-{archive_month}.md"
      archive_header = f"# action-log 封存 {archive_month}\n（共 {archive_count} 筆）\n"
      archive_content = archive_header + "\n### ".join(to_archive)
      # Append to archive (may already exist for this month)
      if archive_path.exists():
          with archive_path.open("a", encoding="utf-8") as f:
              f.write("\n### " + "\n### ".join(to_archive))
      else:
          archive_path.write_text(archive_content, encoding="utf-8")
      
      # Rewrite main log with kept entries
      log_path.write_text("\n### ".join(to_keep), encoding="utf-8")
      print(f"[memory] action-log truncated: archived {archive_count}, kept {keep}")
  ```
  
  在 `append_action()` 的最後一行（`f.write(entry)` 之後）加入呼叫：
  ```python
  _truncate_action_log_if_needed(log_path)
  ```
  
  `run.py` 不需修改（截斷在 memory.py 內部處理）。

- **可修改檔案**：
  - `agent/memory.py`

- **禁止修改**：
  - `agent/run.py`（本任務不需修改）
  - 現有 `memory/action-log.md` 的內容（由代碼自動處理）

- **驗證方式**：
  1. 確認 `_truncate_action_log_if_needed` 函式存在
  2. 單元測試（可在本地或 scratchpad）：建立含 201 筆假條目的 action-log，呼叫函式，確認主 log 剩 100 筆，archive 建立且含 101 筆
  3. 確認 append 後的 action-log 格式仍可被 `get_recent_actions()` 正確解析

- **已知限制**：
  - 同月份多次截斷時，archive 用 append 模式，條目格式略有差異（第一筆無 `### ` 前綴）。可接受，記錄為已知限制。
  - 截斷 threshold 200、keep 100 為 VP 建議值，Worker 可直接使用，無需調整。

- **回報要求**：
  - 貼出 `_truncate_action_log_if_needed` 完整函式
  - 貼出測試結果（201 筆 → 截斷後剩幾筆）

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

### WN4-2：§READ_REQUEST 支援外部 URL（M5）

- **屬性**：PJ
- **重要性**：PR
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  現行 §READ_REQUEST 格式：
  ```json
  {"notes": ["notes/foo.md"], "dialogues": ["12-xxx.md"]}
  ```
  `preprocessor.py` 的 `_load_requested_files()` 只處理 repo 內路徑和 prima-materia dialogues。
  
  `run.py` 的 `handle_read_request()` 只是將 JSON 存入 `memory/read-requests.json`，下次心跳由 preprocessor 讀取。
  
  需新增 `urls` 欄位支援外部 URL 讀取。

- **完成定義**：
  
  **1. decision.py 格式更新（§READ_REQUEST 說明新增 urls 欄位）**
  注意：`agent/decision.py` 由 WN2 負責，本任務在 WN2 完成後才執行。
  需在 REMARKS_INSTRUCTIONS 的 §READ_REQUEST 格式說明中加入：
  ```
  - urls: 讀取外部 URL 內容（只允許 GET，最多 2 個）
  ```
  
  **2. preprocessor.py 的 `_load_requested_files()` 新增 urls 解析**
  注意：`agent/preprocessor.py` 由 WN3 負責。
  需在 `if isinstance(data, dict):` 分支新增：
  ```python
  urls = [u for u in data.get("urls", []) if isinstance(u, str) and u.startswith("https://")]
  return notes, dialogues, urls
  ```
  並更新函式 signature 和所有呼叫點。
  
  **3. preprocessor.py 的 `_layer4_knowledge()` 讀取 URL 內容**
  新增 `_fetch_url()` 輔助函式：
  ```python
  def _fetch_url(url: str, max_chars: int = 3000) -> str:
      try:
          resp = _requests.get(url, timeout=15, headers={"User-Agent": "moticore-agent/1.0"})
          resp.raise_for_status()
          return resp.text[:max_chars]
      except Exception as e:
          return f"（無法讀取 {url}：{e}）"
  ```
  在 `_layer4_knowledge()` 中，處理完 dialogues 後新增 URL 讀取（最多 2 個）。

- **可修改檔案**：
  - `agent/decision.py`（只改 REMARKS_INSTRUCTIONS 的 §READ_REQUEST 說明段落）
  - `agent/preprocessor.py`（`_load_requested_files`, `_fetch_url`, `_layer4_knowledge`）
  
  **注意**：本任務需要修改 decision.py 和 preprocessor.py，這兩個檔案分別由 WN2 和 WN3 負責。執行本任務前，請確認 WN2 和 WN3 的 PR 已合併到 main，再基於最新 main 開新 feature branch。

- **禁止修改**：
  - `agent/run.py`（不需修改，read_request 存檔邏輯不變）
  - `agent/memory.py`

- **驗證方式**：
  1. 確認 `_fetch_url` 函式存在
  2. 測試：構造含 `urls` 欄位的 read-requests.json，執行 `_load_requested_files()`，確認回傳三元組 `(notes, dialogues, urls)`
  3. 確認 `_layer4_knowledge()` 在 notes 區塊中包含 URL 讀取內容
  4. 確認安全限制：非 `https://` 開頭的 URL 被過濾

- **已知限制**：
  - M5 涉及 decision.py 和 preprocessor.py，兩者分別由 WN2/WN3 負責，本任務必須在兩者 merge 後才能執行。若時程緊，可先做 WN4-3，WN4-2 最後做。
  - URL 讀取只支援 GET 純文字，不處理 JavaScript 渲染的頁面。

- **回報要求**：
  - 貼出 `_fetch_url` 完整函式
  - 貼出 `_load_requested_files` 更新後 signature 和 return 語句
  - 說明是否影響 `_layer4_knowledge` 的呼叫點（preprocessor.py 內部）

#### LOCK 紀錄
- **LOCK 時間**：
- **LOCK 代理**：
- **LOCK 範圍**：agent/preprocessor.py（_fetch_url, _load_requested_files, _layer4_knowledge）、agent/decision.py（§READ_REQUEST 說明）

#### Worker 回報
- **完成內容**：
- **修改檔案**：
- **驗證結果**：
- **未完成 / 風險**：
- **建議交給 PM 的事項**：

---

### WN4-3：ROADMAP.md 更新（T10）

- **屬性**：AX
- **重要性**：PR
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  `_docs/strategy/ROADMAP.md` 目前 v0.5.0 條目為：
  ```
  ### v0.5.0 — moti 主動表達
  狀態：💡 構想中
  - M4：§QUESTION 放寬，允許 moti 主動開 Issue 分享洞見
  - M5：§READ_REQUEST 支援外部 URL
  - action-log.md 截斷機制
  ```
  v0.6.0 條目為「多代理擴展（長期）」。

- **完成定義**：
  1. v0.5.0 條目更新：
     - 主題改為「v0.5.0 — 動機論 2.0 太極覺醒」
     - 狀態改為「🚧 進行中」
     - 內容列出：T1-T6 核心功能（太極雙極架構、HORIZON.md、pole 欄位、極性平衡偵測、M4 §INSIGHT）+ T7/T8/T9 技術債
  2. v0.6.0 條目更新：
     - 主題改為「v0.6.0 — 太極自動化（結晶 / 溶解機制）」
     - 說明：自動偵測 crystallize / dissolve 時機；HORIZON.md 定期自動整理；多極震盪長期數據觀測
  3. 版本歷程表新增 v0.5.0 行（日期 2026-06-23，摘要「動機論 2.0：太極雙極架構、HORIZON.md、pole 欄位、極性平衡偵測、M4 §INSIGHT」）

- **可修改檔案**：
  - `_docs/strategy/ROADMAP.md`

- **禁止修改**：
  - 版本歷程中已有的條目（v0.1.0〜v0.4.0）
  - 任何 agent/ 或 core/ 檔案

- **驗證方式**：
  1. 確認 v0.5.0 主題已改
  2. 確認 v0.6.0 條目已更新
  3. 確認版本歷程表含 v0.5.0 行

- **已知限制**：
  v0.5.0 尚在進行中，封版日期暫填 2026-06-23（規劃開始日），實際完成時 Release session 再更新。

- **回報要求**：
  - 貼出更新後的 v0.5.0 和 v0.6.0 完整條目

#### LOCK 紀錄
- **LOCK 時間**：
- **LOCK 代理**：
- **LOCK 範圍**：_docs/strategy/ROADMAP.md

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

## PM 吸収檢查

| 項目 | 狀態 | VP 回寫位置 / 処理方式 |
|------|------|------------------------|
| Worker 完成內容已回寫 VP | ⬜ | |
| 驗証結果已回寫 VP | ⬜ | |
| blocked / review 項目已処理 | ⬜ / N/A | |
| 技術債已回寫 VP | ⬜ / N/A | |
| WN 封版処理決定已填寫 | ⬜ | |
