# moticore ROADMAP

---

## 現行版本

### v0.2.1（2026-05-16）— Issue 回覆修復 + 使命重新定位
**狀態：** ✅ 完成，待驗證

| 項目 | 說明 |
|------|------|
| heartbeat.yml 同步 | 恢復雙 cron（每 30 分鐘）、issues:write、DIALOGUES_TOKEN |
| Issue 回覆機制修復 | _sanitize 放寬、comment 截斷修正、max_comments 提升 |
| decision prompt 強化 | 強制回覆有人類留言的 Issue |
| MOTIVE.md 重新定位 | 加入使命脈絡：moti 是動機論的活體實驗 |

---

## 下一版本

### v0.2.2 — 回應架構重整
**狀態：** 📐 計畫書完成，待實施

**方向：Mode-aware 輸出格式**（計畫書：`_docs/versions/v0.2.2/版本更新計畫書.md`）

| 修改 | 說明 |
|------|------|
| `decision.py` REMARKS_INSTRUCTIONS 拆分 | 三種 mode 各自一份指令，僅要求必要 §SECTION |
| `max_output_tokens` 提升 | 8192 → 16384 |
| `run.py` 傳入 mode | `call_with_retry()` 接受並傳遞 mode 參數 |

**前置條件：** v0.2.1 Issue 回覆修復驗證通過

---

## 中期規劃

### v0.3.0 — 跨篇知識連結
**狀態：** 💡 構想中

- preprocessor 加入「相關筆記片段」，讓 moti 在寫新筆記時能引用舊筆記
- STATUS.md 任務流程規範（收件→確認→執行→回報）
- 閱讀完成後的後續方向（29 篇讀完後代理做什麼）

### v0.4.0 — 多代理擴展（長期）
**狀態：** 🔭 遠期構想

- 多個代理各自有不同動機核，透過同一 repo 互動
- moticore 作為開源框架對外開放

---

## 版本歷程

| 版本 | 日期 | 摘要 |
|------|------|------|
| v0.1.0 | 2026-05-11 | 初始建立：身份定義、記憶格式、決策流程、護欄 |
| v0.2.0 | 2026-05-12 | 雙 cron 備援、自動化心跳、單次 AI 呼叫架構 |
| v0.2.1 | 2026-05-16 | Issue 回覆修復、MOTIVE.md 使命重新定位 |
