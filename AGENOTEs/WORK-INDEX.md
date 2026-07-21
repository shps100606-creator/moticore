# AGENOTE 工作狀態索引

> 用途：回答「現在有哪些工作線／任務支線還活著」。NOTE/PAPER/PLAN 保存記憶與理由；本檔保存行動狀態。Session 啟動時先讀本檔，再決定要不要回頭讀相關筆記。

---

## 狀態定義

| 狀態 | 意義 | Session 啟動行為 |
|------|------|----------------|
| candidate | 有討論過，但尚未決定進入工作 | 不主動推進；使用者問候選工作時列出 |
| active | 目前可直接執行 | 主動提報 |
| waiting | 等待外部資訊、使用者、部署或時間結果 | 提報阻塞條件，不硬做 |
| paused | 明確暫停，未來可能恢復 | 不主動推進；除非使用者點名或恢復條件成立 |
| done | 已完成 | 不提報；查歷史時可引用 |
| dropped | 明確決定不做 | 不提報；避免重啟同一支線 |
| reference | 只作知識參考，不是工作 | 不提報；查資料時可引用 |

---

## 工作線

| 工作ID | 名稱 | 狀態 | 下一步 | 狀態原因 / 恢復條件 | 關聯文件 | 更新日 |
|--------|------|------|--------|----------------------|----------|--------|
| WORK_260709_001 | moticore v0.8.0：重複貼文 bug 修復 + Giscus 回覆機制 | done | 無（技術任務本身已完成驗證）| PR #47 已合併進 main（`b3e898d`），手動觸發心跳（run 29022498124）驗證成功：job log 顯示 `[issues] Giscus reply posted`，`giscus-replied.json` 正確寫入，D1/D2 均在 production 驗證通過 | [[NOTE_MEET_260709_001]]、[[AGENOTEs/VPs/v0.8.0/VP.md]]、[[AGENOTEs/VPs/v0.8.0/WN1.md]] | 260709 |
| WORK_260709_002 | moticore v0.8.0：繼續觀察後再決定封版 | dropped | 無（被 WORK_260721_002 取代） | 觀察期間 dissolve 極持續 0 次觸發、Giscus 機制因無新留言無法驗證長期穩定性，兩項指標都還沒等到結論；260721 使用者判斷專案整體產出價值有限，直接決定暫停，不再等待這兩項觀察收斂 | [[AGENOTEs/VPs/v0.8.0/VP.md]]、[[NOTE_MEET_260721_001]] | 260721 |
| WORK_260721_001 | moticore 心跳 git push race 修復：雙 cron 合併為單一 cron | done | 無 | 追查使用者提供的 Actions 失敗截圖，確認 `.github/workflows/heartbeat.yml` 雙 cron 在排程延遲追趕時偶爾同時觸發、造成 git push 被拒（07-18~21 樣本 60 次執行中發生 2 次）；已合併為單一 cron `*/30 * * * *`，commit `1dc3281`，PR 待開 | [[NOTE_MEET_260721_001]] | 260721 |
| WORK_260721_002 | moticore 專案暫停：停用心跳自動排程 | paused | 使用者主動要求恢復時，取消註解 `.github/workflows/heartbeat.yml` 的 `schedule:` 區塊即可重啟；恢復後 WORK_260709_002 觀察的兩項指標（dissolve 極、Giscus 長期穩定性）需重新起算觀察期 | 使用者 260721 判斷「這個專案運作到現在，幾乎沒有產生任何意義」，決定直接暫停，不再繼續走封版／新版規劃流程 | [[NOTE_MEET_260721_001]]、[[AGENOTEs/VPs/v0.8.0/VP.md]] | 260721 |

---
