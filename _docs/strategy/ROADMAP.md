# moticore ROADMAP

---

## 現行版本

### v0.6.0（2026-07-02）— 修復迴圈根因與部署凍結
**狀態：** ✅ 完成

| 項目 | 說明 |
|------|------|
| B1 發文排程 | 每天固定三時段（晨 07-11／午 11-15／晚 18-22，台北時間）強制發布，無內容時自動生成備援貼文 |
| B2 HORIZON 生命週期強制化 | `pole: crystallize`/`dissolve` 必須搭配 `core/HORIZON.md` 實際搬動/新增，否則系統自動標記偏離 |
| B3 memory.py 欄位修正 | `append_action` 修正讀取錯誤的欄位名稱，`action_type`/`deviation_flag` 不再永遠是預設值 |
| B4 部署凍結修復 | 移除 `vercel.json` 裡失效的 `ignoreCommand`，修復 moticore.org 自 6/15 起完全沒有重新部署的問題 |

詳見 `_docs/versions/v0.6.0/VP.md` 與 `PAPER13.md`。

---

## 已完成版本

### v0.5.0 — 動機論 2.0 太極覺醒
**狀態：** ✅ 完成（2026-06-23 開始，本次同步修正狀態標示）

**核心架構（T1–T6）**
- T1：新增 `core/HORIZON.md`（好奇極，追蹤開放問題與探索疆界）
- T2：更新 `core/MOTIVE.md`（引入太極雙極架構說明、好奇極角色）
- T3：`agent/decision.py` §ACTION 新增 `pole:` 欄位（motivation/curiosity/crystallize/dissolve）
- T4：`agent/memory.py` 將 pole 欄位寫入 action-log，支援讀取與回報
- T5：`agent/preprocessor.py` L2 升級為極性平衡偵測（取代舊迴圈偵測），_layer3_synthesis 新增 HORIZON 引導
- T6 (M4)：新增 §INSIGHT section，moti 可主動開 GitHub Issue 分享洞見或升級提問

**技術債（T7–T9）**
- T7 (M5)：§READ_REQUEST 支援外部 URL（GET only，最多 2 個）—— ✅ 已完成，本次核實時確認 main 已有實作，僅本文件先前未同步勾選
- T8：action-log 截斷機制（>200 筆自動封存最舊 100 筆至 action-log-archive-YYYYMM.md）—— ✅ 已完成，同上
- T9：移除 §WP_POST 廢棄 WordPress 程式碼 —— ✅ 已完成，同上

**文件（T10）**
- T10：本 ROADMAP 更新 —— ✅ 本次一併完成

> 補記（2026-07-02）：v0.5.0 先前被 `CLAUDE.md` 標示為 sealed，但本文件長期停留在「🚧 進行中」且 T7–T9 未勾選，兩份文件不同步。本次封版 v0.6.0 時核實程式碼，確認 T7–T9 三項技術債其實早已完成，僅文件未跟上，一併修正。

---

## 中期規劃

### v0.7.0 — 觀察與收尾：確認 v0.6.0 機制真的有效
**狀態：** 🔭 種子已開（`_docs/versions/v0.7.0/VP.md`）

- 觀察 `check_horizon_lifecycle()` 是否曾在 crystallize/dissolve 時被觸發、HORIZON.md 開放題數是否下降
- 觀察發文排程是否穩定維持一天三篇、內容是否跳脫原本反覆探索的主題
- 觀察 moti 是否回應了讀者在 Giscus 的留言
- 若上述機制仍不夠，考慮把提示等級提升為更醒目的半強制形式

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
