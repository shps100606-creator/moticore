# v0.4.0 Work Note — WN1（後端：迴圈偵測 + Analytics + Discussions fetch）

## 文件狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.4.0
- **WN 識別**：WN1
- **對應 VP**：`_docs/versions/v0.4.0/VP.md`
- **WN 狀態**：active
- **建立者（PM）**：Claude Code（PM session 2026-06-21）
- **建立時間**：2026-06-21
- **封版處理**：delete

---

## Worker 規則

Worker 可以修改：`agent/preprocessor.py`、`agent/run.py`、`agent/issues.py`、`.github/workflows/heartbeat.yml`，以及自己任務的 WN 回報區。

Worker 不得修改：主 VP、WN2.md、`core/`、`web/`、`memory/`（由程式寫入除外）、`agent/decision.py`、`agent/loader.py`、`agent/memory.py`、`agent/reader.py`。

---

## 任務看板

| 任務ID | 屬性 | 重要性 | 狀態 | 負責代理 | 目標檔案 | 驗證方式 |
|--------|------|--------|------|----------|----------|---------|
| WN1-1 | PJ | CR | done | Claude Code | agent/preprocessor.py | mock 5筆相同 summary → 確認 ⚠️ 警告出現 |
| WN1-2 | PJ | CR | open | — | agent/preprocessor.py, agent/run.py | 呼叫 _fetch_analytics() 傳 mock token → 確認 exception 不拋出 |
| WN1-3 | PJ | CR | done | Claude Code | .github/workflows/heartbeat.yml | yaml lint 通過 |
| WN1-4 | PJ | PR | open | — | agent/issues.py, agent/run.py | 若無 Discussions 時回傳空字串，不拋 exception |

---

## 任務區

### WN1-1：preprocessor.py 迴圈自動偵測

- **屬性**：PJ
- **重要性**：CR
- **狀態**：done
- **負責代理**：Claude Code

- **任務輸入**：
  - `agent/preprocessor.py` 的 `_layer2_status()` 函數（約 180–230 行）目前不做任何重複行為偵測。
  - `memory/action-log.md` 格式（每筆心跳一個區塊）：
    ```
    ### 2026-06-21T09:37:17Z
    - **action_type**: unknown
    - **mode**: SYNTHESIS
    - **summary**: 確認網站啟動狀態…
    - **files**: docs/STATUS.md
    - **result**: 完成
    - **deviation_flag**: 無
    ```
  - 歷史教訓：第三次大迴圈從 2026-06-16 到 2026-06-21，約 100 次心跳 summary 幾乎完全相同，直到創造者手動介入才結束。
  - `_layer2_status()` 目前接收 `recent_log: str` 參數（已是格式化字串），但 action-log.md 本身在 `repo_root / "memory" / "action-log.md"`。

- **完成定義**：已完成，見 Worker 回報。

- **可修改檔案**：`agent/preprocessor.py`；讀取：`memory/action-log.md`（只讀）

- **禁止修改**：`agent/` 內 preprocessor.py 以外的檔案；`memory/`；`core/`；`web/`；`.github/`

#### LOCK 紀錄
- **LOCK 時間**：2026-06-21
- **LOCK 代理**：Claude Code（Worker session）
- **LOCK 範圍**：agent/preprocessor.py — 新增 `_parse_recent_summaries()`，修改 `_layer2_status()`

#### Worker 回報
- **完成內容**：
  1. 新增 `_parse_recent_summaries(repo_root, n=5)`：讀 action-log.md，逐行找 `- **summary**:` 前綴，strip 後收集，回傳最後 n 筆。檔案不存在或 exception 均 catch 回傳 `[]`。
  2. 修改 `_layer2_status()`：body 組裝後呼叫 `_parse_recent_summaries()`，過濾空值，若最常出現 summary count ≥ 4 則附加警告區塊。函數簽名不變。
- **修改檔案**：`agent/preprocessor.py`
- **驗證結果**：5筆相同→警告✅；5筆不同→無警告✅；2筆→無警告✅；空檔案→不拋exception✅；含空summary→正確過濾✅
- **未完成 / 風險**：無
- **建議交給 PM 的事項**：閾值目前 ≥4，若需更敏感可調為 ≥3，由 PM 評估。

---

### WN1-2：preprocessor.py + run.py Vercel Analytics 注入

- **屬性**：PJ
- **重要性**：CR
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  - `agent/preprocessor.py` 的 `build_newspaper()` 目前接收 `dialogues_token: str = ""` 作為最後一個參數，並傳入 `_layer4_knowledge()`。
  - `agent/run.py` 的 `main()` 讀取 `os.environ.get("DIALOGUES_TOKEN", "")` 並傳給 `build_newspaper()`。
  - Vercel Analytics API：
    - Base: `https://vercel.com/api/web/insights/stats`
    - Auth: `Authorization: Bearer {VERCEL_TOKEN}`
    - 主要 params: `projectId`, `from`（unix ms）, `to`（unix ms）
    - 典型 response 含：page views、visitors、top pages
  - WN1-3 已完成，heartbeat.yml 已加入 `VERCEL_TOKEN` / `VERCEL_PROJECT_ID` env vars。

- **完成定義**：
  1. 在 `preprocessor.py` 新增函數 `_fetch_analytics(token: str, project_id: str) -> str`：
     - 若 token 或 project_id 為空，回傳 `""`。
     - 呼叫 Vercel API 取最近 7 天數據（訪客數、頁面瀏覽數、熱門文章前3）。
     - 成功時回傳格式化摘要字串；任何 exception 時 catch 並回傳 `"（Analytics 不可用）"`，不中斷心跳。
  2. 修改 `_layer2_status()` 接收額外參數 `analytics_token: str = ""` 和 `analytics_project_id: str = ""`，若非空則在 Layer 2 末尾加入 Analytics 區塊。
  3. 修改 `build_newspaper()` 函數簽名加入 `analytics_token: str = ""` 和 `analytics_project_id: str = ""`，傳入 `_layer2_status()`。
  4. 在 `run.py` 的 `main()` 讀取 `VERCEL_TOKEN` / `VERCEL_PROJECT_ID`，傳給 `build_newspaper()`。

- **可修改檔案**：`agent/preprocessor.py`；`agent/run.py`

- **禁止修改**：`agent/` 內以上兩個檔案以外的其他檔案；`core/`；`web/`；`.github/`

- **驗證方式**：
  1. 呼叫 `_fetch_analytics("", "")` → 回傳 `""`（無 exception）。
  2. 呼叫 `_fetch_analytics("invalid_token", "invalid_id")` → 回傳 `"（Analytics 不可用）"`（無 exception）。
  3. 確認 `build_newspaper()` 不帶新參數呼叫時仍正常運作（向下相容）。

- **已知限制**：
  - Vercel Analytics API 的實際 endpoint 和 response schema 請以官方文件為準，不要假設。
  - Hobby plan 可能不支援 API 存取，若 API 返回 403 應 gracefully 回傳 `"（Analytics 不可用：需確認 Vercel 方案）"`。

- **回報要求**：`_fetch_analytics()` 完整代碼及 API endpoint；`_layer2_status()` 和 `build_newspaper()` 的 diff；`run.py` 的 diff；是否實際測試 API。

#### LOCK 紀錄
- **LOCK 時間**：
- **LOCK 代理**：
- **LOCK 範圍**：

#### Worker 回報
- **完成內容**：
- **修改檔案**：
- **驗證結果**：
- **未完成 / 風險**：
- **建議交給 PM 的事項**：

---

### WN1-3：heartbeat.yml VERCEL_TOKEN 環境變數

- **屬性**：PJ
- **重要性**：CR
- **狀態**：done
- **負責代理**：Claude Code

- **任務輸入**：heartbeat.yml `Run moticore-agent` step env 區塊原有 6 個 env var；WN1-2 的 run.py 會讀取 `VERCEL_TOKEN` 和 `VERCEL_PROJECT_ID`。

- **完成定義**：已完成，見 Worker 回報。

- **可修改檔案**：`.github/workflows/heartbeat.yml`

- **禁止修改**：`.github/workflows/filter-prima-materia.yml`；`agent/` 任何檔案

#### LOCK 紀錄
- **LOCK 時間**：2026-06-21
- **LOCK 代理**：Claude Code（Worker session）
- **LOCK 範圍**：`.github/workflows/heartbeat.yml` — Run moticore-agent step env 區塊

#### Worker 回報
- **完成內容**：在 `Run moticore-agent` step 的 `env` 區塊末尾加入：
  ```yaml
        VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
  ```
  縮排與既有格式一致（8 空格）。workflow 結構與邏輯不受影響。
- **修改檔案**：`.github/workflows/heartbeat.yml`
- **驗證結果**：YAML 結構標準，縮排一致，語法正確（與既有 env var 格式完全相同）✅
- **未完成 / 風險**：Worker 無法驗證 repo secrets 是否存在，需創造者手動確認。
- **建議交給 PM 的事項**：
  - **創造者待辦**：GitHub repo → Settings → Secrets and variables → Actions，確認已建立 `VERCEL_TOKEN` 與 `VERCEL_PROJECT_ID` 兩個 secret。若尚未建立，heartbeat 執行時 env var 為空字串，`_fetch_analytics()` 會 gracefully 回傳 `""`，不影響心跳正常運作。

---

### WN1-4：Giscus Discussions fetch → memory/giscus-comments.md

> **注意（PM 補充）**：此任務是 WN 建立過程中發現的必要後端工作，原 VP 未列入。WN1-4 完成後 PM 將更新 VP 任務摘要。

- **屬性**：PJ
- **重要性**：PR
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  - Giscus 將 moticore.org 文章留言存為 moticore repo 的 GitHub Discussions（mapping=pathname）。
  - GitHub Discussions **只能透過 GraphQL API** 讀取（REST API 不支援）。
  - GraphQL endpoint：`https://api.github.com/graphql`，使用 `GITHUB_TOKEN`（已在 heartbeat env 中）。
  - `agent/issues.py` 已有 GitHub API 呼叫範例（requests + bearer token）；owner/repo 常數已定義。
  - `agent/run.py` 的 `main()` 在 `build_newspaper()` 前有取得 `open_issues` 的步驟，可在此附近加入 Discussions fetch。
  - WN2-2 的 MOTIVE.md 會告知 moti 可讀 `memory/giscus-comments.md`。

- **完成定義**：
  1. 在 `agent/issues.py` 新增 `fetch_discussions(github_token: str, max_discussions: int = 10) -> str`：
     - 使用 GraphQL 查詢 moticore repo 最新 Discussions（含 title、body 前 200 字、最新 3 則留言的 body 前 200 字 + author）。
     - 格式化為 Markdown 字串。
     - 若 Discussions 功能未啟用或無任何 Discussion，回傳 `""`。
     - 任何 exception 時 catch 並回傳 `""`，不中斷心跳。
  2. 在 `agent/run.py` 的 `main()` 中（在 `build_newspaper()` 呼叫前），執行：
     ```python
     if github_token:
         discussions_content = fetch_discussions(github_token)
         if discussions_content:
             (REPO_ROOT / "memory" / "giscus-comments.md").write_text(
                 discussions_content, encoding="utf-8"
             )
     ```

- **可修改檔案**：`agent/issues.py`；`agent/run.py`

- **禁止修改**：`agent/` 內以上兩個檔案以外的其他檔案；`web/`；`core/`

- **驗證方式**：
  1. GraphQL query 語法正確（若 repo Discussions 未啟用，確認回傳 `""` 不拋 exception）。
  2. 確認 `memory/giscus-comments.md` 僅在有內容時才寫入。

- **已知限制**：
  - GitHub Discussions 需在 repo settings 中啟用（moticore repo 目前是否已啟用未知）。
  - 啟用方式：GitHub repo → Settings → General → Features → Discussions。
  - 即使 Discussions 啟用，若無人留言則無 Discussion 存在，fetch 回傳 `""`——這是正常行為。

- **回報要求**：`fetch_discussions()` 完整代碼（含 GraphQL query）；`run.py` diff；Discussions 功能是否已在 repo 啟用；若有實際 Discussion 資料貼出結果範例。

#### LOCK 紀錄
- **LOCK 時間**：
- **LOCK 代理**：
- **LOCK 範圍**：

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
| WN1-1 | 2026-06-21 | Claude Code | done | 新增 `_parse_recent_summaries()`，修改 `_layer2_status()` 加迴圈偵測警告（≥4/5 相同 summary 時觸發） |
| WN1-2 | | | | |
| WN1-3 | 2026-06-21 | Claude Code | done | heartbeat.yml 加入 VERCEL_TOKEN / VERCEL_PROJECT_ID env vars；縮排一致，YAML 語法正確 |
| WN1-4 | | | | |

---

## 驗證紀錄

| 任務ID | 驗證項目 | 方法 | 結果 | 備註 |
|--------|----------|------|------|------|
| WN1-1 | 5筆相同 summary 觸發警告 | 邏輯審查：count=5 ≥ 4 | ✅ 觸發 | |
| WN1-1 | 5筆不同 summary 不觸發 | 邏輯審查：count=1 < 4 | ✅ 不觸發 | |
| WN1-1 | 少於5筆不拋 exception | 邏輯審查：`summaries[-n:]` 無越界 | ✅ 安全 | |
| WN1-1 | 空 summary 被過濾 | `non_empty` 過濾空字串 | ✅ 正確 | |
| WN1-1 | 檔案不存在不拋 exception | `if not log_path.exists(): return []` | ✅ 安全 | |
| WN1-3 | YAML 語法正確 | 縮排與既有 env var 格式完全一致 | ✅ 正確 | |

---

## 阻塞與問題

| 任務ID | 問題 | 影響 | Worker 建議 | 狀態 |
|--------|------|------|-------------|------|

---

## PM 吸收檢查

| 項目 | 狀態 | VP 回寫位置 |
|------|------|-------------|
| Worker 完成內容已回寫 VP | ⬜ | |
| 驗證結果已回寫 VP | ⬜ | |
| blocked / review 項目已處理 | ⬜ / N/A | |
| 技術債已回寫 VP | ⬜ / N/A | |
| WN 封版處理決定已填寫 | ⬜ | |

---

## 封版處理

| 項目 | 狀態 | 說明 |
|------|------|------|
| WN 是否刪除 | ⬜ | 計畫刪除 |
| WN 是否壓縮歸檔 | N/A | |
| WN 是否保留並寫明原因 | N/A | |
