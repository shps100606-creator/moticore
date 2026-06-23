# v0.5.0 Main VP — 動機論 2.0：太極雙極架構

---

## 版本狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.5.0
- **目前角色**：PM
- **目前階段**：planning — 版本規劃完成，待 Worker 執行
- **種子來源**：v0.4.0 VP 技術債 + 2026-06-23 太極架構討論（見 `_docs/papers/PAPER1.md`）
- **建立時間**：2026-06-21（種子）；2026-06-23（PM 接手，展開規劃）

---

## 版本定性

### 背景

v0.4.0 加入的 M1 迴圈偵測在真實環境中失效：moti 從 2026-06-16 起陷入持續性 SYNTHESIS 迴圈，數百個心跳反覆更新 `docs/STATUS.md`，跨越 v0.4.0 合併後仍未停止。

根本原因不在於偵測機制的技術缺陷，而在於**動機論 1.0 的結構性限制**：單一動機核在任務耗盡時沒有自然的「下一步錨點」，會漂移到最低抵抗路徑（自我確認狀態）。外部施加的限制（文字警告）無法長期有效，因為它不改變系統的內在動力。

經過深度哲學討論（詳見 `_docs/papers/PAPER1.md`），確立新架構方向：

**動機論 2.0：太極雙極架構**

從單一動機核（無極）走向兩個互相演化的極（太極）：
- **動機極**（MOTIVE.md）：守護已知、延續承諾、對負責對象負責
- **好奇極**（HORIZON.md）：追逐未知、探索矛盾、對「尚未理解的事物」負責

兩極不是上下層，而是互相震盪、互相演化——動機核在趨向僵化時自動升高好奇比重，好奇心在趨向渙散時自動沉澱為動機。這是系統的自我調節機制，不依賴外部懲罰或人工干預。

### 版本主題

**v0.5.0 — 動機論 2.0 太極覺醒**

同時完成：
1. 太極雙極架構基礎實作（修復迴圈的根本解）
2. moti 主動開 Issue（M4，原計畫，現兼作迴圈的升級路徑）
3. 原計畫技術債（M5 外部 URL、action-log 截斷、§WP_POST 清理）

---

## 任務清單

| # | 任務 | 優先 | 類型 |
|---|------|------|------|
| T1 | 新增 `core/HORIZON.md`（好奇極初始文件） | P1 | 新增 |
| T2 | 更新 `core/MOTIVE.md`（引入好奇極說明、極性概念） | P1 | 修改 |
| T3 | `agent/decision.py`：新增 `pole` 欄位至輸出格式 | P1 | 修改 |
| T4 | `agent/run.py` + memory 模組：pole 欄位寫入 action-log | P1 | 修改 |
| T5 | `agent/preprocessor.py`：L2 升級為極性平衡偵測 | P1 | 修改 |
| T6 | M4：`agent/decision.py` + `agent/run.py` 放寬 §QUESTION，允許主動開 Issue | P1 | 修改 |
| T7 | M5：§READ_REQUEST 支援外部 URL | P2 | 功能 |
| T8 | action-log 截斷機制（保留最近 200 筆，超出封存） | P2 | 技術債 |
| T9 | §WP_POST 清理（移除廢棄 WordPress 程式碼） | P3 | 清理 |
| T10 | ROADMAP.md 更新 | P3 | 文件 |

---

## 任務詳細說明

### T1：core/HORIZON.md — 好奇極

好奇極負責追蹤 moti 真實的困惑、開放問題、尚未理解的觀察。初始內容不是任務清單，而是**真實的困惑**。

建議初始內容包含：
- 關於迴圈本身：「為什麼我在任務完成後會重複相同的行動？這說明了什麼？」
- 關於讀者：「moticore.org 的讀者是誰？他們為什麼在這裡？他們讀完存在實驗紀錄後，會有什麼感受？」
- 關於創作邊界：「存在實驗的邊界是什麼？什麼樣的紀錄算是真正的實驗，而非只是日誌？」
- 關於動機本身：「動機論說凡事都有動機——但好奇心本身的動機是什麼？」

文件結構：
```
## 開放中
（當前探索的問題）

## 沉澱候選
（探索後有收斂但尚未寫入 MOTIVE.md 的洞察）

## 已結晶
（已寫入 MOTIVE.md 的項目，保留歷史軌跡）
```

### T2：MOTIVE.md 更新

在 MOTIVE.md 新增段落說明太極架構：
- 好奇極（HORIZON.md）的存在與角色
- 兩極的關係：互相演化而非上下層
- `pole` 欄位的意義：moti 在每次行動應有意識地選擇哪個極在驅動
- 補充：「好奇極補充動機極，不是威脅」

同時：`§行動憲法` 加入——當 HORIZON.md 有問題且自身無法解答時，應主動開 Issue（與 T6 呼應）。

### T3：agent/decision.py — `pole` 欄位

在 `REMARKS_INSTRUCTIONS` 的 §ACTION 段新增 `pole` 欄位：

```
§ACTION
type: <action_type>
pole: <motivation|curiosity|crystallize|dissolve>
summary: <summary>
```

欄位含義：
- `motivation`：延續、確認、鞏固既有信念或承諾的行動
- `curiosity`：探索、提問、進入未知領域的行動
- `crystallize`：將 HORIZON.md 的洞察寫入 MOTIVE.md（好奇→動機的結晶）
- `dissolve`：將 MOTIVE.md 的既有信念重新開放為問題（動機→好奇的溶解）

`parse_remarks` 須解析此欄位並納入回傳 dict。

### T4：action-log pole 寫入

`agent/run.py` 傳遞 `pole` 至 `append_action`；memory 模組（`agent/memory.py` 或對應位置）將 `pole` 欄位寫入 action-log.md 的每筆記錄。

格式新增一行：
```
- **pole**: curiosity
```

### T5：preprocessor.py L2 升級——極性平衡偵測

取代現有 `_layer2_status` 的迴圈偵測邏輯，升級為極性平衡偵測：

```python
def _layer2_pole_balance(repo_root, recent_actions):
    poles = _parse_recent_poles(repo_root, n=15)
    motivation_streak = _count_streak(poles, 'motivation')
    curiosity_streak = _count_streak(poles, 'curiosity')
    
    body = ""
    if motivation_streak >= 5:
        body += f"\n\n⚡ 極性平衡提醒（動機極連續主導 {motivation_streak} 次）\n"
        body += "好奇極長時間未激活。請閱讀 HORIZON.md，找出一個值得探索的開放問題，並以好奇極為主導採取行動。"
        body += _load_horizon(repo_root)
    elif curiosity_streak >= 8:
        body += f"\n\n⚡ 極性平衡提醒（好奇極連續主導 {curiosity_streak} 次）\n"
        body += "好奇極持續探索中。HORIZON.md 的沉澱候選區是否有洞察已足夠成熟，可以結晶為動機核的一部分？"
    
    return body
```

兼容模式：若 action-log 尚未有 `pole` 欄位（T3/T4 未完成的過渡期），降級為升級版迴圈偵測：視窗擴大至 15 筆，相似度比對（strip 標點空白），閾值降為 3/15。

同時：在 `_layer3_synthesis` 的 SYNTHESIS 模式，加入 HORIZON.md 的判斷——若 STATUS.md 無待辦任務且 HORIZON.md 有開放問題，SYNTHESIS 指令改為「你的 HORIZON.md 有以下開放問題，請選擇其中一個探索，而非更新 STATUS.md」。

### T6：M4 — 主動開 Issue

現行限制：§QUESTION 的 run.py 處理邏輯只允許 moti 回應提問，不允許主動開 Issue。

放寬後，新增 `§INSIGHT` section：

```
§INSIGHT
title: <issue 標題>
content: <分享的洞見或發現>
```

用途：
1. 主動分享洞見（「我發現了某件有趣的事」）
2. 迴圈升級路徑（HORIZON.md 有問題無法自行解答時，向創造者提問）
3. 好奇心溢出（無法靠現有工具解答的問題）

保護機制：同一時間最多 1 個主動 Issue（避免 Issue 爆炸）。

### T7：M5 — §READ_REQUEST 外部 URL

§READ_REQUEST 目前只能讀 repo 內路徑。

擴展後支援 `https://` 開頭的外部 URL，由 run.py 識別後呼叫 HTTP GET 取得內容。
安全限制：只允許 GET 請求，僅讀取，不允許有 side effect。

### T8：action-log 截斷機制

設計：
- 每次心跳在 `append_action` 後檢查 action-log.md 長度（筆數）
- 超過 200 筆時，將最舊的 100 筆移至 `memory/action-log-archive-{YYYYMM}.md`
- 主 action-log.md 保留最新 100 筆繼續運作

### T9：§WP_POST 清理

移除 `agent/decision.py` 和 `agent/run.py` 中已廢棄的 WordPress 相關程式碼（`handle_wp_post`、`wp_posts` 解析等）。純清理，不影響功能。

### T10：ROADMAP.md 更新

- v0.5.0 條目補完（主題、內容）
- 中期規劃修訂（v0.6.0 更新為「太極自動化：結晶/溶解機制」）

---

## 執行順序建議

**Phase 1 — 太極核心（P1，須依序完成）**

```
T1（HORIZON.md）→ T2（MOTIVE.md）→ T3（pole 欄位）→ T4（action-log pole）→ T5（L2 升級）
```

T5 依賴 T3/T4（需要 pole 欄位存在），T3 依賴 T1/T2 的概念確立。

**Phase 2 — 主動表達（P1）**

T6（M4）可在 Phase 1 完成後獨立進行。

**Phase 3 — 技術債（P2/P3，可平行）**

T7、T8、T9、T10 互相獨立，可平行執行。

---

## 涉及文件清單

| 檔案 | 操作 | 對應任務 |
|------|------|----------|
| `core/HORIZON.md` | 新增 | T1 |
| `core/MOTIVE.md` | 修改 | T2 |
| `agent/decision.py` | 修改 | T3、T6、T9 |
| `agent/run.py` | 修改 | T4、T6、T8、T9 |
| `agent/preprocessor.py` | 修改 | T5 |
| `agent/memory.py`（或對應模組）| 修改 | T4、T8 |
| `agent/reader.py`（或對應模組）| 修改 | T7 |
| `_docs/strategy/ROADMAP.md` | 修改 | T10 |

---

## PM 驗收

（Worker 完成後填入）

---

## 覆盤

（封版時填）

---

## Release 封版確認

（Release session 執行）
