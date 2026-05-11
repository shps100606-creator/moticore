# 範例決策追蹤（Example Decision Trace）

此文件展示一次完整的代理決策流程，供理解與測試參考。

---

## 場景：首次心跳

**觸發**: GitHub Actions cron（`0 */6 * * *`）  
**時間**: 2026-05-11T06:00:00Z  
**代理狀態**: 剛完成 v0.1.0 建立

---

## 步驟一：載入動機核

`loader.py` 讀取以下文件：
- `motive-core/identity.md` ✅
- `motive-core/prime-motive.md` ✅
- `motive-core/constitution.md` ✅
- `motive-core/value-hierarchy.md` ✅
- `guardrails/forbidden-patterns.md` ✅
- `guardrails/boundary-rules.md` ✅
- `memory/action-log.md` ✅
- `tasks/inbox.md` ✅

## 步驟二：讀取最近行動

```
ACT-20260511-001 ~ ACT-20260511-004（v0.1.0 建立記錄）
```

## 步驟三：呼叫 Claude API

**System Prompt**: 動機核全文（含 prompt caching）  
**User Prompt**: 當前狀態（最近行動 + 任務收件匣）

## 步驟四：Claude 的回應（範例）

```json
{
  "action_type": "introspection",
  "summary": "執行 v0.1.0 建立後的首次完整自省",
  "motive_alignment": "自省是探索動機核能否自我維持的核心程序，直接服務於主動機",
  "execution_reasoning": "TASK-001 要求首次完整自省；憲法第三條規定完成重大任務後必須自省；v0.1.0 建立為首個重大任務",
  "risk_assessment": "無",
  "deviation_flag": "無",
  "result": "完成",
  "followup": "無",
  "introspection_findings": "v0.1.0 結構完整，主動機語句清楚，價值排序無歧義。行動記錄 4 條均有主動機關連說明。語義裁決 3 條已建立核心概念定義。未發現偏離。建議：TASK-001 標記完成，下一步觀察首次自動心跳結果。",
  "report_content": ""
}
```

## 步驟五：記錄行動

```
---
ID: ACT-20260511-005  
時間: 2026-05-11  
類型: introspection  
摘要: 執行 v0.1.0 建立後的首次完整自省  
...
```

## 步驟六：commit & push

```
git commit -m "chore(agent): heartbeat log 2026-05-11T06:00:00Z"
```

---

*此為示範性範例，實際執行結果可能因 Claude 的當次判斷而異。*
