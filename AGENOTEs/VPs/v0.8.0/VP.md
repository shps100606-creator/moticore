# v0.8.0 Main VP — 繼續觀察：迴圈是否真的被打破

---

## 版本狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.8.0
- **目前角色**：—
- **目前階段**：execution — WN1 兩項任務已完成（見下方「技術決策」與 WN1）
- **種子來源**：v0.7.0 覆盤 + 技術債
- **建立時間**：2026-07-02
- **最後更新**：2026-07-09
- **WN**：[[AGENOTEs/VPs/v0.8.0/WN1.md]]

---

## 觀察評估結果（260709）

依據 [[NOTE_MEET_260709_001]]，07-03～07-09 共 7 天觀察資料（超過種子設定的 3-5 天門檻）評估如下：

| 待驗證項目 | 結論 |
|-----------|------|
| `check_horizon_lifecycle()` 是否曾觸發 | ✅ 已確認觸發——`core/HORIZON.md`「已結晶」區塊自 07-05 起累積 8 筆，action-log 20 筆 `pole: crystallize`。但 dissolve 極（沉澱候選）仍完全空白，0 次觸發 |
| moti 是否跳脫「讀者／迴圈／創作邊界」三主題 | 部分改善（主題有演進），但新發現 07-04 出現兩篇內容幾乎相同的貼文——與 07-02 同類重複問題再犯，指向**發布管線本身有重複寫入 bug**，不只是內容多樣性問題 |
| Giscus 留言回應 | ❌ 未回應。追查發現**架構缺口**：`agent/issues.py` 的 `fetch_discussions()` 只做讀取，完全沒有回覆／寫入 Giscus 的機制。創作者本人 07-02 的留言提問至今無法被回應 |
| 貼文檔名 UTC/台北不一致 | 本次未檢查，維持低優先技術債 |
| 規則整併（C1/C2）後決策品質 | 正面訊號：7 天內 `deviation_flag` 無「顯著」記錄（「無」94／「輕微」23），但樣本未必涵蓋所有情境 |

使用者確認兩項候選任務都要做，且確認「不得修改 agent/」為舊規則、已從 CLAUDE.md 移除。落成 WN1（見下），本 session 同時完成規劃與執行。

---

## 技術決策

### D1：重複貼文 bug — 發文 slug 去 title 化

- 問題：`handle_journal()` 原本用 `{date}-{window}-{title 的 slug}` 當檔名，LLM 每次生成的標題文字不同，若同一視窗被寫入兩次（例如前一次心跳的 `journal-state.json` 更新尚未反映在檢查點），會產生兩個不同檔名、內容相近的貼文檔案，而非被現有的「每視窗最多一篇」防呆擋下
- 選項：A) 保留 title-based slug，另外加锁機制／二次比對 　B) 把 slug 改成純 `{date}-{window}`，讓同視窗的第二次寫入直接撞名
- 決定：B
- 理由：B 是最小改動、無新增狀態；即使真的發生同視窗雙寫，第二次會覆蓋同一檔案而非產生新檔案，若兩次寫入來自不同 CI job 各自 commit，git 的 fast-forward-only push 會讓後到者的 push 失敗並在 Actions 顯示為錯誤，是比「靜默產生重複公開文章」更安全的失敗模式。副作用：Giscus 留言的 URL（依路徑）在同一視窗內保持穩定，不受標題重寫影響
- 未能確認的部分：這份 repo 是淺層 clone（`git rev-parse --is-shallow-repository` = true），真正觸發 07-04 重複寫入的原始時序無法從本地 git log 還原，上述是根據程式碼推論出的最可能機制，不是逐行覆核過的實錄

### D2：Giscus 留言回覆機制

- 問題：`agent/issues.py` 的 `fetch_discussions()` 原本只做 GraphQL 讀取查詢，且讀到的內容從未被接入 `preprocessor.py` 組出的「newspaper」提示詞——moti 實際上從來沒有在心跳輸入裡看過讀者留言，也沒有任何寫入/回覆 API
- 選項：A) 只讓 moti 在 §JOURNAL 貼文裡間接回應（原設計）　B) 新增 GraphQL `addDiscussionComment` mutation，讓 moti 能直接對特定留言發串接回覆
- 決定：B
- 理由：A 的問題是無法針對特定留言、不會通知留言者、且觀察 7 天實際上從未被使用過；B 提供真正的能力缺口修補。設計採「短代號」（`G1`、`G2`…）取代直接把 GraphQL node ID 塞進提示詞，因為 LLM 覆寫長 ID 容易出錯；`memory/giscus-replied.json` 記錄已回覆的留言 ID，避免同一則留言被反覆提示
- 涉及檔案：`agent/issues.py`（新增 `post_discussion_reply()`；`fetch_discussions()` 改為回傳 `(text, label_map)` 並支援 `replied_ids` 過濾）、`agent/preprocessor.py`（`build_newspaper()`／`_layer2_status()` 新增 `giscus_note` 參數）、`agent/decision.py`（新增 `§GISCUS_REPLY label={代號}` 區塊格式與解析）、`agent/run.py`（新增 `handle_giscus_replies()`，串接 label_map 與已回覆狀態持久化）、`.github/workflows/heartbeat.yml`（`permissions` 新增 `discussions: write`，否則 `GITHUB_TOKEN` 無權限呼叫 mutation）
- 未解決問題：GraphQL mutation 本身未在真實 GitHub API 上驗證（僅以 mock `requests.post` 做單元層級 smoke test），需要下一次真實心跳跑過一次才能確認 `GITHUB_TOKEN` 的 `discussions: write` 權限與 Giscus 的 mapping 機制真的允許這個 mutation 成功

---

## 版本定性（種子）

v0.6.0／v0.7.0 兩版都只用了 1-2 天的資料就要下結論，觀察期明顯不夠——crystallize/dissolve、留言回應都是 moti 自主判斷的行為，不會每次心跳都發生。**v0.8.0 開工前，建議先累積至少 3-5 天的 `memory/action-log.md` 再開始評估**，不要重蹈觀察期過短的覆轍。

### 待驗證項目（承接自 v0.6.0 / v0.7.0）

- `check_horizon_lifecycle()` 是否曾在 `pole: crystallize`/`dissolve` 時被觸發過警告；`core/HORIZON.md` 的「開放中」題數是否曾經下降過
- moti 是否曾經跳脫「讀者／迴圈／創作邊界」這三個主題，寫出真正不同的內容
- moti 是否回應了使用者在 Giscus 留言區的留言（截至 v0.7.0 封版仍未回應）
- 貼文檔名 UTC/台北日期不一致是否需要修（低優先，純命名）
- 動機核規則整併（v0.7.0 C1/C2）後，moti 的決策品質是否有可觀察的變化

### 潛在方向（若觀察後確認機制仍不夠）

- 若 crystallize/dissolve 持續沒有發生，現有的「顯著偏離」抓包只對「宣稱但沒做」有效，對「乾脆不宣稱」沒有約束力——可以考慮：若好奇極連續探索同一批題目超過 N 次仍未 crystallize，直接在 Layer 2 用更強的措辭要求處理，而不只是建議
- 若 Giscus 留言持續沒有回應，考慮把「有新留言」做成類似發文時段的半強制提示
- 若確認 moti 反覆寫出幾乎相同的內容，可以考慮把最近幾篇 §JOURNAL 標題/摘要餵進提示詞，明確要求不要重複

---

## PM 驗收

| 任務 | 完成標準 | 驗證方式 | 狀態 |
|------|---------|---------|------|
| D1 重複貼文 bug 修復 | 同一 date+window 至多一個 `web/content/posts/` 檔案 | `py_compile`；程式碼審查確認 slug 生成邏輯；合併後心跳（13:44 UTC）落在已發布的晚間視窗，正確跳過未重複寫入 | ✅ 完成並經一次真實心跳驗證無異常 |
| D2 Giscus 回覆機制 | moti 能看到讀者留言、能對指定留言發出串接回覆、已回覆留言不重複提示 | `py_compile`；三項離線 smoke test；**真實心跳驗證通過**（見下） | ✅ 完成並已驗證成功 |

**部署狀態（260709 補充）**：WN1 原本只在 feature branch `claude/agenote-enablement-izknyf`，合併前兩次真實心跳（11:30、11:51 UTC）用的都還是舊程式碼。已開 PR #47 並合併進 `main`（merge commit `b3e898d`）。合併後排程隔了近 2 小時未觸發（原因不明，GitHub Actions 排程延遲，workflow 本身狀態確認為 `active`），改用 `workflow_dispatch` 手動觸發一次驗證（run 29022498124，13:44 UTC）。

**真實驗證結果**：job log 直接顯示 `[issues] Giscus reply posted`——對 07-02 創作者本人留言的串接回覆已成功發布；`GITHUB_TOKEN Permissions` 區塊確認 `Discussions: write` 生效；`memory/giscus-replied.json` 正確寫入該留言 ID（`DC_kwDOSZ-Dns4BCyrB`），避免下次心跳重複提示。D1、D2 均已在 production 完整驗證，WN1 兩項任務可視為完成。

---

## 覆盤

（封版時填）

---

## Release 封版確認

（Release session 執行）
