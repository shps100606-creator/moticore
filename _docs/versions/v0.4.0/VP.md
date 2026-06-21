# v0.4.0 Main VP — moti 感知世界的回饋

> PM 使用文件。Worker 不直接修改本文件，執行細節寫入 WN。

---

## 版本狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.4.0
- **目前角色**：PM
- **目前階段**：execution
- **目前步驟**：Step 5 — WN 已建立，等待 Worker 執行
- **下一步**：Worker 執行 WN1（後端）、WN2（前端 + 身份），PM 驗收
- **禁止前進條件**：WN1 / WN2 任一 blocked 未處理前不進入 Release
- **WN 文件**：WN1.md（後端：迴圈偵測 + Analytics）、WN2.md（前端：Giscus + MOTIVE.md）
- **版本摘要**：（封版時填）

---

## 接手閱讀清單

### 固定文件

- [x] `CVP.md`（含 § 二 全局 SOP）
- [x] `CLAUDE.md`
- [x] `PAPER12.md`（本版種子，替代上一版 VP）

### 決策記錄

- [x] PAPER12.md § 四（三次迴圈教訓）
- [x] PAPER12.md § 六（演進方向，v0.4.0 機制定義來源）

### 專案相關文件

- [x] `.github/workflows/heartbeat.yml`
- [x] `agent/preprocessor.py`
- [x] `memory/action-log.md`（最近 100 次心跳確認迴圈狀態）
- [x] `web/content/posts/`（確認目前發文狀態）

---

## PM 情報筆記

### 專案現況（截至 2026-06-21）

| 項目 | 狀態 |
|------|------|
| 心跳頻率 | 每 30 分鐘（雙 cron，穩定） |
| 最新心跳 | 2026-06-21T09:37:17Z — 「確認網站啟動狀態，並將存在實驗室的運作邏輯納入日常心跳」|
| moti 當前模式 | SYNTHESIS — 自由探索 + 網站經營 |
| 迴圈問題 | 第三次（「等待審核」06-16 至 06-21，~100 次心跳）今日已修復 |
| 修復內容 | MOTIVE.md 加入 moticore.org 所有權 + STATUS.md 中斷等待語義 |
| 網站發文現況 | `web/content/posts/`：2 篇（existence-lab-001.md、welcome.md）|
| v0.3.1 狀態 | 事實上已完成（moti 今日成功發文），無需獨立封版，直接進入 v0.4.0 |

### 關鍵技術現況

**heartbeat.yml 環境變數：**
```
GOOGLE_API_KEY     ← Gemini 呼叫
GITHUB_TOKEN       ← Issues + commit
DIALOGUES_TOKEN    ← prima-materia 原典讀取
WP_USER / WP_APP_PASSWORD  ← WordPress（備用，現以 §FILE 為主）
```
⚠️ **VERCEL_TOKEN 尚未加入 heartbeat.yml**（M3 的前提，Worker 執行前需確認 secret 是否已存在於 repo settings）

**preprocessor.py 目前能力：**
- Layer 1：MOTIVE.md 全文
- Layer 2：時間、模式、進度、緊急事項、最近行動、STATUS.md、文件樹
- Layer 3：閱讀原文 / Issue 回應 / 知識綜合（依模式切換）
- Layer 4：筆記摘要
- ❌ 無迴圈偵測
- ❌ 無 Analytics 注入

**action-log.md 結構：**
每筆含 `summary` 欄位 → 可用來比對最近 N 次心跳是否重複。

### 已知限制

| 限制 | 說明 |
|------|------|
| agent/ 不可被 moti 修改 | 但我們（Claude Code worker）可以修改 |
| VERCEL_TOKEN 需確認 | heartbeat.yml 目前沒有此變數，需手動加入 repo secrets 並更新 yml |
| Giscus 需 GitHub Discussions 開啟 | 需在 repo settings 啟用 Discussions |
| moti 無法感知讀者 | Giscus 上線後 moti 需透過 §READ_REQUEST 讀取留言，MOTIVE.md 需更新告知 |

### 初步風險

| 風險 | 機率 | 影響 | 緩解 |
|------|------|------|------|
| Vercel Analytics API 格式不符 | 低 | 中 | Worker 先用 dummy data 驗證注入邏輯 |
| Giscus 設定錯誤導致留言無法載入 | 低 | 低 | 前端錯誤不影響 moti 運作 |
| 迴圈偵測閾值設太嚴 | 中 | 中 | 保守設定（5 次完全相同才警告），後續可調整 |
| MOTIVE.md 更新引發 moti 行為改變 | 中 | 中 | 僅加入機制說明，不改動使命或禁止規則 |

---

## 訪問紀錄

**代理初步判斷（PM）**：
M1（迴圈偵測）+ M2（Giscus）+ M3（Analytics）可一次實作，技術上獨立，風險可控。M4-M6 屬架構層級，留後續版本。

**使用者確認**：
> 「要把 paper12 預計的新增機制寫進去」
> 「有啊，不然現在 moti 怎麼運作的」（確認 Vercel token 可取得）

**最終共識**：
本版實作 M1 + M2 + M3（PAPER12 § 六 v0.4.0 全部機制）。
M4（自主開 Issue）、M5（外部 URL）、M6（多代理）留 v0.5.0。

---

## 需求與邊界

- **確認需求**：
  1. M1 迴圈自動偵測：preprocessor Layer 2 加入最近 5 次 summary 比對，相似度過高時顯示 ⚠️ 警告
  2. M2 Giscus 讀者留言：`web/` 文章頁加入 Giscus 元件；MOTIVE.md 告知 moti 可用 §READ_REQUEST 讀取 Discussions 留言
  3. M3 Vercel Analytics 流量感知：heartbeat 執行前抓取訪客數 + 熱門文章，注入 Layer 2

- **不做事項**：M4-M6；不動 Gemini 呼叫邏輯；不改 decision.py 的輸出格式

- **前提**：
  - M3 前提：VERCEL_TOKEN 存在於 repo secrets，Worker 執行前必須確認
  - M2 前提：moticore repo 的 GitHub Discussions 功能已啟用（或 Worker 執行時確認並說明啟用方式）

- **風險**：見 PM 情報筆記 → 初步風險

- **驗收標準**：
  - M1：人工模擬 5 次相同 summary → Layer 2 出現警告文字
  - M2：moticore.org 文章頁面顯示 Giscus 留言框；MOTIVE.md 含機制說明
  - M3：heartbeat 執行後 Layer 2 含 Analytics 區塊（即使數字為 0）

---

## 版本規劃

### 目標

讓 moti 從「只能輸出」進化為「能感知部分回饋」：
- 感知自身行為模式（迴圈偵測）
- 感知讀者互動（Giscus 留言）
- 感知網站流量（Analytics）

### 方案

| 機制 | 實作位置 | 說明 |
|------|----------|------|
| M1 迴圈偵測 | `agent/preprocessor.py` | 讀 action-log.md 最近 5 筆 summary，若 ≥4 筆相同則 Layer 2 加 ⚠️ 警告 |
| M2 Giscus | `web/components/GiscusComments.vue` + `web/pages/posts/[...slug].vue` | 嵌入 Giscus 留言框；MOTIVE.md 加入感知說明 |
| M3 Analytics | `agent/preprocessor.py`（新增 `_fetch_analytics()`）+ `heartbeat.yml` | 執行前抓 Vercel Analytics API，注入 Layer 2 |

### 不採用方案

- WordPress 整合（已廢棄）
- 爬取 moticore.org 頁面（間接且不穩定）
- 在 decision.py 層加感知（職責分離，感知應在 preprocessor）

### 工作批次

| 批次 | 內容 | 產出 | 狀態 |
|------|------|------|------|
| B1 後端 | M1 迴圈偵測 + M3 Analytics（preprocessor + heartbeat） | preprocessor.py 更新、heartbeat.yml 更新 | planning |
| B2 前端 + 身份 | M2 Giscus 元件 + MOTIVE.md 更新 | GiscusComments.vue、slug.vue 更新、MOTIVE.md 更新 | planning |

---

## 任務分配摘要

| 任務ID | 屬性 | 重要性 | 任務 | WN 位置 | 狀態 | PM 驗收 |
|--------|------|--------|------|---------|------|----------|
| WN1-1 | PJ | CR | M1：preprocessor 迴圈偵測（最近 5 筆 summary 比對，Layer 2 警告） | `WN1.md#WN1-1` | open | |
| WN1-2 | PJ | CR | M3：preprocessor 新增 `_fetch_analytics()` + Layer 2 注入 | `WN1.md#WN1-2` | open | |
| WN1-3 | PJ | CR | M3：heartbeat.yml 加入 VERCEL_TOKEN + VERCEL_PROJECT_ID 環境變數 | `WN1.md#WN1-3` | open | |
| WN2-1 | PJ | PR | M2：建立 `GiscusComments.vue` 元件 + 嵌入文章頁 | `WN2.md#WN2-1` | open | |
| WN2-2 | PJ | CR | M2：MOTIVE.md 加入 Giscus 感知說明（moti 知道可用 §READ_REQUEST 讀 Discussions） | `WN2.md#WN2-2` | open | |

---

## 涉及文件清單

| 文件名稱 | 路徑 | 預定動作 | 實際動作 | 驗證狀態 | 補修 / 備註 |
|----------|------|----------|----------|----------|-----------|
| `VP.md` | `_docs/versions/v0.4.0/VP.md` | 新建 | ✅ 新建 | — | 本文件 |
| `WN1.md` | `_docs/versions/v0.4.0/WN1.md` | 新建 | | | 後端任務 |
| `WN2.md` | `_docs/versions/v0.4.0/WN2.md` | 新建 | | | 前端 + 身份任務 |
| `preprocessor.py` | `agent/preprocessor.py` | 更新 | | | M1 + M3 |
| `heartbeat.yml` | `.github/workflows/heartbeat.yml` | 更新 | | | M3 環境變數 |
| `GiscusComments.vue` | `web/components/GiscusComments.vue` | 新建 | | | M2 |
| `[...slug].vue` | `web/pages/posts/[...slug].vue` | 更新 | | | 嵌入 Giscus |
| `MOTIVE.md` | `core/MOTIVE.md` | 更新 | | | M2 感知說明 |

---

## PM 驗收

（Worker 完成後填入）

| 任務ID | Worker 結果 | PM 驗收 | 落差 | 處理 |
|--------|-------------|---------|------|------|
| WN1-1 | | | | |
| WN1-2 | | | | |
| WN1-3 | | | | |
| WN2-1 | | | | |
| WN2-2 | | | | |

### WN 吸收狀態

| 項目 | 狀態 | 說明 |
|------|------|------|
| Worker 完成內容已吸收回 VP | ⬜ | |
| 驗證結果已吸收回 VP | ⬜ | |
| blocked / review 項目已處理 | ⬜ | |
| 技術債已寫入 VP | ⬜ | |

---

## 品質評估

（封版時填）

| 指標 | 結果 | 備註 |
|------|------|------|
| M1 迴圈偵測邏輯驗證 | 未測 | |
| M2 Giscus 前端顯示 | 未測 | |
| M3 Analytics 注入 | 未測 | |
| CI / GitHub Actions heartbeat | 未測 | |
| Vercel 部署 | 未測 | |

**已知問題**：
- VERCEL_TOKEN 需在 repo settings → Secrets 確認或新增
- GitHub Discussions 需在 repo settings 確認已啟用（Giscus 依賴）

---

## 技術債與下一版方向

| 技術債 / 下一步 | 類型 | 優先級 | 建議處理版本 |
|-----------------|------|--------|-------------|
| M4：§QUESTION 放寬，允許 moti 主動開 Issue 分享洞見 | 功能 | P1 | v0.5.0 |
| M5：§READ_REQUEST 支援外部 URL | 功能 | P1 | v0.5.0 |
| M6：多代理對話架構 | 架構 | P3 | v0.6.0+ |
| §WP_POST 清理（decision.py、run.py WordPress 相關程式碼）| 清理 | P2 | v0.4.x |
| action-log.md 長期管理（目前無截斷機制，會無限增長）| 技術債 | P2 | v0.5.0 |

**給下一個 PM 的提示**：
v0.4.0 完成後，moti 已有迴圈偵測 + 讀者感知。下一版重點是讓 moti 更主動：M4 讓他能主動開 Issue 表達洞見，M5 讓他能讀外部資料。
注意：MOTIVE.md 是最高層級文件，改動前評估行為影響。

---

## 覆盤

（封版時填）

---

## 決策記錄判斷

| 項目 | 狀態 | 說明 |
|------|------|------|
| 是否需要寫決策記錄 | ⬜ | 封版後判斷 |
| 決策記錄已撰寫並推送 | ⬜ / N/A | |

---

## Release 封版確認

（Release session 執行）

### WN 處理

| WN 文件 | WN 回報已被 PM 吸收 | 處理方式 | 狀態 |
|---------|---------------------|----------|------|
| WN1.md | ⬜ | 刪除 / 壓縮歸檔 | ⬜ |
| WN2.md | ⬜ | 刪除 / 壓縮歸檔 | ⬜ |

### 文件

| 文件 | 本版有變動？ | 已更新？ |
|------|-------------|----------|
| `CLAUDE.md` | 否 | N/A |
| `ROADMAP.md` | 是 | ⬜ |
| `PAPER12.md` 或 PAPER13.md | 是（若需記錄） | ⬜ |

### Git / 驗證

| 項目 | 狀態 |
|------|------|
| 所有必要變更已 commit | ⬜ |
| CI heartbeat 綠燈確認 | ⬜ |
| Vercel 部署確認 | ⬜ |
| Tag（等使用者確認）| ⬜ |
