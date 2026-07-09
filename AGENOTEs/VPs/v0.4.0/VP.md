# v0.4.0 Main VP — moti 感知世界的回饋

> PM 使用文件。Worker 不直接修改本文件，執行細節寫入 WN。

---

## 版本狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.4.0
- **目前角色**：PM → Released
- **目前階段**：✅ Released
- **封版時間**：2026-06-21
- **Merge commit**：`f3f90be656c880dba5383eaf21cd83762a7156f2`（PR #35 → main）
- **WN 文件**：WN1.md（已吸收，刪除）、WN2.md（已吸收，刪除）
- **版本摘要**：M1 迴圈偵測 + M2 Giscus（前端 + 後端 + 身份）+ M3 Analytics，共 6 個子任務全數完成；創造者手動完成 Discussions 啟用、Giscus 設定、VERCEL_TOKEN / VERCEL_PROJECT_ID 四項設定。

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

**heartbeat.yml 環境變數（v0.4.0 後）：**
```
GOOGLE_API_KEY     ← Gemini 呼叫
GITHUB_TOKEN       ← Issues + commit + Discussions fetch
DIALOGUES_TOKEN    ← prima-materia 原典讀取
WP_USER / WP_APP_PASSWORD  ← WordPress（備用）
VERCEL_TOKEN       ← Analytics API（WN1-3 新增）✅ 已設定
VERCEL_PROJECT_ID  ← Analytics API（WN1-3 新增）✅ 已設定
```

**preprocessor.py v0.4.0 能力：**
- Layer 1：MOTIVE.md 全文
- Layer 2：時間、模式、進度、緊急事項、最近行動、STATUS.md、文件樹 + **Vercel Analytics** + **迴圈偵測警告**
- Layer 3：閱讀原文 / Issue 回應 / 知識綜合（依模式切換）
- Layer 4：筆記摘要
- ✅ M1 迴圈偵測：`_parse_recent_summaries()` + `_layer2_status()` 警告（≥4/5 相同 summary）
- ✅ M3 Analytics：`_fetch_analytics()` 呼叫 Vercel API，注入 Layer 2

**[WN 建立時發現]** WN1-4 為必要新增任務：Giscus 的讀者留言存在於 GitHub Discussions，需後端持續抓取並寫入 `memory/giscus-comments.md`，moti 才能透過 §READ_REQUEST 讀取。

### 已知限制（封版時狀態）

| 限制 | 狀態 |
|------|------|
| agent/ 不可被 moti 修改 | 持續有效（保護機制） |
| VERCEL_TOKEN | ✅ 已由創造者設定 |
| VERCEL_PROJECT_ID | ✅ 已由創造者設定（`prj_kL5Bq9AYA9GSZMveeoaaWUtf1P9Y`） |
| GitHub Discussions | ✅ 已由創造者啟用 |
| GiscusComments.vue PLACEHOLDER | ✅ 已填入（data-repo-id: R_kgDOSZ-Dng；category: Announcements） |

### 初步風險（封版時狀態）

| 風險 | 結果 |
|------|------|
| Vercel Analytics API 格式不符 | 待首次心跳驗證；graceful degradation 已就位 |
| Giscus 設定錯誤 | 已填入正確 ID，預期正常 |
| 迴圈偵測閾值 | 保守設定（≥4/5），上線後觀察 |
| MOTIVE.md 更新影響行為 | 僅加說明，使命未動 |
| GitHub Discussions 未啟用 | ✅ 已啟用 |

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
  2. M2 Giscus 讀者留言：`web/` 文章頁加入 Giscus 元件；WN1-4 後端持續抓取 Discussions 寫入 memory/；MOTIVE.md 告知 moti
  3. M3 Vercel Analytics 流量感知：heartbeat 執行前抓取訪客數 + 熱門文章，注入 Layer 2

- **不做事項**：M4-M6；不動 Gemini 呼叫邏輯；不改 decision.py 的輸出格式

- **驗收標準（結果）**：
  - M1 ✅：邏輯驗證通過；首次心跳後自然驗證
  - M2 ✅：Giscus 元件上線；MOTIVE.md 更新；Discussions fetch 就位
  - M3 ✅：Analytics 注入邏輯完成；首次心跳後以真實 token 驗證

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
| M2 Giscus 前端 | `web/components/GiscusComments.vue` + `web/pages/posts/[...slug].vue` | 嵌入 Giscus 留言框 |
| M2 Giscus 後端 | `agent/issues.py` + `agent/run.py` | 持續抓取 Discussions 寫入 `memory/giscus-comments.md` |
| M2 身份 | `core/MOTIVE.md` | 加入 Giscus 感知說明 |
| M3 Analytics | `agent/preprocessor.py`（新增 `_fetch_analytics()`）+ `heartbeat.yml` | 執行前抓 Vercel Analytics API，注入 Layer 2 |

### 工作批次

| 批次 | 內容 | 產出 | 狀態 |
|------|------|------|------|
| B1 後端 | M1 迴圈偵測 + M3 Analytics + M2 Discussions fetch（WN1） | preprocessor.py、run.py、issues.py、heartbeat.yml | done |
| B2 前端 + 身份 | M2 Giscus 元件 + MOTIVE.md（WN2） | GiscusComments.vue、slug.vue、MOTIVE.md | done |

---

## 任務分配摘要

| 任務ID | 屬性 | 重要性 | 任務 | WN 位置 | 狀態 | PM 驗收 |
|--------|------|--------|------|---------|------|----------|
| WN1-1 | PJ | CR | M1：preprocessor 迴圈偵測（最近 5 筆 summary 比對，Layer 2 警告） | `WN1.md#WN1-1` | done | ✅ 通過 |
| WN1-2 | PJ | CR | M3：preprocessor `_fetch_analytics()` + Layer 2 注入 + run.py 傳參 | `WN1.md#WN1-2` | done | ✅ 通過 |
| WN1-3 | PJ | CR | M3：heartbeat.yml 加入 VERCEL_TOKEN + VERCEL_PROJECT_ID | `WN1.md#WN1-3` | done | ✅ 通過 |
| WN1-4 | PJ | PR | M2：issues.py `fetch_discussions()` + run.py 寫入 memory/giscus-comments.md | `WN1.md#WN1-4` | done | ✅ 通過 |
| WN2-1 | PJ | PR | M2：建立 `GiscusComments.vue` 元件 + 嵌入文章頁 | `WN2.md#WN2-1` | done | ✅ 通過 |
| WN2-2 | PJ | CR | M2：MOTIVE.md 加入 Giscus 感知說明 | `WN2.md#WN2-2` | done | ✅ 通過 |

---

## 涉及文件清單

| 文件名稱 | 路徑 | 預定動作 | 實際動作 | 驗證狀態 | 補修 / 備註 |
|----------|------|----------|----------|----------|-----------|
| `VP.md` | `_docs/versions/v0.4.0/VP.md` | 新建 | ✅ 新建 | ✅ | |
| `WN1.md` | `_docs/versions/v0.4.0/WN1.md` | 新建 | ✅ 新建→刪除 | ✅ | PM 吸收後刪除 |
| `WN2.md` | `_docs/versions/v0.4.0/WN2.md` | 新建 | ✅ 新建→刪除 | ✅ | PM 吸收後刪除 |
| `preprocessor.py` | `agent/preprocessor.py` | 更新 | ✅ 更新 | ✅ | M1 + M3；新增 `_parse_recent_summaries()`、`_fetch_analytics()` |
| `run.py` | `agent/run.py` | 更新 | ✅ 更新 | ✅ | VERCEL_TOKEN/PROJECT_ID 傳參 + Discussions 寫入 |
| `issues.py` | `agent/issues.py` | 更新 | ✅ 更新 | ✅ | `fetch_discussions()` via GraphQL |
| `heartbeat.yml` | `.github/workflows/heartbeat.yml` | 更新 | ✅ 更新 | ✅ | VERCEL_TOKEN + VERCEL_PROJECT_ID env vars |
| `GiscusComments.vue` | `web/components/GiscusComments.vue` | 新建 | ✅ 新建 | ✅ | ID 已填入 |
| `[...slug].vue` | `web/pages/posts/[...slug].vue` | 更新 | ✅ 更新 | ✅ | `<GiscusComments />` 加入 article-body 後 |
| `MOTIVE.md` | `core/MOTIVE.md` | 更新 | ✅ 更新 | ✅ | 操作邊界末尾加入 Giscus 感知說明一行 |
| `memory/giscus-comments.md` | `memory/giscus-comments.md` | 程式寫入 | 待心跳執行 | — | 有留言時才由 run.py 寫入 |

---

## PM 驗收

| 任務ID | Worker 結果 | PM 驗收 | 落差 | 處理 |
|--------|-------------|---------|------|------|
| WN1-1 | 新增 `_parse_recent_summaries()`；修改 `_layer2_status()` 加入迴圈警告；5 種情境全過 | ✅ 通過 | 無 | — |
| WN1-2 | 新增 `_fetch_analytics()`；修改 `_layer2_status()` / `build_newspaper()` 注入 Analytics；graceful degradation 全路徑 | ✅ 通過 | API schema 待真實 token 驗證 | 接受；首次心跳後確認 |
| WN1-3 | heartbeat.yml env 加入兩個 VERCEL_* vars；YAML 正確 | ✅ 通過 | 無 | — |
| WN1-4 | `fetch_discussions()` via GraphQL；空結果不寫檔；全路徑 graceful | ✅ 通過 | 無 | — |
| WN2-1 | `GiscusComments.vue` 新建（SSR 安全）；slug.vue 加入元件；ID 已填入 | ✅ 通過 | 無 | — |
| WN2-2 | MOTIVE.md 操作邊界末尾加入 Giscus 感知說明；其他段落未動 | ✅ 通過 | 無 | — |

### WN 吸收狀態

| 項目 | 狀態 |
|------|------|
| Worker 完成內容已吸收回 VP | ✅ |
| 驗證結果已吸收回 VP | ✅ |
| blocked / review 項目已處理 | ✅ 無 blocked |
| 技術債已寫入 VP | ✅ |

---

## 品質評估

| 指標 | 結果 | 備註 |
|------|------|------|
| M1 迴圈偵測邏輯驗證 | ✅ 通過（邏輯審查） | 首次心跳後自然驗證 |
| M2 Giscus 前端 | ✅ 上線 | ID 已填入，Discussions 已啟用 |
| M2 Discussions fetch | ✅ 就位 | 有留言時下次心跳自然驗證 |
| M3 Analytics 注入 | ✅ 就位 | 首次心跳後以真實 token 驗證 |
| CI / GitHub Actions heartbeat | ⬜ 待首次心跳 | merge 後下次排程執行時確認 |
| Vercel 部署 | ✅ 已觸發 | PR #35 merge → 自動部署 |

---

## 技術債與下一版方向

| 技術債 / 下一步 | 類型 | 優先級 | 建議處理版本 |
|-----------------|------|--------|-------------|
| M4：§QUESTION 放寬，允許 moti 主動開 Issue 分享洞見 | 功能 | P1 | v0.5.0 |
| M5：§READ_REQUEST 支援外部 URL | 功能 | P1 | v0.5.0 |
| M6：多代理對話架構 | 架構 | P3 | v0.6.0+ |
| §WP_POST 清理（decision.py、run.py WordPress 相關程式碼）| 清理 | P2 | v0.4.x |
| action-log.md 長期管理（目前無截斷機制，會無限增長）| 技術債 | P2 | v0.5.0 |
| Vercel Analytics 閾值可調（目前 ≥4，可考慮 ≥3）| 微調 | P3 | v0.5.0 |

**給下一個 PM 的提示**：
v0.4.0 完成後，moti 已有迴圈偵測 + 讀者感知。下一版重點是讓 moti 更主動：M4 讓他能主動開 Issue 表達洞見，M5 讓他能讀外部資料。注意：MOTIVE.md 是最高層級文件，改動前評估行為影響。

---

## 覆盤

**整體評估**：順利。6 個子任務全數完成，無 blocked，無技術債新增。

**做得好的地方**：
- WN 建立階段發現 Giscus Discussions 需要後端 fetch 機制（WN1-4），及時補入 VP，未遺漏。
- 所有機制均有 graceful degradation，上線後即使 API 不可用也不影響心跳。
- 創造者手動待辦（Discussions / Giscus / Secrets）在同一 session 內全數完成，未跨 session 拖延。

**可改進的地方**：
- Vercel Analytics API response schema 未以真實 token 預先驗證，需觀察首次心跳。
- PAPER12.md 定義了 M4-M6，但本版僅做 M1-M3；若下一個 PM 未讀 PAPER12，可能不清楚 M4-M6 的設計意圖。建議 v0.5.0 VP 開頭明確引用。

**第三次迴圈危機後記**：
v0.4.0 的直接觸發原因是第三次大迴圈（~100 次心跳陷入「等待審核」）。M1 迴圈偵測上線後，同等規模的迴圈在第 4 次心跳即可被 moti 自我察覺。這是本版最重要的防護機制。

---

## 決策記錄判斷

| 項目 | 狀態 | 說明 |
|------|------|------|
| 是否需要寫決策記錄 | 不需要 | 本版無架構轉向；PAPER12 已完整記錄設計意圖與三次迴圈教訓 |
| 決策記錄已撰寫並推送 | N/A | |

---

## Release 封版確認

### WN 處理

| WN 文件 | WN 回報已被 PM 吸收 | 處理方式 | 狀態 |
|---------|---------------------|----------|------|
| WN1.md | ✅ | 刪除 | ✅ 已刪除 |
| WN2.md | ✅ | 刪除 | ✅ 已刪除 |

### 文件

| 文件 | 本版有變動？ | 已更新？ |
|------|-------------|----------|
| `CLAUDE.md` | 否 | N/A |
| `ROADMAP.md` | 是 | ⬜ 待更新 |
| `PAPER12.md` 或新 PAPER | 否 | N/A |

### Git / 驗證

| 項目 | 狀態 |
|------|------|
| 所有必要變更已 commit | ✅ |
| PR #35 merged to main | ✅ 2026-06-21（commit: f3f90be） |
| Vercel 部署 | ✅ 已觸發（merge → 自動部署） |
| CI heartbeat 首次執行 | ⬜ 待下次排程（最多 30 分鐘） |
| Tag v0.4.0 | ⬜ 待創造者確認是否需要 |
| ROADMAP.md 更新 | ⬜ 待本 session 結束前完成 |
