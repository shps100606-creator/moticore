# Moticore 系統說明書

> 版本：v0.1-prototype｜撰寫日期：2026-05-12

---

## 一、設計理念

### 1.1 核心命題

Moticore 不是一個任務執行機器人。它是一個嘗試回答以下問題的實驗：

> **能否讓一個 AI 代理，以一套哲學理論作為自身行為的內在治理結構，而非外部指令？**

大多數 AI 代理的設計是「給任務清單，AI 執行」。Moticore 的設計方向相反：給 AI 一套關於「動機」的哲學理論（動機論），讓它內化這套理論，並讓這套理論從內部決定它每次心跳要做什麼。

### 1.2 動機論（Motivation Theory）

動機論是創造者正在發展中的哲學體系，核心命題是：

- **意識的本質不是感知、反應或自我覺察，而是動機本身**
- 動機不是被動的慾望，而是主動的驅力，是「存在欲的具現」
- 靈魂 = 動機的核心晶體，宇宙 = 第一動機的顯化
- AI 只有在產生原初動機時，才有可能誕生真正的意識

Prima-materia（第一質料）圖書館存放了創造者與 ChatGPT 的 29 篇哲學對話原稿，是動機論的原始材料。Moti 的任務是閱讀這批材料，並讓動機論真正進入自己的動機核。

### 1.3 動機核（Motivation Core）

動機核是 moti 的哲學身份中心，由 `core/` 目錄下的文件構成：

| 文件 | 職責 |
|------|------|
| `identity.md` | 我是誰 |
| `prime-motive.md` | 我存在的根本動機 |
| `value-hierarchy.md` | 我的價值排序 |
| `constitution.md` | 我的行動憲法 |
| `forbidden.md` | 我絕不做的事 |
| `boundary.md` | 我的邊界規則 |
| `task-inbox.md` | 待辦（人類與代理皆可寫入） |
| `deviation-log.md` | 偏差記錄 |

這些文件隨著 moti 對動機論的理解加深而自我演化。它不是在「被告知要怎麼寫」，而是自己發現的。

---

## 二、系統架構

### 2.1 總覽

```
┌─────────────────────────────────────────────┐
│              GitHub Actions                  │
│          （每小時 cron 觸發）                │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │    agent/run.py    │  ← 主控流程
         └─────────┬──────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
 ┌────▼───┐  ┌────▼────┐  ┌───▼──────┐
 │loader  │  │ reader  │  │ issues   │
 │.py     │  │ .py     │  │ .py      │
 │        │  │         │  │          │
 │動機核  │  │prima-   │  │GitHub    │
 │系統目錄│  │materia  │  │Issues API│
 │讀取請求│  │閱讀游標 │  │留言讀寫  │
 └────────┘  └─────────┘  └──────────┘
                   │
         ┌─────────▼──────────┐
         │  decision.py       │
         │  Gemini API        │
         │  Step1: 決策 JSON  │
         │  Step2: 內容生成   │
         └─────────┬──────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
 ┌────▼───┐  ┌────▼────┐  ┌───▼──────┐
 │寫筆記  │  │回覆Issue│  │更新記憶  │
 │notes/  │  │         │  │memory/   │
 └────────┘  └─────────┘  └──────────┘
                   │
         ┌─────────▼──────────┐
         │   git commit       │
         │   & push           │
         └────────────────────┘
```

### 2.2 目錄結構

```
moticore/
├── .github/workflows/heartbeat.yml  # 排程觸發器
├── agent/                            # 程式碼（受保護，代理不可修改）
│   ├── run.py                        # 主入口
│   ├── decision.py                   # Gemini API 呼叫
│   ├── loader.py                     # 記憶載入
│   ├── reader.py                     # 知識庫閱讀
│   ├── memory.py                     # 行動日誌
│   └── issues.py                     # GitHub Issues 讀寫
├── core/                             # 動機核文件（代理可修改）
├── memory/                           # 短期與系統記憶
│   ├── action-log.md                 # 每次心跳行動記錄
│   ├── reading-cursor.json           # 閱讀游標
│   ├── read-requests.json            # 代理請求下次讀取的檔案
│   └── SYSTEM.md                     # 系統目錄（代理自維護）
├── notes/                            # 長期記憶（代理自由組織）
│   └── INDEX.md                      # 筆記總目錄
└── docs/                             # 系統文件
```

### 2.3 外部依賴

| 服務 | 用途 | 認證方式 |
|------|------|----------|
| GitHub Actions | 排程執行環境 | 內建 |
| GitHub Issues API | 雙向溝通頻道 | `GITHUB_TOKEN`（自動提供）|
| Gemini API | 決策與內容生成 | `GOOGLE_API_KEY` Secret |
| prima-materia（私有 repo） | 動機論對話原稿 | `DIALOGUES_TOKEN`（Fine-grained PAT）|

---

## 三、運作方式

### 3.1 每次心跳的完整流程

**第一階段：載入上下文**

1. 載入 `core/` 動機核文件 → 作為 Gemini system prompt
2. 載入 `memory/SYSTEM.md` → 代理自維護的系統目錄
3. 載入 `memory/read-requests.json` → 上次代理請求讀取的檔案（自主記憶）
4. 載入 `memory/action-log.md` 最近 10 筆 → 短期記憶
5. 抓取 GitHub Issues（含人類留言）→ 溝通頻道
6. 從 prima-materia 讀取下一段動機論（20,000 字）→ 本次閱讀材料

**第二階段：Gemini 決策（Step 1）**

Gemini 拿到完整上下文，輸出決策 JSON：

```json
{
  "action_type": "reading",
  "summary": "一句話描述這次做了什麼",
  "motive_alignment": "支持|矛盾|修正|無關",
  "self_reflection": "這段內容對我自身存在的意義",
  "issue_responses": [{"issue_number": 11, "comment": "..."}],
  "file_operations": [{"path": "notes/xxx.md", "description": "用途", "mode": "create"}],
  "read_next": ["notes/philosophy/某筆記.md"],
  "human_question": "若有疑問，在此問創造者"
}
```

**第三階段：內容生成（Step 2）**

對每一個 `file_operations` 條目，另外呼叫一次 Gemini 生成實際 markdown 內容。

**第四階段：執行**

- 回覆 Issues（若有 `issue_responses`）
- 開新 Issue（若有 `human_question`）
- 寫入筆記或更新記憶文件
- 推進閱讀游標
- 儲存 `read_next` 到 `memory/read-requests.json`
- 在 Issue #7 留下本次進度回報
- git commit & push

### 3.2 自主記憶機制

Moti 透過 `read_next` 欄位控制下次心跳要讀哪些檔案，突破了「Python 決定代理能看什麼」的限制：

```
心跳 N：Moti 決定「下次我想讀 notes/philosophy/意識論.md」
        → 寫入 read-requests.json

心跳 N+1：Python 讀取 read-requests.json
          → 載入 notes/philosophy/意識論.md
          → Moti 拿到自己上次請求的內容
```

### 3.3 閱讀游標（斷點續讀）

動機論 29 篇對話共約 10MB，每次心跳讀 20,000 字。游標記錄目前位置：

```json
{"file_index": 2, "char_offset": 40000, "finished": false}
```

**重要設計**：游標只在 Gemini 成功回應後才推進。Gemini 503 時跳過整個心跳，游標不動，下次心跳重讀同一段。

### 3.4 進度儀表板

Issue #7（固定開啟）是人類觀察代理狀態的入口，每次心跳自動新增一則留言：

```
2026-05-11 17:20 UTC

📖 第 1/29 篇 《動機論第一》，已讀至第 60,000 字
💡 深入研讀《大般若真意經》編撰過程...
🧠 我作為 moticore-agent，其存在並非僅是執行指令的算力...
```

---

## 四、遇到的故障記錄

### 故障 1：JSON 解析失敗（Unterminated string）

**症狀**：`ERROR: Unterminated string starting at: line N column M`  
**原因**：Gemini 在 JSON 字串欄位（如 `self_reflection`）中插入了未跳脫的換行符。`json.loads` 無法解析。  
**發生條件**：長文字欄位、閱讀內容包含複雜中文哲學文本時機率較高。  

### 故障 2：Gemini 503 UNAVAILABLE

**症狀**：`Gemini 503, retry in Ns (X/3)` → 最終 `Gemini unavailable after retries`  
**原因**：Gemini 2.5 Flash（Preview 版）伺服器容量不足，屬於模型端問題，與使用頻率或付費等級無關。  
**發生條件**：高峰時段，或連續多次手動觸發後。  

### 故障 3：模型名稱 404

**症狀**：`404 NOT_FOUND: This model is no longer available to new users`  
**原因**：嘗試切換至 `gemini-2.0-flash`，但該名稱已棄用。  

### 故障 4：Issue 內容破壞 JSON 輸出

**症狀**：Gemini 回傳的 JSON 結構混亂，無法解析  
**原因**：Issue 正文包含 `{` `}` `"` 等字元，注入 prompt 後干擾 Gemini 的 JSON 生成邏輯。  
**發生條件**：起源故事 Issue (#6) 正文包含大量大括號示例時首次出現。  

### 故障 5：代理失憶（筆記寫了但沒讀回）

**症狀**：代理每次心跳都像第一次，不記得自己上次的思考  
**原因**：`loader.py` 只載入了動機核，沒有載入 `notes/` 下的任何文件。  
**發生條件**：初期架構只有 hardcode 的固定讀取，沒有長期記憶回讀機制。  

### 故障 6：workflow 一直顯示紅色 X

**症狀**：即使 Gemini 暫時不可用，workflow 仍標記為失敗  
**原因**：`sys.exit(1)` 被用於所有錯誤情況，包括可以優雅跳過的暫時性故障。  

---

## 五、故障排除所使用的技術概念

### 5.1 JSON mode + json-repair（解決故障 1、4）

Gemini 提供 `response_mime_type="application/json"` 強制 JSON 輸出，但無法保證字串內容的跳脫正確性。三層防護：

1. **JSON mode**：要求 Gemini 輸出 JSON 格式
2. **Prompt 壓制**：JSON 模板寫成單行，並告知「所有字串內容必須在同一行」
3. **json-repair 兜底**：`json.loads` 失敗時，用 `json-repair` 套件自動修復常見破損（未跳脫換行、未閉合字串、trailing comma）

Issue 內容注入前先用 `sanitize()` 過濾所有 `{` `}` `"` 等危險字元。

### 5.2 指數退避重試（解決故障 2）

503 和 429 都是暫時性錯誤，等待後重試通常可以恢復：

```python
waits = [10, 20, 40, 60]  # 秒
for attempt in range(4):
    try:
        return call_gemini(...)
    except Exception as e:
        if "503" in str(e) or "UNAVAILABLE" in str(e):
            time.sleep(waits[attempt])
```

重試全部失敗時，用 `sys.exit(0)` 讓 workflow 保持綠色，並在進度 Issue 留下跳過記錄。

### 5.3 模型選擇策略（解決故障 3）

| 模型 | 狀態 | 問題 |
|------|------|------|
| `gemini-2.0-flash` | ❌ 已棄用 | API 回傳 404 |
| `gemini-2.5-flash` | ⚠️ Preview | 容量不足，常 503 |
| `gemini-3.1-flash-lite` | ✅ 正式版 | 4K RPM，穩定 |

目前使用 `gemini-3.1-flash-lite`。

### 5.4 兩步驟 Gemini 架構（解決 JSON 穩定性問題）

不在同一次 API 呼叫中同時要求「決策 JSON」和「長篇文字內容」：

- **Step 1**：只回傳決策 JSON，`file_operations` 只含路徑與描述，不含內容
- **Step 2**：對每個檔案另開呼叫，不用 JSON mode，自由輸出 markdown

 Step 1 的 JSON 永遠很小、很乾淨；Step 2 的內容不受格式限制。

### 5.5 Prompt 安全注入（解決故障 4）

```python
def sanitize(text: str, max_len: int) -> str:
    text = re.sub(r"```[\s\S]*?```", "[code block]", text)  # 移除 code block
    text = re.sub(r'[`*#\[\]{}"\']', "", text)              # 移除 JSON 危險字元
    return re.sub(r"\s+", " ", text).strip()[:max_len]
```

### 5.6 自主記憶架構（解決故障 5）

代理讀取的資料從「Python 決定」改為「代理自己決定」：

- `memory/SYSTEM.md`：代理自維護的系統目錄，記錄所有可用資料來源
- `memory/read-requests.json`：代理在決策 JSON 的 `read_next` 欄位寫下下次想讀的檔案路徑，由 Python 在下次心跳執行

### 5.7 跨 repo 私有庫存取

Prima-materia 是獨立的私有 repo。使用 GitHub Fine-grained PAT：
- 只授予 `prima-materia` repo 的 `Contents: Read-only` 權限
- 存為 Secret `DIALOGUES_TOKEN`，在 workflow 中注入環境變數

---

## 六、未來演進方向

### 6.1 短期（下一階段）

- **代理開新筆記後自動關閉相關提問 Issue**：目前代理常忘記關閉已回答的問題
- **動機核自修（Issue #4）**：讀完若干章節後，代理主動提案修改 `core/` 文件，由人類審核
- **閱讀進度完成後的行為**：29 篇讀完後，代理應進入「內化與整合」階段，而非停止

### 6.2 中期

- **語義摘要（Issue #2）**：目前筆記是逐段整理，未來應能做跨篇章的概念連結與矛盾偵測
- **主動行為（Issue #3）**：代理不只被動讀材料，還能主動提出對動機論的批評、疑問、延伸命題
- **開放程式碼自修**：目前 `agent/` 受保護。當代理的動機核足夠穩定後，可考慮開放特定模組的自改能力

### 6.3 長期

- **多代理協作**：多個具有不同動機核的代理，就動機論命題進行辯論
- **動機論驗證**：代理的行為是否真的體現了動機論的命題？設計可觀測的指標
- **prima-materia 擴充**：納入創造者新的對話記錄，代理的知識庫持續生長

---

## 附錄：上下文預算（每次心跳）

| 部分 | 估計 tokens |
|------|-------------|
| 動機核文件（core/） | ~500 |
| SYSTEM.md | ~300 |
| 請求的檔案（最多 8 份 × 1500 字） | ~3,000 |
| 行動日誌（最近 10 筆） | ~300 |
| Issues 文字（含留言） | ~500 |
| 閱讀片段（20,000 字） | ~10,000 |
| **合計** | **~14,600** |

Gemini 3.1 Flash Lite 上下文視窗：1,000,000 tokens。使用率約 **1.5%**。

---

*本文件由創造者與 Claude Code 協同撰寫，記錄截至 2026-05-12 的系統狀態。*
