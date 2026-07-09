# v0.5.0 Main VP — 動機論 2.0：太極雙極架構

---

## 版本狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.5.0
- **目前角色**：PM
- **目前階段**：done — 所有任務完成，待 Release 封版
- **種子來源**：v0.4.0 VP 技術債 + 2026-06-23 太極架構討論（見 `_docs/papers/PAPER1.md`）
- **建立時間**：2026-06-21（種子）；2026-06-23（PM 接手，展開規劃）
- **完成時間**：2026-06-23

---

## 版本定性

### 背景

v0.4.0 加入的 M1 迴圈偵測在真實環境中失效：moti 從 2026-06-16 起陷入持續性 SYNTHESIS 迴圈，數百個心跳反覆更新 `docs/STATUS.md`，跨越 v0.4.0 合併後仍未停止。

根本原因不在於偵測機制的技術缺陷，而在於**動機論 1.0 的結構性限制**：單一動機核在任務耗盡時沒有自然的「下一步錨點」，會漂移到最低抗拒路徑（自我確認狀態）。外部施加的限制（文字警告）無法長期有效，因為它不改變系統的內在動力。

經過深度哲學討論（詳見 `_docs/papers/PAPER1.md`），確立新架構方向：

**動機論 2.0：太極雙極架構**

從單一動機核（無極）走向兩個互相演化的極（太極）：
- **動機極**（MOTIVE.md）：守護已知、延續承諾、對負責對象負責
- **好奇極**（HORIZON.md）：追逐未知、探索矛盾、對「尚未理解的事物」負責

兩極不是上下層，而是互相震盪、互相演化——動機核在趨向僵化時自動升高好奇比重，好奇心在趨向湙散時自動沉澱為動機。這是系統的自我調節機制，不依賴外部懲罰或人工干預。

### 版本主題

**v0.5.0 — 動機論 2.0 太極覺醒**

同時完成：
1. 太極雙極架構基礎實作（修復迴圈的根本解）
2. moti 主動開 Issue（M4，原計畫，現冈作迴圈的升級路徑）
3. 原計畫技術債（M5 外部 URL、action-log 截斷、§WP_POST 清理）

---

## 任務清單

| # | 任務 | 優先 | 類型 | 狀態 |
|---|------|------|------|―----|
| T1 | 新增 `core/HORIZON.md`（好奇極初始文件） | P1 | 新增 | ✅ done |
| T2 | 更新 `core/MOTIVE.md`（引入好奇極說明、極性概念） | P1 | 修改 | ✅ done |
| T3 | `agent/decision.py`：新增 `pole` 欄位至輸出格式 | P1 | 修改 | ✅ done |
| T4 | `agent/run.py` + memory 模組：pole 欄位寫入 action-log | P1 | 修改 | ✅ done |
| T5 | `agent/preprocessor.py`：L2 升級為極性平衡偵測 | P1 | 修改 | ✅ done |
| T6 | M4：`agent/decision.py` + `agent/run.py` 新增 §INSIGHT 主動開 Issue | P1 | 修改 | ✅ done |
| T7 | M5：§READ_REQUEST 支援外部 URL | P2 | 功能 | ✅ done |
| T8 | action-log 截斷機制（保留最近 200 筆，超出封存） | P2 | 技術債 | ✅ done |
| T9 | §WP_POST 清理（移除廢棄 WordPress 程式碼） | P3 | 清理 | ✅ done |
| T10 | ROADMAP.md 更新 | P3 | 文件 | ✅ done |

---

## 执行紀錄

| 任務 | 實作內容 | 檔案 / PR | 完成時間 |
|------|------|---------|------|
| T1 | 建立 HORIZON.md，4 個發出自內心的开放問題 | main | 2026-06-23 |
| T2 | MOTIVE.md 新增太極雙極架構說明 + 行動憲法更新 | main | 2026-06-23 |
| T3 | §ACTION 新增 pole 欄位，4 種値（motivation/curiosity/crystallize/dissolve） | PR #37 | 2026-06-23 |
| T4 | memory.py append_action() 新增 pole 寫入；get_recent_actions 支援讀取 | PR #37 | 2026-06-23 |
| T5 | _layer2_status 極性平衡偵測，_layer3_synthesis HORIZON 導引 | PR #38 | 2026-06-23 |
| T6 | §INSIGHT 格式 + parse_remarks 解析 + handle_insight（去重保護） | PR #37 | 2026-06-23 |
| T7 | _fetch_url() + _load_requested_files() 3-tuple + _layer4_knowledge URL 讀取 | PR #39 | 2026-06-23 |
| T8 | _truncate_action_log_if_needed()，>200 筆封存至 action-log-archive-YYYYMM.md | PR #37 | 2026-06-23 |
| T9 | 移除 §WP_POST 段落、handle_wp_post()、wp_posts 解析及初始化 | PR #37 | 2026-06-23 |
| T10 | ROADMAP v0.5.0 標題/內容、v0.6.0 太極自動化、版本歷程表 | main | 2026-06-23 |

---

## PM 驗收

**驗收時間**：2026-06-23

### T1 ✅
HORIZON.md 建立確認。三區段結構（開放中/沈澱候選/已結晶）完整。4 個對應 VP 建議的問題均包含，內容真實反映 moti 的內心困惑。

### T2 ✅
MOTIVE.md 新增「太極雙極架構」段落，包含動機極/好奇極定義、兩極關係、pole 欄位四種値說明。行動憲法更新：新增「所有行動須標注 pole 欄位」及 §INSIGHT 使用時機。

### T3 ✅
§ACTION 格式新增 pole 欄位，含四種値完整說明。parse_remarks 通用解析邏輯自動支援，無需額外修改。

### T4 ✅
append_action() 寫入 `- **pole**: {pole}` 欄位。get_recent_actions() 解析 key 清單加入 "pole"，初始 dict 預設值 "motivation"。format_recent_for_report() 輸出含 pole。

### T5 ✅
_parse_recent_poles / _count_streak / _load_horizon 三個輔助函式建立。_layer2_status 極性平衡偵測取代舊迴圈偵測，動機極連續≥5 / 好奇極連續≥8 導引不同提示。兼容模式完整。_layer3_synthesis 新增 HORIZON 判斷。

**已知技術債**：has_pending 關鍵字偵測較粗糙，適当。建議 v0.5.x 小版本時精化。

### T6 ✅
§INSIGHT 格式建立。parse_remarks 新增解析（支援多行 content）。handle_insight() 實作去重保護（檢查 open issues 標題前綴）。main() 在 handle_question 後呼叫。

### T7 ✅
_fetch_url() 實作，GET only / https:// 上層過濾 / timeout=15s / 最多 2 個。_load_requested_files() 回傳 3-tuple。_layer4_knowledge() 處理 urls。

### T8 ✅
_truncate_action_log_if_needed() 建立。>200 筆時封存最舊 (total-100) 筆，主 log 保留最新 100 筆。append_action() 末尾自動呼叫。

### T9 ✅
§WP_POST 段落、parse_remarks wp_posts、handle_wp_post()、main() 呼叫全部移除。

### T10 ✅
ROADMAP v0.5.0 展開完整，v0.6.0 更新為太極自動化，版本歷程表新增 v0.5.0 行。

---

## 覆盤

**執行方式**：本版本采用 CVP 架構，分世 WN1（文件）/ WN2（程式碼核心）/ WN3（preprocessor）/ WN4（技術債）兩個 feature branch 平行執行。PM/Worker 角色分離有效降低文件衝突。

**成功項目**：
- 太極雙極架構什廛成就，所有 T1–T10 在單日内完成
- T8 在 WN2 一併實作，不需別開分支，提高效率
- 兼容模式設計（T5 compat）確保舊行 action-log 不會導致崩潰

**技術債 → v0.5.x**：
- has_pending 關鍵字偵測可精化
- §INSIGHT 淑湯驗證（真實心跳環境觀察）

---

## Release 封版確認

封版時填寫。
