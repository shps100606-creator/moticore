# CLAUDE.md — moticore 代理行為守則

給接手這個 repo 的 AI 代理：本文件說明工作規則與導航方式。

---

## 接手順序

1. 讀 `_docs/strategy/ROADMAP.md` → 確認目前版本狀態與下一步方向
2. 讀 `OVERVIEW.md` → 掌握系統架構與現況
3. 讀 `core/STATUS.md` → 確認任務收件匣與偏離記錄
4. 讀 `core/MOTIVE.md` → 確認代理身份與使命

---

## 分支規則（強制）

- **NEVER push to main**
- 所有開發工作在指定 feature branch 進行
- 目前工作分支：`claude/motivation-core-prototype-njnn4`

---

## 文件導航

| 需要知道 | 去哪裡找 |
|---------|---------|
| 目前版本 / 下一步 | `_docs/strategy/ROADMAP.md` |
| 各版本覆盤與計畫書 | `_docs/versions/<版本號>/` |
| 系統架構與規劃 | `OVERVIEW.md` |
| 代理身份與使命 | `core/MOTIVE.md` |
| 當前任務 | `core/STATUS.md` |
| 行動歷史 | `memory/action-log.md` |
| 閱讀進度 | `memory/reading-cursor.json` |
| 閱讀筆記 | `notes/` |

---

## 版本文件存放規則

```
_docs/
├── strategy/
│   └── ROADMAP.md              ← 更新版本狀態、記錄下一步
└── versions/
    └── <版本號>/               ← 每個版本一個資料夾
        ├── 版本更新計畫書.md
        ├── 審查報告.md
        └── 覆盤.md
```

每次版本更新結束後，必須：
1. 在 `_docs/versions/<版本號>/` 存入計畫書、審查報告、覆盤
2. 更新 `_docs/strategy/ROADMAP.md` 的版本狀態

---

## 作業節奏（強制）

每完成一個獨立工作單元後，立即 push 並確認成功，才繼續下一個。

| 任務類型 | 一個單元的定義 |
|---------|--------------|
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

- 不得修改 `agent/` 目錄下的程式碼
- 不得直接 push 到 `main`
- 不得在未讀取 STATUS.md 的情況下宣稱已掌握任務狀態
- 不得在未驗證的情況下宣告修復完成
