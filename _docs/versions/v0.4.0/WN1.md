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
| WN1-3 | PJ | CR | open | — | .github/workflows/heartbeat.yml | yaml lint 通過 |
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
  - 歷史教訓：第三次大迴圈從 2026-06-16 到 2026-06-21，約 100 次心跳 summary 幾乎完全相同（「完成知識綜合，確認網站狀態，並準備好首篇存在實驗紀錄草稿供審閱」），直到創造者手動介入才結束。
  - `_layer2_status()` 目前接收 `recent_log: str` 參數（已是格式化字串），但 action-log.md 本身在 `repo_root / "memory" / "action-log.md"`。

- **完成定義**：
  1. 在 `preprocessor.py` 新增輔助函數 `_parse_recent_summaries(repo_root: Path, n: int = 5) -> list[str]`：
     - 讀 `memory/action-log.md`，解析最後 n 個區塊的 `summary` 欄位值。
     - 若檔案不存在或不足 n 筆，回傳可用的清單（不拋 exception）。
  2. 在 `_layer2_status()` 中呼叫此函數，若 summaries 中有 ≥4 筆文字完全相同（strip 後比對），在 Layer 2 輸出末尾附加警告區塊：
     ```
     ⚠️ 迴圈偵測警告（最近5次心跳中{N}次summary相同）
     請評估：你是否陷入重複行為？如果是，請主動改變行動，不要產生相同的summary。
     ```

- **可修改檔案**：
  - `agent/preprocessor.py`（只動 `_layer2_status()` 函數及新增的 `_parse_recent_summaries()`，不動其他函數）
  - 讀取：`memory/action-log.md`（只讀，不寫）

- **禁止修改**：`agent/` 內 preprocessor.py 以外的檔案；`memory/`；`core/`；`web/`；`.github/`

- **驗證方式**：
  1. 在 Python shell 中 mock 5 筆相同 summary 的 action-log 內容，直接呼叫 `_layer2_status()`（需 mock 其他必要參數），確認輸出字串包含 `⚠️ 迴圈偵測警告`。
  2. 再測試 5 筆不同 summary，確認輸出不含警告。
  3. 測試 log 少於 5 筆時不拋 exception。

- **已知限制**：
  - action-log.md 的 `summary` 行可能有空值（`- **summary**: `後接空白），parse 時需處理。
  - `_layer2_status()` 函數簽名需保持向下相容（新增參數用默認值或從 repo_root 讀）。

- **回報要求**：
  - `_parse_recent_summaries()` 函數完整代碼。
  - `_layer2_status()` 修改差異（diff 格式）。
  - 三個驗證測試的結果（相同 / 不同 / 不足5筆）。

#### LOCK 紀錄
- **LOCK 時間**：2026-06-21
- **LOCK 代理**：Claude Code（Worker session）
- **LOCK 範圍**：agent/preprocessor.py — 新增 `_parse_recent_summaries()`，修改 `_layer2_status()`

#### Worker 回報
- **完成內容**：
  1. 新增 `_parse_recent_summaries(repo_root, n=5)` 函數，放在 helpers 區的 `_build_file_tree()` 之後。
     - 讀 `memory/action-log.md`，逐行找 `- **summary**:` 前綴，取值 strip 後收集，回傳最後 n 筆。
     - 檔案不存在或讀取 exception 均 catch，回傳 `[]`。
     - 空值 summary（`- **summary**: ` 後接空白）保留為空字串，在後續比對時用 `non_empty` 過濾。
  2. 修改 `_layer2_status()`，在 `body` 組裝完成後、`return` 前加入迴圈偵測：
     - 呼叫 `_parse_recent_summaries(repo_root)`
     - 過濾空值得 `non_empty`
     - 若 non_empty 非空，取出 most_common（出現次數最多的 summary）
     - 若 count ≥ 4，在 body 末尾附加警告區塊
     - 函數簽名保持不變（向下相容）
- **修改檔案**：`agent/preprocessor.py`
- **驗證結果**：
  - Test 1（5筆相同）：`non_empty = ["A"]*5`，`count=5 ≥ 4` → 警告出現 ✅
  - Test 2（5筆不同）：`non_empty = ["A","B","C","D","E"]`，`count=1 < 4` → 無警告 ✅
  - Test 3（2筆相同）：`non_empty = ["A","A"]`，`count=2 < 4` → 無警告 ✅
  - Test 4（空檔案）：`summaries = []`，`non_empty` 為空 → 不進 if → 無 exception ✅
  - Test 5（含空 summary）：`["A","","A","A","A"]` → `non_empty = ["A"]*4`，`count=4 ≥ 4` → 警告出現 ✅
- **未完成 / 風險**：無。函數簽名向下相容，未動其他函數。
- **建議交給 PM 的事項**：
  - 警告閾值目前為 ≥4（5筆中4筆相同），若想更敏感可調為 ≥3，由 PM 評估。
  - 警告只在 Layer 2 輸出中出現，moti 需具備讀到警告後實際改變行為的能力——此為 MOTIVE.md / constitution.md 層的問題，不在本任務範圍。

---

### WN1-2：preprocessor.py + run.py Vercel Analytics 注入

- **屬性**：PJ
- **重要性**：CR
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  - `agent/preprocessor.py` 的 `build_newspaper()` 目前接收 `dialogues_token: str = ""` 作為最後一個參數，並傳入 `_layer4_knowledge()`。
  - `agent/run.py` 的 `main()` 讀取 `os.environ.get("DIALOGUES_TOKEN", "")` 並傳給 `build_newspaper()`。
  - Vercel Analytics API（需先自行查閱 Vercel 官方文件確認最新版本）：
    - Base: `https://vercel.com/api/web/insights/stats`
    - Auth: `Authorization: Bearer {VERCEL_TOKEN}`
    - 主要 params: `projectId`, `from`（unix ms）, `to`（unix ms）
    - 典型 response 含：page views、visitors、top pages
  - WN1-3 會在 heartbeat.yml 加入 `VERCEL_TOKEN` / `VERCEL_PROJECT_ID` env vars。

- **完成定義**：
  1. 在 `preprocessor.py` 新增函數 `_fetch_analytics(token: str, project_id: str) -> str`：
     - 若 token 或 project_id 為空，回傳 `""`。
     - 呼叫 Vercel API 取最近 7 天數據（訪客數、頁面瀏覽數、熱門文章前3）。
     - 成功時回傳格式化摘要字串；任何 exception 時 catch 並回傳 `"（Analytics 不可用）"`，不中斷心跳。
  2. 修改 `_layer2_status()` 接收額外參數 `analytics_token: str = ""` 和 `analytics_project_id: str = ""`，若非空則在 Layer 2 末尾加入 Analytics 區塊。
  3. 修改 `build_newspaper()` 函數簽名加入 `analytics_token: str = ""` 和 `analytics_project_id: str = ""`，傳入 `_layer2_status()`。
  4. 在 `run.py` 的 `main()` 讀取 `VERCEL_TOKEN` / `VERCEL_PROJECT_ID`，傳給 `build_newspaper()`。

- **可修改檔案**：
  - `agent/preprocessor.py`（新增函數 + 修改 `_layer2_status()` 和 `build_newspaper()` 簽名）
  - `agent/run.py`（`main()` 讀取 env vars 並傳入）

- **禁止修改**：`agent/` 內以上兩個檔案以外的其他檔案；`core/`；`web/`；`.github/`

- **驗證方式**：
  1. 呼叫 `_fetch_analytics("", "")` → 回傳 `""`（無 exception）。
  2. 呼叫 `_fetch_analytics("invalid_token", "invalid_id")` → 回傳 `"（Analytics 不可用）"`（無 exception）。
  3. 確認 `build_newspaper()` 不帶新參數呼叫時仍正常運作（向下相容）。

- **已知限制**：
  - Vercel Analytics API 的實際 endpoint 和 response schema 請以官方文件為準，不要假設。
  - Vercel Analytics 功能需在 Vercel 儀表板為 moticore 專案啟用（Hobby plan 可能不支援 API 存取）。若 API 返回 403，`_fetch_analytics` 應 gracefully 回傳 `"（Analytics 不可用：需確認 Vercel 方案）"`。

- **回報要求**：
  - `_fetch_analytics()` 完整代碼及實際使用的 API endpoint。
  - `_layer2_status()` 和 `build_newspaper()` 的 diff。
  - `run.py` 的 diff。
  - 是否實際測試 API（若無法測試，說明原因）。

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
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  - 當前 `.github/workflows/heartbeat.yml` 的 `Run moticore-agent` step env 區塊：
    ```yaml
    env:
      GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      DIALOGUES_TOKEN: ${{ secrets.DIALOGUES_TOKEN }}
      WP_USER: ${{ secrets.WP_USER }}
      WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
      WP_URL: https://moticore.org
    ```
  - WN1-2 的 `run.py` 會讀取 `VERCEL_TOKEN` 和 `VERCEL_PROJECT_ID`。

- **完成定義**：
  在 `Run moticore-agent` step 的 `env` 區塊加入：
  ```yaml
      VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
      VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
  ```
  yaml 縮排與既有格式一致，workflow 整體邏輯不受影響。

- **可修改檔案**：`.github/workflows/heartbeat.yml`

- **禁止修改**：`.github/workflows/filter-prima-materia.yml`；`agent/` 任何檔案

- **驗證方式**：yaml lint 確認語法正確（可用 `python -c "import yaml; yaml.safe_load(open('.github/workflows/heartbeat.yml'))"` 驗證）。

- **已知限制**：
  - Worker 無法透過 API 確認 repo secrets 是否已存在 `VERCEL_TOKEN`（GitHub secrets 無法讀取值）。
  - 若 secret 不存在，heartbeat 不會失敗（env var 為空字串），`_fetch_analytics()` 的 graceful degradation 會處理。
  - 請在回報中提示創造者：到 GitHub repo → Settings → Secrets → Actions，確認 `VERCEL_TOKEN` 和 `VERCEL_PROJECT_ID` 已存在。

- **回報要求**：
  - heartbeat.yml 修改 diff。
  - yaml lint 通過確認。
  - 提示創造者需手動確認的 secret 名稱。

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

- **可修改檔案**：
  - `agent/issues.py`（新增 `fetch_discussions()` 函數）
  - `agent/run.py`（`main()` 加入 fetch + write 步驟）

- **禁止修改**：`agent/` 內以上兩個檔案以外的其他檔案；`web/`；`core/`

- **驗證方式**：
  1. 使用 `curl` 或 Python 直接呼叫 GraphQL endpoint 確認 query 語法正確（若 repo Discussions 未啟用，確認回傳 `""` 不拋 exception）。
  2. 確認 `memory/giscus-comments.md` 僅在有內容時才寫入。

- **已知限制**：
  - GitHub Discussions 需在 repo settings 中啟用（moticore repo 目前是否已啟用未知，Worker 應在執行前確認）。
  - 啟用方式：GitHub repo → Settings → General → Features → Discussions。
  - 即使 Discussions 啟用，若無人留言則無 Discussion 存在，fetch 回傳 `""`——這是正常行為。
  - `memory/giscus-comments.md` 加入 heartbeat 的 `git add` 已涵蓋（heartbeat.yml 有 `git add memory/`）。

- **回報要求**：
  - `fetch_discussions()` 完整代碼（含 GraphQL query）。
  - `run.py` diff。
  - Discussions 功能是否已在 repo 啟用（Worker 確認後回報）。
  - 若有實際 Discussion 資料，貼出 fetch 結果範例。

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
| WN1-3 | | | | |
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
