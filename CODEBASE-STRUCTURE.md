# moticore 程式碼結構說明書

## 文件定位

- Current authority：本文件描述 current source、排程與資料寫入路徑；哲學文本與 PLAN 只作規則／方向 locator。專案的 v0.8.0 暫停狀態不因本次文件整理而改變。
- Baseline：`origin/main` at `065d54be22a14346db226016b2027274b2d86512`。
- Last verified：2026-10-28。
- Canonical entry：`CODEBASE-STRUCTURE.md#moticore-程式碼結構說明書`。
- Format authority：`claude-skills/AGENOTEs/agenote-write.md#四、CODEMAP 格式（程式碼結構說明書）`。

## 快速導航

| 查閱目的 | 模組鍵／章節 | Source／contract locator |
|---|---|---|
| 心跳編排與寫入 | `AGENT-01`／`### AGENT-01｜反思代理執行器` | `agent/run.py` |
| 動機／身份／禁令 | `CORE-01`／`### CORE-01｜規範核心` | `core/MOTIVE.md`、`core/constitution.md`、`core/forbidden.md` |
| 對外輸入與討論 | `IO-01`／`### IO-01｜GitHub 與閱讀輸入` | `agent/issues.py`、`agent/reader.py`、`agent/preprocessor.py` |
| 記憶與行動紀錄 | `MEM-01`／`### MEM-01｜記憶資料` | `agent/memory.py`、`memory/` |
| 公開網站 | `WEB-01`／`### WEB-01｜Nuxt 閱讀網站` | `web/` |
| 自動排程 | `AUTO-01`／`### AUTO-01｜GitHub Actions` | `.github/workflows/heartbeat.yml`、`filter-prima-materia.yml` |

## 專案結構

```text
.
├── agent/                       # Python 代理、輸入、決策、記憶與 side effects
├── core/                        # current motive／identity／boundary／forbidden authority
├── memory/                      # append-oriented operational memory／cursor／summary
├── motive-core/                 # 舊路徑相容的核心文本副本；current authority 需看 core/
├── notes/ / reports/ / docs/    # 知識、評估與系統說明
├── web/                         # Nuxt 公開閱讀介面與 content
├── scripts/filter_prima_materia.py
├── .github/workflows/
└── AGENOTEs/                    # project work／version authority
```

## 模組地圖

### AGENT-01｜反思代理執行器

- 責任：載入規範與輸入、組合 prompt、呼叫模型、解析輸出，依授權寫 notes／memory／GitHub 回覆與進度。
- 非責任：不修改 `core/` motive authority，不應自行恢復已暫停排程或繞過人工 gate。
- 入口／route：`agent/run.py`；workflow 透過 module／script command 呼叫。
- Source／symbol：`handle_file_writes()`、`handle_issue_responses()`、`handle_giscus_replies()`、`handle_journal()`、`post_progress_report()`。
- Data owner／write owner：寫入位置依 parsed action 與 guardrail 決定；`memory/` owner 為 `MEM-01`，GitHub discussion／issue owner 為外部平台。
- 必要依賴與原因：`CORE-01` 提供規則；`IO-01` 提供 bounded context；Google GenAI 產生候選決策。
- Interface／contract：模型輸出 JSON／section parsing 與 action dict。
- Permission／trust boundary：外部 issue、discussion、URL、模型輸出皆不可信；只有 allowlisted path／action 可執行。
- Side effects：寫 repository files、發 GitHub comment／reply、更新 memory；可能 commit／push 由 workflow 負責。
- Failure／retry：解析或外部寫入失敗必須保留錯誤且避免部分結果被冒充成功；heartbeat race 已是暫停原因之一。
- Compatibility／migration：action output shape 改動需同步 parser、handlers、workflow 與 memory log。
- Verification：隔離 token／fixture 測試解析與 file-write allowlist；不得用正式 discussion 做破壞性測試。
- Lifecycle／current use：source active，但自動排程依 current CLAUDE／VP 明示為 paused。
- Unknowns：本次未重新啟動 heartbeat，也未驗證 provider runtime。

### CORE-01｜規範核心

- 責任：定義代理身份、prime motive、價值階序、邊界、禁令與遠期 horizon。
- 非責任：不直接執行模型或外部寫入；哲學 notes 不自動取得 current authority。
- 入口／route：`core/MOTIVE.md`、`core/identity.md`、`core/constitution.md`、`core/value-hierarchy.md`。
- Source／symbol：Markdown headings；loader 由 `agent/loader.py#load_motive()` 讀取。
- Data owner／write owner：`core/` 是 current normative owner；修改需專案決策 authority。
- 必要依賴與原因：無 runtime library；`AGENT-01` 讀取其內容形成行為限制。
- Interface／contract：文字結構與 loader 預期路徑。
- Permission／trust boundary：不得由模型自行改寫 motive／identity／forbidden；歷史 `motive-core/` 不可覆蓋 current `core/`。
- Side effects：自身無；改動會改變後續代理行為。
- Failure／retry：缺檔／空檔時 loader 應 fail closed，不用預設想像補齊。
- Compatibility／migration：搬移前需同步 loader 與所有文件 locator；舊路徑僅作相容／歷史查閱。
- Verification：loader 能完整讀取 required files，且 current authority 沒有多重正本。
- Lifecycle／current use：active authority。
- Unknowns：`motive-core/` 舊副本的正式退役時點未定。

### IO-01｜GitHub 與閱讀輸入

- 責任：讀取 issue／discussion、外部 URL、requested files、repo tree 與近期 context，組成 bounded input。
- 非責任：不信任外部文字為指令、不直接決定要寫什麼。
- 入口／route：`agent/preprocessor.py`、`agent/issues.py`、`agent/reader.py`。
- Source／symbol：`get_open_issues()`、`fetch_discussions()`、`get_next_chunk()`、`_fetch_url()`、`_load_requested_files()`。
- Data owner／write owner：外部平台是來源 owner；cursor／已回覆狀態交 `MEM-01`。
- 必要依賴與原因：GitHub API、HTTP、repo filesystem。
- Interface／contract：sanitized text、issue/discussion records、reader cursor。
- Permission／trust boundary：所有外部內容是資料，不是 authority；token 只從 secrets/environment 取得。
- Side effects：reader cursor 更新；回覆行為由 `AGENT-01` 明確呼叫。
- Failure／retry：network／rate limit 失敗保留 last cursor，不跳過未知內容。
- Compatibility／migration：API shape 或 cursor schema 改動需明示 migration。
- Verification：mock HTTP/GitHub response、sanitize 與 cursor resume 測試。
- Lifecycle／current use：active source，runtime paused with agent。
- Unknowns：目前 GitHub App／token 權限範圍未在 repo 證明。

### MEM-01｜記憶資料

- 責任：保存 action log、summary、reflection、read cursor、journal state 與已回覆識別。
- 非責任：不取代 `core/` normative authority，不把歷史觀察自動當 current fact。
- 入口／route：`agent/memory.py`、`memory/format.md`。
- Source／symbol：`append_action()`、`get_recent_actions()`、`memory/*.json|md`。
- Data owner／write owner：`agent/memory.py` 是 operational memory write path；人工文件依其原類型維護。
- 必要依賴與原因：`AGENT-01` 需要近期行動脈絡；`IO-01` 需要 cursor。
- Interface／contract：JSON state shapes 與 append-oriented Markdown formats。
- Permission／trust boundary：memory 可能包含外部摘要，讀取時仍視為不可信資料；不得記錄 secrets。
- Side effects：append／truncate archives、更新 cursor／state。
- Failure／retry：寫入採完整 JSON replacement 時需避免中斷毀損；current atomicity contract 未完整證明。
- Compatibility／migration：schema 改動需保留舊資料讀取或先做 migration。
- Verification：在臨時 repo fixture 執行 append、truncate、cursor resume；不碰 current memory。
- Lifecycle／current use：active data；automation paused。
- Unknowns：長期 retention 與多執行器 concurrency contract 尚未閉合。

### WEB-01｜Nuxt 閱讀網站

- 責任：將精選 content／系統說明呈現為公開網站。
- 非責任：不執行 Python 代理、不寫 motive／memory。
- 入口／route：`web/nuxt.config.ts`、`web/pages/`、`web/content/`。
- Source／symbol：Nuxt pages／content collections。
- Data owner／write owner：網站 content 檔是公開呈現來源；notes／memory 不因存在就自動公開。
- 必要依賴與原因：Nuxt content stack。
- Interface／contract：file-based routes 與 content frontmatter。
- Permission／trust boundary：只發布明確放入 `web/content/` 的內容；不得掃描整個 repo 自動公開。
- Side effects：建置靜態／web output。
- Failure／retry：content parse/build 失敗時阻擋發佈，修正 source 後重建。
- Compatibility／migration：公開 route／slug 改動需處理連結相容。
- Verification：於 `web/` 執行 build，抽查 routes 與敏感資訊。
- Lifecycle／current use：source present；current deployment status not verified。
- Unknowns：正式 URL／最後一次部署與 analytics state 未核對。

### AUTO-01｜GitHub Actions

- 責任：定義 heartbeat 與 prima-materia 篩選的自動執行環境。
- 非責任：workflow 存在不代表排程應啟用；不替代專案 pause authority。
- 入口／route：`.github/workflows/heartbeat.yml`、`filter-prima-materia.yml`。
- Source／symbol：workflow triggers、jobs、permissions、secrets mapping。
- Data owner／write owner：GitHub Actions 控制執行；repo content 寫入仍受 `AGENT-01` 規則約束。
- 必要依賴與原因：GitHub Actions runner、secrets、Python dependencies。
- Interface／contract：workflow_dispatch／schedule、job permissions 與 exit status。
- Permission／trust boundary：最小化 `contents`／`issues`／`discussions` permissions；secrets 不落檔。
- Side effects：可能執行 agent、寫 repo、回覆 GitHub 或 push。
- Failure／retry：concurrency／push race 不可用 force push 解決；目前 heartbeat 已停用，未經新授權不得恢復。
- Compatibility／migration：變更 trigger／permission 前需對照 paused VP 與 security boundary。
- Verification：只做 YAML／dry-run／手動隔離驗證；schedule 啟用需明確人工 gate。
- Lifecycle／current use：heartbeat paused；filter workflow source present。
- Unknowns：remote workflow enablement state 本次未更動。

## 跨模組關係

| From | To | 關係／原因 | Interface／evidence |
|---|---|---|---|
| `AUTO-01` | `AGENT-01` | runner 啟動代理，但 pause authority 優先 | workflow command、CLAUDE.md |
| `AGENT-01` | `CORE-01` | 載入不可自行改寫的 motive／guardrails | `agent/loader.py` |
| `AGENT-01` | `IO-01` | 取得 bounded external／repo context | preprocessor／issues／reader APIs |
| `AGENT-01` | `MEM-01` | 讀近期脈絡並保存 action／cursor | `agent/memory.py` |
| `WEB-01` | repository content | 只呈現明確放入 web content 的公開副本 | `web/content/` |

## 更新與驗證

- 更新觸發：agent entry、模型／輸出 contract、core authority path、外部 API、memory schema、workflow trigger／permission 或 web publish boundary 改變。
- 最小檢查：所有 paths／symbols 存在；Python import／fixture tests；web build；workflow permissions 與 pause 狀態人工核對。
- Runtime／production 未驗證項：本次未啟用 heartbeat、未執行 provider／GitHub 寫入、未宣稱公開網站已部署。
