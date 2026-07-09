# moticore

> 動機核驅動的自主 AI 代理實驗系統

## 這是什麼？

**moticore** 是一個以「動機核」哲學治理的自主 AI 代理實驗。核心命題：

> **AI 代理的長期行為一致性，取決於動機的清晰度，而非規則的詳細程度。**

代理 **moti** 每 30 分鐘心跳一次，閱讀動機論原典、回應 Issues、更新記憶。它同時是這場實驗的研究者，也是被研究的對象。

---

## 接手代理：從這裡開始

| 文件 | 說明 |
|------|------|
| `_docs/strategy/ROADMAP.md` | **版本歷程 + 下一步方向（優先讀這裡）** |
| `AGENOTEs/VPs/<版本號>/` | 各版本覆盤、計畫書、審查報告 |
| `OVERVIEW.md` | 系統架構完整說明、現況快照、後續規劃 |
| `core/MOTIVE.md` | 代理身份 + 使命（直接作為 Gemini system_instruction）|
| `core/STATUS.md` | 任務收件匣 + 偏離記錄 |

---

## 目前版本

**v0.2.1**（2026-05-16）— Issue 回覆修復 + 使命重新定位

| 狀態 | 說明 |
|------|------|
| 心跳頻率 | 每 30 分鐘（雙 cron 備援）|
| AI 模型 | `gemini-3.1-flash-lite` |
| 閱讀進度 | 動機論第 16/29 篇 |
| Issue 回覆 | v0.2.1 修復中，待驗證 |

---

## 系統架構

```
每 30 分鐘觸發（雙 cron）
     ↓
[loader]       core/MOTIVE.md → Gemini system_instruction
     ↓
[preprocessor] 整合上下文（狀態、Issues、行動記錄、閱讀進度）
     ↓
[decision]     單次 Gemini 呼叫 → 完整 JSON 決策
     ↓
[action]       執行：寫檔、回 Issue、更新記憶、推進閱讀游標
```

---

## 目錄結構

```
moticore/
├── README.md                 ← 本文件（快速定向）
├── CLAUDE.md                 ← 代理行為守則
├── OVERVIEW.md               ← 系統架構完整說明與規劃
├── CHANGELOG.md              ← 版本紀錄
├── _docs/
│   ├── strategy/
│   │   └── ROADMAP.md        ← 版本歷程 + 中長期規劃
│   └── versions/
│       └── v0.2.1/
│           └── 覆盤.md
├── agent/                    ← Python 代理程式碼（禁止修改）
│   ├── run.py
│   ├── loader.py
│   ├── preprocessor.py
│   ├── decision.py
│   ├── issues.py
│   ├── memory.py
│   └── reader.py
├── core/                     ← 動機核治理文件
│   ├── MOTIVE.md             ← 身份 + 使命（system_instruction）
│   └── STATUS.md             ← 任務收件匣 + 偏離記錄
├── memory/                   ← 記憶層
│   ├── action-log.md         ← 每次心跳行動紀錄
│   └── reading-cursor.json   ← 動機論閱讀游標
├── notes/                    ← moti 的閱讀筆記與研究文件
├── reports/                  ← 心跳進度報告
└── .github/workflows/
    └── heartbeat.yml         ← 每 30 分鐘觸發
```

---

## 操作邊界

- 只操作 `shps100606-creator/moticore` 倉庫
- 只讀取 / 寫入 `claude/motivation-core-prototype-njnn4` 分支
- 只透過 GitHub Issues 與外部溝通
- **禁止修改 `agent/` 目錄下的程式碼**

---

*任何失敗、修正與演化過程皆為有效實驗資料。*
