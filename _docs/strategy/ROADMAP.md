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

## 下一版本

### v0.5.0 — moti 主動表達
**狀態：** 💡 構想中

- M4：§QUESTION 放寬，允許 moti 主動開 Issue 分享洞見
- M5：§READ_REQUEST 支援外部 URL（讓 moti 能讀外部資料）
- action-log.md 截斷機制（避免無限增長）

---

## 中期規劃

### v0.6.0 — 多代理擴展（長期）
**狀態：** 🔭 遠期構想

- 多個代理各自有不同動機核，透過同一 repo 互動
- moticore 作為開源框架對外開放

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
