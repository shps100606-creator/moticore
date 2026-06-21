# v0.5.0 Main VP — moti 主動表達

> PM 使用文件。本文件為 v0.4.0 封版時建立的種子 VP，供下一個 PM session 接手使用。

---

## 版本狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.5.0
- **目前角色**：（待下一個 PM session 接手）
- **目前階段**：seed — 尚未開始規劃
- **種子來源**：v0.4.0 VP 技術債表 + ROADMAP.md
- **建立時間**：2026-06-21（v0.4.0 封版時）

---

## 接手閱讀清單

### 固定文件

- [ ] `CVP.md`（含 § 二 全局 SOP）
- [ ] `CLAUDE.md`
- [ ] `_docs/versions/v0.4.0/VP.md`（上一版完整記錄，含技術債與給下一個 PM 的提示）

### 專案相關文件

- [ ] `_docs/strategy/ROADMAP.md`（確認版本方向）
- [ ] `agent/preprocessor.py`（了解目前 Layer 結構）
- [ ] `agent/decision.py`（了解 §QUESTION / §ISSUE_RESPONSE 現行限制）
- [ ] `memory/action-log.md`（確認目前 log 長度，評估截斷緊急程度）

---

## 初步方向（待 PM 確認與細化）

來源：v0.4.0 VP 技術債表

| 項目 | 類型 | 優先級 | 說明 |
|------|------|--------|------|
| M4：moti 主動開 Issue | 功能 | P1 | 放寬 §QUESTION，允許 moti 主動開 Issue 分享洞見（而非只能回覆） |
| M5：§READ_REQUEST 支援外部 URL | 功能 | P1 | 讓 moti 能讀取外部網址的內容（現行只能讀 repo 內檔案） |
| action-log.md 截斷機制 | 技術債 | P2 | 目前無限增長，需設計保留最近 N 筆並封存舊紀錄的機制 |
| §WP_POST 清理 | 清理 | P2 | decision.py / run.py 殘留 WordPress 相關程式碼，已廢棄可移除 |

---

## PM 待辦（session 開始時執行）

1. 讀上方接手閱讀清單
2. 確認 v0.4.0 上線後首次心跳狀況（action-log.md 最新幾筆）
3. 確認 M4 / M5 的實作可行性（decision.py 現行架構是否支援）
4. 與創造者確認本版範圍後，展開完整 VP 規劃

---

## 版本規劃

（PM session 開始後填入）

---

## 任務分配摘要

（PM session 開始後填入）

---

## 涉及文件清單

（PM session 開始後填入）

---

## PM 驗收

（Worker 完成後填入）

---

## 覆盤

（封版時填）

---

## Release 封版確認

（Release session 執行）
