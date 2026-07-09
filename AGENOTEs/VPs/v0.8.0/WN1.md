# v0.8.0 WN1 — 重複貼文 bug 修復 + Giscus 回覆機制

---

## Worker 必讀

1. `AGENOTEs/VPs/v0.8.0/VP.md`「觀察評估結果」「技術決策」兩區——問題背景與 D1/D2 決策理由
2. `AGENOTEs/notes/NOTE_MEET_260709_001.md`——原始觀察評估記錄
3. `agent/run.py`、`agent/issues.py`、`agent/decision.py`、`agent/preprocessor.py`——本次任務的修改範圍

---

## 任務 1：D1 重複貼文 bug 修復

- **任務輸入**：`agent/run.py` 的 `handle_journal()`，原本用 `{date}-{window}-{title slug}` 產生檔名
- **完成條件**：同一 date+window 至多寫入一個 `web/content/posts/` 檔案；即使發生同視窗二次寫入，也是檔名碰撞覆蓋，不是產生新檔案
- **目標檔案**：`agent/run.py`（移除 `_slugify()`，slug 改為 `f"{date}-{window}"`；同步移除變成未使用的 `import re`）
- **驗證方式**：`python3 -m py_compile agent/run.py`；程式碼審查確認 `handle_journal()` 邏輯
- **已知限制**：本地 repo 為淺層 clone，無法從 git 歷史還原 07-04 重複貼文的真實觸發時序；此修復是根據程式碼推論的最小改動，不是逐行覆核過的根因修復。舊有的兩組重複貼文（07-02、07-04）未清理，是否要下架由使用者決定，本任務只處理往後的寫入行為
- **回報要求**：完成後在 VP「PM 驗收」勾狀態，說明驗證方式與未驗證風險
- **相依**：無
- **狀態**：✅ 完成（本 session）

---

## 任務 2：D2 Giscus 留言回覆機制

- **任務輸入**：`agent/issues.py` 的 `fetch_discussions()` 原本只讀取留言且從未接入 newspaper 提示詞，完全沒有回覆/寫入機制
- **完成條件**：
  1. moti 的心跳輸入（newspaper）能看到讀者留言，並附短代號（如 `G1`）
  2. moti 可用 `§GISCUS_REPLY label=G1` 對指定留言發出 GraphQL 串接回覆
  3. 已成功回覆的留言 ID 持久化在 `memory/giscus-replied.json`，之後不再帶代號出現，避免重複提示
- **目標檔案**：
  - `agent/issues.py` — 新增 `post_discussion_reply()`；`fetch_discussions()` 改為回傳 `(text, label_map)`，GraphQL query 加上 `id` 欄位並接受 `replied_ids` 過濾
  - `agent/preprocessor.py` — `build_newspaper()` / `_layer2_status()` 新增 `giscus_note` 參數，接在 `journal_note` 之後
  - `agent/decision.py` — REMARKS_INSTRUCTIONS 新增 `§GISCUS_REPLY label={代號}` 格式與規則 14；`parse_remarks()` 新增 `giscus_replies` 解析
  - `agent/run.py` — 新增 `handle_giscus_replies()`；`main()` 內建立 `giscus_label_map`／`giscus_note`，讀寫 `memory/giscus-replied.json`，並在 handler 派發區塊呼叫
  - `.github/workflows/heartbeat.yml` — `permissions` 新增 `discussions: write`
- **驗證方式**：
  - `python3 -m py_compile` 全部四個 `agent/*.py` 通過
  - 離線 smoke test（mock `requests.post`，stub `google.genai`）三項皆通過：`parse_remarks` 正確解析多個 `§GISCUS_REPLY` 區塊；`handle_giscus_replies` 正確派發合法 label、略過不存在的 label、正確持久化 `giscus-replied.json`；`fetch_discussions` 正確產生 label_map 並排除 `replied_ids` 中的留言
  - **未驗證**：真實 GitHub GraphQL API 呼叫（`discussions: write` 權限是否足夠、mutation 是否真的成功）需要下一次 CI 心跳實跑才能確認
- **已知限制**：短代號（`G1`、`G2`…）在單次心跳的 newspaper 內有效，不跨心跳持久化對應關係——如果 moti 在同一次心跳沒有回覆而下次心跳重新 fetch，代號可能重新編號（例如原本 G2 的留言下次變成 G1）。這是可接受的簡化，因為 label_map 只在單次 `main()` 執行內建立並使用，不會有代號指向錯誤留言的風險，只是代號本身不穩定
- **回報要求**：下一次真實心跳跑完後，檢查 Actions log 是否有 `[issues] Giscus reply posted` 或 `[issues] Giscus reply failed`，回報 VP「PM 驗收」的「未驗證的風險」是否已解除
- **相依**：無（與任務 1 各自獨立，但共用 `agent/run.py`，已在同一 session 內合併修改，無衝突）
- **狀態**：✅ 程式碼完成、離線驗證通過；真實 API 呼叫待下次心跳驗證
