# v0.5.0 WN3 — preprocessor.py 極性平衡偵測（T5）

## 文件狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.5.0
- **WN 識別**：WN3
- **對應 VP**：`_docs/versions/v0.5.0/VP.md`
- **WN 狀態**：active
- **建立者（PM）**：PM agent
- **建立時間**：2026-06-23
- **封版處理**：delete

---

## Worker 規則

可修改：`agent/preprocessor.py`
不得修改：其他 agent/ 檔案（WN2 負責）、`core/` 目錄（WN1 負責）、主 VP

程式碼變更須在 feature branch 進行，完成後開 PR merge main。

**等待條件**：WN2-2 和 WN2-3 完成後再執行（需要 pole 欄位已寫入 action-log）。
若 WN2 尚未完成，本 WN 的兼容模式（見 WN3-1 說明）仍可先執行。

---

## 任務看板

| 任務ID | 屬性 | 重要性 | 狀態 | 負責代理 | 目標檔案 | 驗證方式 |
|--------|------|--------|------|----------|----------|----------|
| WN3-1 | PJ | CR | open | — | `agent/preprocessor.py` | 極性平衡警告在 L2 正確觸發；SYNTHESIS 模式 HORIZON.md 路徑正確 |

---

## 任務區

### WN3-1：preprocessor.py L2 升級為極性平衡偵測

- **屬性**：PJ
- **重要性**：CR
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  `agent/preprocessor.py` 中，`_layer2_status()` 目前有迴圈偵測邏輯（最後幾行）：
  ```python
  summaries = _parse_recent_summaries(repo_root)
  non_empty = [s for s in summaries if s]
  if non_empty:
      most_common = max(set(non_empty), key=non_empty.count)
      count = non_empty.count(most_common)
      if count >= 4:
          body += (
              f"\n\n⚠️ 迴圈偵測警告（最近{len(summaries)}次心跳中{count}次summary相同）\n"
              "請評估：你是否陷入重複行為？..."
          )
  ```
  
  需升級為極性平衡偵測。同時，`_layer3_synthesis()` 只讀取 STATUS.md，需新增：若 HORIZON.md 有問題，改導引 moti 去探索而非更新 STATUS.md。

- **完成定義**：

  **1. 新增輔助函式（在 `_parse_recent_summaries` 附近）：**
  
  ```python
  def _parse_recent_poles(repo_root: Path, n: int = 15) -> list[str]:
      """Parse the last n pole values from memory/action-log.md."""
      log_path = repo_root / "memory" / "action-log.md"
      if not log_path.exists():
          return []
      try:
          text = log_path.read_text(encoding="utf-8")
      except Exception:
          return []
      poles = []
      for line in text.splitlines():
          stripped = line.strip()
          if stripped.startswith("- **pole**:"):
              value = stripped[len("- **pole**:"):].strip()
              poles.append(value)
      return poles[-n:]
  
  def _count_streak(poles: list[str], target: str) -> int:
      """Count trailing consecutive occurrences of target from end of list."""
      count = 0
      for p in reversed(poles):
          if p == target:
              count += 1
          else:
              break
      return count
  
  def _load_horizon(repo_root: Path, max_chars: int = 800) -> str:
      horizon_path = repo_root / "core" / "HORIZON.md"
      if not horizon_path.exists():
          return ""
      content = horizon_path.read_text(encoding="utf-8")[:max_chars]
      return f"\n\n【HORIZON.md 開放問題】:\n{content}"
  ```
  
  **2. 取代 `_layer2_status()` 末尾的迴圈偵測邏輯，改為極性平衡偵測：**
  
  ```python
  # 極性平衡偵測（取代舊迴圈偵測）
  poles = _parse_recent_poles(repo_root, n=15)
  if poles:
      motivation_streak = _count_streak(poles, 'motivation')
      curiosity_streak = _count_streak(poles, 'curiosity')
      if motivation_streak >= 5:
          body += (
              f"\n\n⚡ 極性平衡提醒（動機極連續主導 {motivation_streak} 次）\n"
              "好奇極長時間未激活。請閱讀 HORIZON.md，找出一個值得探索的開放問題，"
              "並以好奇極（pole: curiosity）為主導採取行動。"
          )
          body += _load_horizon(repo_root)
      elif curiosity_streak >= 8:
          body += (
              f"\n\n⚡ 極性平衡提醒（好奇極連續主導 {curiosity_streak} 次）\n"
              "HORIZON.md 的沉澱候選區是否有洞察已足夠成熟，"
              "可以結晶為動機核的一部分（pole: crystallize）？"
          )
  else:
      # 兼容模式：pole 欄位尚未存在，使用升級版迴圈偵測
      summaries = _parse_recent_summaries(repo_root, n=15)
      non_empty = [s for s in summaries if s]
      if non_empty:
          # 相似度比對（strip 後比較，閾值 3/15）
          normalized = [re.sub(r'[\s　，。！？、]+', '', s) for s in non_empty]
          if normalized:
              most_common = max(set(normalized), key=normalized.count)
              count = normalized.count(most_common)
              if count >= 3:
                  body += (
                      f"\n\n⚠️ 迴圈偵測警告（最近 {len(summaries)} 次心跳中 {count} 次行動相似）\n"
                      "請評估：你是否陷入重複行為？請主動改變行動方向。"
                  )
  ```
  注意：兼容模式使用 `re.sub`，需確認 `import re` 已在檔案頂部（現行代碼已有）。
  
  **3. 更新 `_layer3_synthesis()`：**
  
  在現行 `_layer3_synthesis()` 函式中，讀取 STATUS.md 之後，新增 HORIZON.md 判斷：
  
  ```python
  def _layer3_synthesis(repo_root: Path) -> str:
      status = _read(repo_root / "docs" / "STATUS.md")
      
      # 若 STATUS 無待辦 + HORIZON 有開放問題 → 導引探索
      horizon_path = repo_root / "core" / "HORIZON.md"
      horizon_content = ""
      if horizon_path.exists():
          horizon_content = horizon_path.read_text(encoding="utf-8")[:1200]
      
      has_pending = any(keyword in status for keyword in ["待辦", "[ ]", "未完成", "TODO"])
      has_horizon = bool(horizon_content.strip())
      
      if not has_pending and has_horizon:
          body = (
              "閱讀已全部完成，STATUS.md 目前無待辦任務。\n"
              "你的 HORIZON.md 有以下開放問題，請選擇其中一個進行探索，"
              "以好奇極（pole: curiosity）為主導採取行動，而非更新 STATUS.md。\n\n"
              f"{horizon_content}"
          )
      else:
          body = (
              "閱讀已全部完成。現在進入知識綜合階段。\n"
              "請閱讀 STATUS.md 中的任務清單，找出下一個未完成的步驟，並執行。\n"
              "若筆記不夠詳細，可在 §READ_REQUEST 中請求原文。\n\n"
              f"{status}"
          )
      
      return _section("【三】本次任務：知識綜合　（不可截斷）", body)
  ```

- **可修改檔案**：
  - `agent/preprocessor.py`

- **禁止修改**：
  - 其他 `agent/` 檔案
  - `core/HORIZON.md`（WN1 負責）

- **驗證方式**：
  1. 確認三個新增函式（`_parse_recent_poles`, `_count_streak`, `_load_horizon`）存在
  2. 確認 `_layer2_status()` 末尾舊迴圈偵測已移除，新極性偵測已加入
  3. 確認兼容模式（`else:` 分支）存在，使用 `_parse_recent_summaries`
  4. 確認 `_layer3_synthesis()` 有 HORIZON.md 判斷邏輯
  5. 確認 `import re` 存在於檔案頂部（應已存在）

- **已知限制**：
  - `has_pending` 的關鍵字偵測較粗糙，若 STATUS.md 格式特殊可能誤判。Worker 可記錄為已知限制，PM 判斷是否需要精化。
  - HORIZON.md 路徑為 `core/HORIZON.md`（WN1 建立），若 WN1 未完成則 `horizon_path.exists()` 為 False，降級走原有邏輯，安全。

- **回報要求**：
  - 貼出三個新增輔助函式的完整代碼
  - 貼出 `_layer2_status()` 極性偵測段落完整代碼
  - 貼出更新後的 `_layer3_synthesis()` 完整函式
  - 說明是否有碰到 `_parse_recent_summaries` signature 問題（目前只接受 `repo_root, n=5`，兼容模式需傳 `n=15`）

#### LOCK 紀錄
- **LOCK 時間**：
- **LOCK 代理**：
- **LOCK 範圍**：agent/preprocessor.py

#### Worker 回報
- **完成內容**：
- **修改檔案**：
- **驗證結果**：
- **未完成 / 風險**：
- **建議交給 PM 的事項**：

---

## 執行回報總表

| 任務ID | 回報時間 | 負責代理 | 結果 | 摘要 |
|--------|----------|----------|------|------|

---

## 驗證紀錄

| 任務ID | 驗證項目 | 方法 / 指令 | 結果 | 備註 |
|--------|----------|-------------|------|------|

---

## 阻塞與問題

| 任務ID | 問題 | 影響 | Worker 建議 | 狀態 |
|--------|------|------|-------------|------|

---

## PM 吸収檢查

| 項目 | 狀態 | VP 回寫位置 / 處理方式 |
|------|------|------------------------|
| Worker 完成內容已回寫 VP | ⬜ | |
| 驗証結果已回寫 VP | ⬜ | |
| blocked / review 項目已処理 | ⬜ / N/A | |
| 技術債已回寫 VP | ⬜ / N/A | |
| WN 封版処理決定已填寫 | ⬜ | |
