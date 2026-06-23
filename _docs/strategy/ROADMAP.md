# moticore ROADMAP

---

## 現行版本

### v0.4.0（2026-06-21）— moti 感知世界的回饋
**狀態：** ✅ 完成

| 項目 | 說明 |
|------|------|
| M1 迴圈自動偵測 | `preprocessor.py` 讀取 action-log.md 最近 5 筆 summary，≥4 筆相同時 Layer 2 加入 ⚠️ 警告 |
| M2 Giscus 讀者留言 | 文章頁嵌入 Giscus 留言框；後端每次心跳 fetch GitHub Discussions 寫入 `memory/giscus-comments.md`；MOTIVE.md 告知 moti |
| M3 Vercel Analytics | 每次心跳呼叫 Vercel Analytics API，訪客數 + 熱門文章注入 Layer 2 |

---

## 進行中版本

### v0.5.0 — 動機論 2.0 太極覺醒
**狀態：** 🚧 進行中（2026-06-23 開始）

**核心架構（T1–T6）**
- T1：新增 `core/HORIZON.md`（好奇極，追蹤開放問題與探索疆界）
- T2：更新 `core/MOTIVE.md`（引入太極雙極架構說明、好奇極角色）
- T3：`agent/decision.py` §ACTION 新增 `pole:` 欄位（motivation/curiosity/crystallize/dissolve）
- T4：`agent/memory.py` 將 pole 欄位寫入 action-log，支援讀取與回報
- T5：`agent/preprocessor.py` L2 升級為極性平衡偵測（取代舊迴圈偵測），_layer3_synthesis 新增 HORIZON 引導
- T6 (M4)：新增 §INSIGHT section，moti 可主動開 GitHub Issue 分享洞見或升級提問

**技術債（T7–T9）**
- T7 (M5)：§READ_REQUEST 支援外部 URL（GET only，最多 2 個）
- T8：action-log 截斷機制（>200 筆自動封存最舊 100 筆至 action-log-archive-YYYYMM.md）
- T9：移除 §WP_POST 廢棄 WordPress 程式碼

**文件（T10）**
- T10：本 ROADMAP 更新

---

## 中期規劃

### v0.6.0 — 太極自動化（結晶 / 溶解機制）
**狀態：** 🔭 構想中

- 自動偵測 crystallize 時機（好奇極洞察成熟時自動寫入 MOTIVE.md）
- 自動偵測 dissolve 時機（動機核信念趨於僵化時自動開放為問題）
- HORIZON.md 定期自動整理（沉澱候選 → 已結晶 / 關閉）
- 多極震盪長期數據觀測（pole 分布視覺化）

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
