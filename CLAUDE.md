# CLAUDE.md — moticore 代理行為守則

給接手這個 repo 的 AI 代理：本文件說明工作規則與導航方式。

---

## 接手順序

1. 確認本文件的 **版本狀態** 區塊 → 確認當前版本與 VP 路徑
2. 讀 `_docs/strategy/ROADMAP.md` → 確認目前版本狀態與下一步方向
3. 讀 `OVERVIEW.md` → 掌握系統架構與現況
4. 讀 `core/STATUS.md` → 確認任務收件匚與偏離記錄
5. 讀 `core/MOTIVE.md` → 確認代理身份與使命

---

## 版本開發：模式判斷表（framework: agenote-3.4）

Session 啟動時依下表自動分流，不需使用者指定模式。第一步永遠是讀下方「版本狀態」區塊定位最新版本資料夾（`AGENOTEs/VPs/{version}/`）；CLAUDE.md 欄位與 VP frontmatter 不一致時，**以 VP frontmatter 的 `status` 為準**（資料夾內的檔案是真相，本區塊只是指標）。

工作線與任務支線的活躍狀態以 `AGENOTEs/WORK-INDEX.md` 為準；NOTE/PAPER/PLAN 是脈絡與決策來源，不直接代表可執行工作。

| 狀態 | 模式 | 讀取 |
|------|------|------|
| 版本狀態 = sealed，或無進行中版本 | 一般對話／新版規劃 | 不開 WN。新版規劃走 claude-skills `AGENOTEs/agenote-cvp.md`（先跑 `AGENOTEs/agenote-session.md` 脈絡恢復），必讀「最近封版」VP 的「技術債與下一版方向」區 |
| 版本狀態 = planning（VP 已建、WN 未齊） | AGENOTE 規劃（續建 WN） | claude-skills `AGENOTEs/agenote-cvp.md`（先跑脈絡恢復） |
| 版本狀態 = execution 且 WN 有未完成任務 | Worker 執行 | 下方版本狀態的 WN 路徑 + WN 頂部必讀清單；規則見 claude-skills `AGENOTEs/agenote-worker.md` |
| 版本狀態 = execution 且 WN 全部完成 | 提示封版 | claude-skills `AGENOTEs/agenote-release.md` |

## 版本狀態

| 項目 | 內容 |
|------|------|
| 當前版本 | v0.8.0 |
| VP 路徑 | `AGENOTEs/VPs/v0.8.0/VP.md`（main）|
| WN 路徑 | `AGENOTEs/VPs/v0.8.0/WN1.md` |
| 版本狀態 | execution（WN1 兩項任務程式碼已完成並通過離線驗證，見 VP「PM 驗收」；真實 GitHub API 呼叫待下次心跳確認後可提報封版）|
| 最近封版 | v0.7.0（`AGENOTEs/VPs/v0.7.0/VP.md`）|
| 最後更新 | 2026-07-09 |

維護責任：agenote-cvp 建立 WN 後更新；agenote-release 封版後更新。

## 上層文件（指導文件）

規劃寫 VP 時的依據；封版時逐項核對是否需更新。

| 文件 | 位置 | 讀取時機 |
|------|------|---------|
| 共用工具 skill 索引 | claude-skills 根目錄 `skills.md`（跨 repo） | 建 VP/WN 任務前，確認有無現成可重用工具 skill |
| 系統架構與現況說明 | `OVERVIEW.md` | 規劃任何版本必讀 |
| 代理身份與使命 | `core/MOTIVE.md` | 涉及行為規則、決策邏輯異動時必讀 |
| 好奇極追蹤機制 | `core/HORIZON.md` | 涉及 crystallize/dissolve 或好奇極相關開發時 |
| 版本方向與歷程總覽 | `_docs/strategy/ROADMAP.md` | 版本定位不明時 |
| 起點與早期發展紀錄（至 v0.2.2） | `PAPER11.md` | 涉及專案起源、動機論命題背景時參考 |
| 架構演進與三次迴圈診斷（v0.3.0–v0.4.0） | `PAPER12.md` | 涉及自我修改機制、moticore.org 建置、迴圈問題根因時參考 |
| 第四次迴圈與部署凍結根因診斷 | `PAPER13.md` | 涉及 HORIZON 生命週期、部署管線問題時參考 |
| 太極動機架構決策（雙極設計緣起） | `_docs/papers/PAPER1.md` | 涉及 pole（motivation/curiosity/crystallize/dissolve）機制設計時參考 |

---

## 分支規則

- **程式碼變更**：feature branch → PR → merge main
- **版本文件（VP / WN）**：直接建立在 main，不使用 feature branch
- 目前無進行中的 feature branch

---

## 文件導航

| 需要知道 | 去哪裡找 |
|---------|----------|
| 當前版本 / VP 路徑 | 本文件版本狀態區塊（上方）|
| 版本方向 / 下一步 | `_docs/strategy/ROADMAP.md` |
| 各版本覆盤與計畫書 | `AGENOTEs/VPs/<版本號>/` |
| 架構決策與根因分析 | `PAPER11.md`、`PAPER12.md`、`PAPER13.md` |
| 系統架構與規劃 | `OVERVIEW.md` |
| 代理身份與使命 | `core/MOTIVE.md` |
| 當前任務 | `core/STATUS.md` |
| 行動歷史 | `memory/action-log.md` |
| 閱讀進度 | `memory/reading-cursor.json` |
| 閱讀筆記 | `notes/` |

---

## 作業節奏（強制）

每完成一個獨立工作單元後，立即 push 並確認成功，才繼續下一個。

| 任務類型 | 一個單元的定義 |
|---------|---------------|
| 程式碼修復 | 一個功能點 |
| 文件更新 | 一個文件 |
| MOTIVE.md 修改 | 整份文件（不分段 push）|

**禁止：** 讀 N 個 → 改 N 個 → 一起 push
**正確：** 讀一個 → 改一個 → push → 確認成功 → 下一個

---

## 修改前先讀 SHA

使用 `mcp__github__get_file_contents` 讀取檔案時，回傳的 SHA 就是更新時必須提供的 `sha` 參數。讀完立刻更新，不要在讀取和更新之間穿插其他操作（避免 SHA 過期）。

---

## 禁止行為

- 不得直接 push 到 `main`（程式碼變更）；版本文件除外
- 不得在未讀取 STATUS.md 的情況下宣稱已掌握任務狀態
- 不得在未驗證的情況下宣告修復完成
