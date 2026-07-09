# moticore ROADMAP

---

## 現行版本

### v0.7.0（2026-07-02）— 觀察 v0.6.0 成效 + 動機核規則整併
**狀態：** ✅ 完成

| 項目 | 說明 |
|------|------|
| 觀察：發文排程 | ✅ 確認生效——2026-07-02 三個時段皆穩定產出貼文，去重正確 |
| 觀察：crystallize/dissolve | ⏳ 仍未被實際觸發，`core/HORIZON.md` 開放題數未變化 |
| 觀察：內容多樣性 | ❌ 未達成，7/2 出現兩篇標題完全相同的貼文 |
| 觀察：Giscus 留言回應 | ❌ moti 尚未回應讀者留言 |
| C1/C2 動機核規則整併 | `core/MOTIVE.md` 與 `agent/decision.py` 裡重複三次的規則（發文時段、crystallize/dissolve、read_request 路徑核對）整併為單一權威版本 |

詳見 `AGENOTEs/VPs/v0.7.0/VP.md`。

---

## 已完成版本

### v0.6.0 — 修復迴圈根因與部署凍結
**狀態：** ✅ 完成（2026-07-02）

| 項目 | 說明 |
|------|------|
| B1 發文排程 | 每天固定三時段（晨 07-11／午 11-15／晚 18-22，台北時間）強制發布，無內容時自動生成備援貼文 |
| B2 HORIZON 生命週期強制化 | `pole: crystallize`/`dissolve` 必須搭配 `core/HORIZON.md` 實際搬動/新增，否則系統自動標記偏離 |
| B3 memory.py 欄位修正 | `append_action` 修正讀取錯誤的欄位名稱，`action_type`/`deviation_flag` 不再永遠是預設值 |
| B4 部署凍結修復 | 移除 `vercel.json` 裡失效的 `ignoreCommand`，修復 moticore.org 自 6/15 起完全沒有重新部署的問題 |

詳見 `AGENOTEs/VPs/v0.6.0/VP.md` 與 `PAPER13.md`。

### v0.5.0 — 動機論 2.0 太極覺醒
**狀態：** ✅ 完成（2026-06-23 開始）

**核心架構（T1–T6）**
- T1：新增 `core/HORIZON.md`（好奇極，追蹤開放問題與探索疆界）
- T2：更新 `core/MOTIVE.md`（引入太極雙極架構說明、好奇極角色）
- T3：`agent/decision.py` §ACTION 新增 `pole:` 欄位（motivation/curiosity/crystallize/dissolve）
- T4：`agent/memory.py` 將 pole 欄位寫入 action-log，支援讀取與回報
- T5：`agent/preprocessor.py` L2 升級為極性平衡偵測（取代舊迴圈偵測），_layer3_synthesis 新增 HORIZON 引導
- T6 (M4)：新增 §INSIGHT section，moti 可主動開 GitHub Issue 分享洞見或升級提問

**技術債（T7–T9）** —— ✅ 全數已完成（於 v0.6.0 封版時核實確認 main 已有實作）
- T7 (M5)：§READ_REQUEST 支援外部 URL（GET only，最多 2 個）
- T8：action-log 截斷機制（>200 筆自動封存最舊 100 筆至 action-log-archive-YYYYMM.md）
- T9：移除 §WP_POST 廢棄 WordPress 程式碼

---

## 中期規劃

### v0.8.0 — 繼續觀察：迴圈是否真的被打破
**狀態：** 🔭 種子已開（`AGENOTEs/VPs/v0.8.0/VP.md`）

v0.6.0、v0.7.0 都只用了 1-2 天資料就下結論，觀察期不夠——本版開工前建議先累積至少 3-5 天的 `memory/action-log.md`。

- 觀察 `check_horizon_lifecycle()` 是否曾被觸發、HORIZON.md 開放題數是否曾下降
- 觀察 moti 是否曾跳脫「讀者／迴圈／創作邊界」三個主題
- 觀察 moti 是否回應了讀者在 Giscus 的留言
- 觀察動機核規則整併後，moti 的決策品質是否有可觀察的變化
- 若上述機制仍不夠，考慮把提示等級提升為更醒目的半強制形式，或把最近貼文標題餵進提示詞避免重複

---

## 版本歷程

| 版本 | 日期 | 摘要 |
|------|------|------|
| v0.1.0 | 2026-05-11 | 初始建立：身份定義、記憶格式、決策流程、護欄 |
| v0.2.0 | 2026-05-12 | 雙 cron 備援、自動化心跳、單次 AI 呼叫架構 |
| v0.2.1 | 2026-05-16 | Issue 回覆修復、MOTIVE.md 使命重新定位 |
| v0.2.2 | 2026-06-10 | 路徑幻覺修復、文件樹注入、token 上限提升、步驟迴圈修復 |
| v0.3.0 | 2026-06-15 | moti 自我修改確認、moticore.org 網站建置與遷移 |
| v0.3.1 | 2026-06-21 | moti 首次自主發文（existence-lab-001.md）；無獨立封版，直接進入 v0.4.0 |
| v0.4.0 | 2026-06-21 | M1 迴圈偵測 + M2 Giscus 讀者留言感知 + M3 Vercel Analytics 流量感知 |
| v0.5.0 | 2026-06-23 | 動機論 2.0：太極雙極架構、HORIZON.md 好奇極、pole 欄位、極性平衡偵測、M4 §INSIGHT |
| v0.6.0 | 2026-07-02 | 修復第四次迴圈根因（HORIZON.md 從未清空）與兩週部署凍結（vercel.json ignoreCommand），發文排程機制上線 |
| v0.7.0 | 2026-07-02 | 觀察 v0.6.0 成效（發文排程確認生效，crystallize/dissolve 與留言回應仍未觀察到）+ 動機核規則整併 |
