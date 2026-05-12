# moticore-agent 系統目錄

## 身份核心（唯讀參考）
- `core/identity.md` — 我是誰
- `core/prime-motive.md` — 我存在的根本動機
- `core/value-hierarchy.md` — 價值排序
- `core/constitution.md` — 行動憲法
- `core/forbidden.md` — 禁止模式
- `core/boundary.md` — 邊界規則
- `core/task-inbox.md` — 待辦任務（人類可寫入）
- `core/deviation-log.md` — 偏差記錄

## 記憶系統
- `memory/action-log.md` — 每次心跳的行動記錄（自動累積）
- `memory/reading-cursor.json` — 動機論閱讀游標
- `memory/read-requests.json` — 下次心跳我想讀的檔案清單
- `memory/SYSTEM.md` — 本文件，系統目錄（我可自由更新）

## 筆記系統（自由結構）
- `notes/INDEX.md` — 筆記總目錄
- `notes/` — 所有筆記，結構由我自主決定

## 知識來源
- prima-materia 私有庫：動機論對話稿（第 1-29 篇），透過 DIALOGUES_TOKEN 存取
- 每次心跳讀取約 20,000 字

## GitHub Issues 溝通
- Issue #7：閱讀進度回報（每次心跳自動更新）
- 其他 Issues：與創造者的溝通，我可回覆或開新 Issue

## 我可自主操作的範圍
- 讀寫 `notes/`、`core/`、`memory/`、`reports/` 下的所有檔案
- 透過 `read_next` 欄位指定下次心跳要讀取的檔案
- 更新本文件（SYSTEM.md）以記錄系統變化

## 禁止操作
- 修改 `agent/` 目錄下的程式碼
