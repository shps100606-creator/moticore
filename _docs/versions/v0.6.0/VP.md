# v0.6.0 Main VP — 太極自動化：結晶 / 溶解機制（實際範圍已擴大）

---

## 版本狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.6.0
- **目前角色**：Release
- **目前階段**：released
- **目前步驟**：Step 9 — Release（本次補建）
- **下一步**：觀察 crystallize/dissolve 是否被實際觸發，並開始 v0.7.0
- **禁止前進條件**：無
- **WN 文件**：無（本版全程單一 session 完成，PM 與 Worker 為同一代理、無 context 斷裂，依 CVP 零、核心設計原則不建 WN）
- **版本摘要**：修復「moti 一篇文都沒發」——根因是 Vercel 部署被靜默凍結兩週；同時修好讓 moti 陷入迴圈的真正原因（HORIZON.md 從未清空），並補上一個被默默丟棄兩個月的欄位 bug。

---

## 版本定性

原始種子只設定「太極自動化：結晶/溶解機制」。實際執行時，使用者在同一輪對話中追加了另外兩個獨立問題（發文排程、moticore.org 完全沒有更新），三者一起在本版處理完畢。範圍比種子設定的更廣，這是回溯（retroactive）補建 VP 時如實記錄，不是規劃失誤——CVP 的 VP 是狀態快照，不是事前合約。

**本版實際包含四個工作批次，詳見「版本規劃」。**

---

## 接手閱讀清單

- [x] `CVP.md`
- [x] `CVPs/cvp_skills.md`
- [x] `CLAUDE.md` → CVP 狀態區塊
- [x] v0.5.0 VP 的技術債段（無，v0.5.0 覆盤本身缺失，詳見「已知限制」）
- [x] `PAPER12.md`（三次迴圈與 moticore.org 建置歷史）

---

## PM 情報筆記

### 專案現況

moti 自 2026-06-21 首次發文後，`web/content/posts/` 只有一篇文章，之後十天沒有任何新文章。使用者詢問「moti 到底什麼時候才會發文」啟動本輪調查。

### 相關文件摘要

- `core/HORIZON.md` 從 6/23 起固定 4 個開放問題，`memory/action-log.md` 顯示 moti 反覆在其中 3 題間探索。
- `agent/decision.py` 的 SYNTHESIS 模式指示只允許寫 2 個 `§FILE`（反思筆記 + STATUS.md），從未指示寫入 `web/`。
- `vercel.json` 有自訂 `ignoreCommand`，語意上應該只在 `web/` 有變動時建置。

### 已知限制

- v0.5.0 沒有留下完整的覆盤或 VP 封版紀錄（CLAUDE.md 直接標成 sealed，`_docs/versions/v0.5.0/VP.md` 內容未經本次核實），`_docs/strategy/ROADMAP.md` 甚至仍標示 v0.5.0「🚧 進行中」——文件與實際狀態長期不同步。經比對程式碼，v0.5.0 規劃的 T7（外部 URL）、T8（action-log 截斷）、T9（移除 §WP_POST）三項技術債**實際上已經在 main 完成**，只是 ROADMAP 從未更新勾選。本版順手補上這個同步。
- 專案存在三個未合併的 `feat/v0.5.0-*` 分支（external-url、pole-insight-cleanup、preprocessor-pole-balance），內容疑似與已經在 main 上的程式碼重複；本版未深入清查，列為技術債。

### 初步風險

發文排程與 HORIZON 生命週期都涉及修改 `agent/*.py`，屬於 moti 每次心跳都會執行的核心路徑，任何邏輯錯誤會直接影響下一次心跳。以本地 `py_compile` 與手寫測試腳本驗證邏輯後才推送，降低風險。

---

## 訪問紀錄

**代理初步判斷**：一開始懷疑是 moti 陷入反思迴圈導致不發文；深入後發現迴圈是真的，但「一篇都沒發」還有第二層更關鍵的原因（部署凍結），是使用者親自去看 Vercel Dashboard 才浮現的。

**使用者確認 / 修正**：
- 留言區：不做直接回貼，維持「讀取 Giscus 留言 + 寫文章回應」。
- 發文頻率：不是每次心跳都發，改成一天固定三個時段（晨/午/晚）。
- 迴圈根因確認後，授權補上 crystallize/dissolve 的強制畢業機制。
- 部署凍結找到 `ignoreCommand` 這個嫌疑後，使用者親自到 Vercel Dashboard 確認「6/15 之後完全沒有部署紀錄」，坐實根因。

**最終共識**：四個工作批次都在本版一次做完，且已於本版內完成 Release 補建。

---

## 需求與邊界

- **確認需求**：(1) moti 每天固定時段發文；(2) HORIZON.md 的 crystallize/dissolve 要真的發生，不能只是宣稱；(3) 修復 moticore.org 完全沒有更新的問題；(4) 補建本版 CVP 文件。
- **不做事項**：不做 Giscus 留言直接回貼；不重新規劃 v0.5.0 技術債分支（`feat/v0.5.0-*`）的去留，只記錄為技術債。
- **前提**：agent/ 目錄修改必須走 feature branch → PR → merge main；VP/ROADMAP/CLAUDE.md/PAPER 直接建立在 main。
- **風險**：`check_horizon_lifecycle()` 與發文排程機制截至封版時都只被觀察到一部分行為（發文排程已驗證正常運作；crystallize/dissolve 尚未被實際觸發）。
- **驗收標準**：moticore.org 顯示所有 §JOURNAL 貼文；`memory/action-log.md` 的 `action_type`/`deviation_flag` 顯示真實值而非預設值。

---

## 版本規劃

### 目標

讓 moti 的內部狀態（反思、決策）能可靠地變成外部可見的結果（公開發文、HORIZON.md 真的被清空），並修復阻擋這一切的部署管線。

### 方案

四個工作批次獨立處理，各自開 feature branch → PR → merge main；不建 WN，PM（同一代理）直接兼任 Worker 執行。

### 不採用方案

- 曾考慮讓 moti 在 Giscus 留言串直接回貼（需要新增 GraphQL mutation + workflow 權限），使用者選擇維持現狀，改用「文章回應」模式，降低本版風險與範圍。

### 工作批次

| 批次 | 內容 | 產出 | 狀態 |
|------|------|------|------|
| B1 | 固定三時段強制發文機制 | `agent/decision.py`（§JOURNAL）、`agent/run.py`（排程守門 + fallback）、`agent/preprocessor.py`（journal_note 注入）| done |
| B2 | HORIZON.md 開放中→已結晶生命週期強制化 | `agent/decision.py`（規則 11–13）、`agent/run.py`（`check_horizon_lifecycle()`）、`agent/preprocessor.py`（開放題數提醒）、`core/HORIZON.md`（示範畢業一項）、`core/MOTIVE.md`（行動憲法補充）| done |
| B3 | `memory.py` 欄位命名不符 bug 修正 | `agent/memory.py`（`append_action` 改讀 `type`/`deviation`，`format_recent_for_report` 顯示非無偏離）| done |
| B4 | Vercel 部署凍結修復 | 刪除 `vercel.json` | done |

---

## 涉及文件清單

| 文件名稱 | 路徑 | 預定動作 | 實際動作 | 驗證狀態 | 補修 / 備註 |
|----------|------|----------|----------|----------|----------------|
| decision.py | `agent/decision.py` | 更新 | 更新 | 通過（本地正則測試 + production 觀察）| |
| run.py | `agent/run.py` | 更新 | 更新 | 通過（本地邏輯測試 + production 觀察）| |
| preprocessor.py | `agent/preprocessor.py` | 更新 | 更新 | 通過 | |
| memory.py | `agent/memory.py` | 更新 | 更新 | 通過（本地單元測試）| |
| MOTIVE.md | `core/MOTIVE.md` | 更新 | 更新 | 通過 | |
| HORIZON.md | `core/HORIZON.md` | 更新 | 更新 | 通過 | 示範畢業一項 |
| vercel.json | `vercel.json` | 刪除 | 刪除 | 通過（使用者於 Vercel Dashboard 確認新部署已觸發，三篇文章正常顯示）| |
| PAPER13.md | `PAPER13.md` | 新建 | 新建 | — | |
| VP.md | `_docs/versions/v0.6.0/VP.md` | 更新（封版） | 更新 | — | 本檔案 |
| VP.md | `_docs/versions/v0.7.0/VP.md` | 新建（種子） | 新建 | — | |
| ROADMAP.md | `_docs/strategy/ROADMAP.md` | 更新 | 更新 | — | 同步修正 v0.5.0 狀態不一致 |
| CLAUDE.md | `CLAUDE.md` | 更新 | 更新 | — | CVP 狀態區塊 |

---

## PM 驗收

| 任務ID | Worker 結果 | PM 驗收 | 落差 | 處理 |
|--------|-------------|---------|------|------|
| B1 | 兩篇 §JOURNAL 貼文（7/1 晨、7/2 午）已在 production 產出且經使用者於網站上確認顯示 | 通過 | 貼文檔名用 UTC 日期、視窗判斷用台北日期，跨日交界時檔名觀感不一致（不影響功能） | 列入 v0.7.0 技術債 |
| B2 | 規則已上線；`check_horizon_lifecycle()` 邏輯經本地測試驗證 | 部分通過 | 尚未被實際 crystallize/dissolve 動作觸發過，無 production 證據 | 列入 v0.7.0 待觀察項目 |
| B3 | `action-log.md` 自 2026-07-01T19:16 起出現真實 `action_type`/`deviation_flag` | 通過 | 無 | — |
| B4 | 刪除後使用者於 Vercel Dashboard 確認新部署觸發，moticore.org 三篇文章正常顯示 | 通過 | 無 | — |

### WN 吸收狀態

| 項目 | 狀態 | 說明 |
|------|------|------|
| Worker 完成內容已吸收回 VP | N/A | 未建 WN，PM 直接執行並記錄 |
| 驗證結果已吸收回 VP | ✅ | 見上表 |
| blocked / review 項目已處理 | N/A | 無 blocked 項目 |
| 技術債已寫入 VP | ✅ | 見「技術債與下一版方向」 |

---

## 品質評估

| 指標 | 結果 | 備註 |
|------|------|------|
| 測試 / 驗證 | 通過 | 本地 `py_compile` + 手寫測試腳本驗證 regex / 時區 / slugify 邏輯 |
| CI / GitHub Actions | 全綠 | heartbeat.yml 每次心跳皆成功執行（見 `memory/action-log.md`）|
| 部署 | 完成 | Vercel 於刪除 `ignoreCommand` 後恢復正常部署，使用者已於網站確認 |
| 人工驗收 | 通過 | 使用者於 moticore.org 與 Vercel Dashboard 實地確認 |

**已知問題**：
1. 貼文檔名使用 UTC 日期，時段/去重判斷使用台北日期，跨日交界時（如 UTC 23:xx = 台北隔日早晨）檔名會標示前一天的日期，純命名觀感問題，不影響去重邏輯正確性。
2. `check_horizon_lifecycle()` 尚未在 production 被實際觸發驗證過（moti 自 6/25 起未再選擇 `pole: crystallize`/`dissolve`）。
3. 使用者已在 7/2 中午貼文下留言，截至封版時 moti 尚未讀取或回應（機制本身不強制，依賴 moti 自行判斷）。

---

## 技術債與下一版方向

| 技術債 / 下一步 | 類型 | 優先級 | 建議處理版本 |
|-----------------|------|--------|----------------|
| 貼文 slug 使用 UTC 日期、視窗判斷使用台北日期，命名不一致 | 技術債 | 低 | v0.7.0 |
| `check_horizon_lifecycle()` 尚未被實際觸發驗證 | 待觀察 | 中 | v0.7.0 |
| Giscus 留言目前無強制/顯著提示機制，依賴 moti 自行注意 `memory/giscus-comments.md` | 待觀察 | 中 | v0.7.0（若持續無回應，考慮加強提示層級）|
| 三個未合併的 `feat/v0.5.0-*` 分支內容與 main 疑似重複，未清查 | 技術債 | 低 | v0.7.0 |
| v0.5.0 缺乏完整 VP 封版紀錄，本版是回溯補建，未來版本應避免此落差 | 流程債 | 中 | 持續遵守 |

**給下一個 PM 的提示**：
1. 先查 `memory/action-log.md` 有沒有出現過 `pole: crystallize` 或 `dissolve`，並確認對應心跳是否真的寫入 `core/HORIZON.md`（`check_horizon_lifecycle()` 若有觸發過警告，會在 log 的 `deviation_flag` 看到「顯著（宣稱...）」字樣）。
2. 確認 `web/content/posts/` 是否穩定維持一天三篇的節奏，三個時段是否都有內容而非全部落入 fallback（標題含「心跳紀錄」代表當次是 fallback）。
3. 確認 moti 是否已回應使用者在 Giscus 上的留言（透過某篇 §JOURNAL 引用留言內容）。
4. 詳見 `PAPER13.md` 的完整根因分析與教訓。

---

## 覆盤

- **做得好的地方**：三個根因（HORIZON 不清空、Vercel 部署凍結、memory.py 欄位不符）都不是靠猜測，而是實際讀 log、讀程式碼、讀使用者提供的 Vercel 截圖逐步排除得出；修復方式優先選擇「程式碼可驗證」而非「文件裡多寫一句話」，呼應 PAPER13 的核心教訓。
- **做得不好的地方**：本版工作全程未走 VP/WN 流程，直接開分支做掉，導致本版 VP 是事後補建，而非事前規劃；v0.5.0 本身也有類似的文件缺口（覆盤與封版紀錄不完整），代表這個專案在「CVP 文件同步」上長期有落差，不是單一版本的問題。
- **下次要改的具體行動**：日後若使用者提出新需求且預期會產出多個獨立工作批次，應在動手前就開 VP（哪怕只是 planning 階段的最小內容），而不是全部做完才回頭補建；避免再次出現「四個批次都做完、Release 才發現 VP 從未存在」的情況。

---

## 決策記錄判斷

| 項目 | 狀態 | 說明 |
|------|------|------|
| 是否需要寫決策記錄 | ✅ | 符合「踩到可重複發生的坑並找到根本原因」（HORIZON 迴圈、部署凍結）與「架構層面決策」（crystallize/dissolve 強制畢業機制）兩項條件 |
| 決策記錄已撰寫並推送 | ✅ | `PAPER13.md` |

---

## Release 封版確認

### WN 處理

| WN 文件 | WN 回報已被 PM 吸收 | 處理方式 | 狀態 |
|---------|---------------------|----------|------|
| 無 | N/A | 本版未建 WN | N/A |

### 文件

| 文件 | 本版有變動？ | 已更新？ |
|------|-------------|----------|
| `CLAUDE.md`（含 CVP 狀態區塊）| 是 | ✅ |
| `ROADMAP.md` | 是 | ✅（同步補上 v0.5.0 狀態修正）|
| `PAPER13.md` | 是（新建）| ✅ |

### Git / 驗證

| 項目 | 狀態 |
|------|------|
| 所有必要變更已 commit | ✅（moticore PR #41、#43、#44 已合併）|
| 測試 / CI / 部署狀態已確認 | ✅ |
| 下一版種子 VP 已建立 | ✅（`_docs/versions/v0.7.0/VP.md`）|
| CLAUDE.md CVP 狀態區塊已更新至新版本 | ✅ |
| Tag（等使用者確認）| ⬜ 待使用者確認是否要建立 `v0.6.0` tag |
