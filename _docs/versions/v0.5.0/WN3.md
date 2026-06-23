# v0.5.0 WN3 — preprocessor.py 極性平衡偵測（T5）

## 文件狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.5.0
- **WN 識別**：WN3
- **對應 VP**：`_docs/versions/v0.5.0/VP.md`
- **WN 狀態**：done
- **建立者（PM）**：PM agent
- **建立時間**：2026-06-23
- **封版處理**：delete

---

## Worker 規則

可修改：`agent/preprocessor.py`
不得修改：其他 agent/ 檔案（WN2 負責）、`core/` 目錄（WN1 負責）、主 VP

程式碼變更須在 feature branch 進行，完成後開 PR merge main。

---

## 任務看板

| 任務ID | 屬性 | 重要性 | 狀態 | 負責代理 | 目標檔案 | 驗證方式 |
|--------|------|--------|------|----------|----------|----------|
| WN3-1 | PJ | CR | ✅ done | Worker agent | `agent/preprocessor.py` | 極性平衡警告在 L2 正確觸發；SYNTHESIS 模式 HORIZON.md 路徑正確 |

---

## 任務區

### WN3-1：preprocessor.py L2 升級為極性平衡偵測

#### Worker 回報
- **完成內容**：
  1. 新增三個輔助函式：`_parse_recent_poles()`（讀 action-log 的 pole 行）、`_count_streak()`（計算尾端連續相同 pole）、`_load_horizon()`（讀 HORIZON.md 前 800 字）
  2. `_layer2_status()` 末尾舊迴圈偵測邏輯替換為極性平衡偵測：動機極連續 ≥5 次 → 提示探索 HORIZON；好奇極連續 ≥8 次 → 提示結晶
  3. 兼容模式（else 分支）：pole 欄位尚未存在時，使用升級版迴圈偵測（n=15，normalize 標點，閾值 3）
  4. `_layer3_synthesis()` 新增 HORIZON.md 判斷：STATUS.md 無待辦 + HORIZON.md 有內容 → 導引好奇極探索，不要求更新 STATUS.md
  5. 確認 `import re` 已在頂部
- **修改檔案**：`agent/preprocessor.py`（branch: feat/v0.5.0-preprocessor-pole-balance）
- **驗證結果**：三個輔助函式存在、極性偵測邏輯存在、兼容模式存在、_layer3_synthesis HORIZON 判斷存在、import re 確認
- **未完成 / 風險**：`has_pending` 關鍵字偵測較粗糙（偵測「待辦/[ ]/未完成/TODO」），若 STATUS.md 格式特殊可能誤判。已知限制，低風險。
- **建議交給 PM 的事項**：has_pending 偵測精化可列為 v0.5.x 技術債

---

## 執行回報總表

| 任務ID | 回報時間 | 負責代理 | 結果 | 摘要 |
|--------|----------|----------|------|------|
| WN3-1 | 2026-06-23 | Worker agent | ✅ done | 極性平衡偵測實作完成 |

---

## 驗證紀錄

| 任務ID | 驗證項目 | 方法 / 指令 | 結果 | 備註 |
|--------|----------|-------------|------|------|
| WN3-1 | 三個輔助函式存在 | 讀取 preprocessor.py | ✅ 確認 | |
| WN3-1 | 極性偵測取代迴圈偵測 | 讀取 _layer2_status() | ✅ 確認 | |
| WN3-1 | 兼容模式存在 | 讀取 else 分支 | ✅ 確認 | |
| WN3-1 | _layer3_synthesis HORIZON 判斷 | 讀取函式 | ✅ 確認 | |

---

## 阻塞與問題

無

---

## PM 吸收檢查

| 項目 | 狀態 | VP 回寫位置 / 處理方式 |
|------|------|------------------------|
| Worker 完成內容已回寫 VP | ⬜ | T5 |
| 驗證結果已回寫 VP | ⬜ | |
| blocked / review 項目已處理 | ✅ N/A | |
| 技術債已回寫 VP | ⬜ | has_pending 精化 → v0.5.x |
| WN 封版處理決定已填寫 | ⬜ | delete（PR merge 後） |
