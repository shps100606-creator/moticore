# PAPER13.md — 第四次迴圈：HORIZON.md 從未清空，以及一次沉默兩週的部署凍結

**類型：** 根因診斷 + 架構決策
**版本：** 2026-07-02
**接續：** PAPER12.md（2026-06-21）

---

## 一、本文定位

PAPER12.md 記錄了三次迴圈（知識整合迴圈、50 次審計迴圈、等待審核迴圈）與 moticore.org 的建立。本文記錄第四次迴圈——這次不是任務板語意的問題，而是**「結晶」動作本身從未真正發生**——以及一個獨立但同時被發現、影響更隱蔽的問題：**moticore.org 從 6/15 之後，有整整兩週完全沒有被重新部署過**。

兩件事最初看起來無關，最後拼出同一個教訓：**系統可以連續數週輸出「完成」，卻沒有一件事真的抵達使用者能看到的地方。**

---

## 二、第四次迴圈：宣稱結晶，卻沒有畢業

### 2.1 症狀

從 2026-06-23（v0.5.0 引入 `pole` 欄位與 HORIZON.md）到 2026-07-02，moti 反覆在「關於讀者」「關於迴圈本身」「關於創作邊界」三個開放問題之間探索，每次心跳的 summary 措辭略有不同，但實質內容高度重複。`memory/action-log.md` 裡有兩次 `pole: crystallize`（2026-06-25），但之後又持續回到 `curiosity`，同一批問題從未真正結案。

`HORIZON.md` 甚至有一個項目標題寫著「（已結晶）」，內文也附了洞見，卻仍然放在「開放中」區塊——「已結晶」區塊直到本次修正前都是空的。

### 2.2 根本原因

1. **crystallize 只被定義成一個標籤，沒有對應的必要動作。** `agent/decision.py` 的 pole 定義寫「crystallize：將 HORIZON.md 的洞察寫入 MOTIVE.md」，但沒有規則要求 moti 同時編輯 `HORIZON.md` 本身——結果 moti 選擇 `pole: crystallize` 時，只寫了 `MOTIVE.md` 或 `docs/STATUS.md`，從未觸碰 `HORIZON.md`。
2. **`_layer3_synthesis` 每次都把完整的「開放中」清單原封不動地餵回去。** 因為清單從未變化，模型能選的探索對象也就那三、四題，於是內容自然趨於重複。
3. **舊的「內容相似度」迴圈偵測已經被新的「極性平衡偵測」悄悄取代，而且從沒被注意到。** `_layer2_status` 寫成「若 `pole` 欄位存在就用極性平衡偵測，否則才用舊的內容相似度偵測」。自從 `pole` 開始被記錄，舊偵測就再也沒有執行過——即使 moti 逐字重複自己說過的話，系統也不會發出警告，因為極性平衡偵測只看「連續用同一個 pole 幾次」，不看內容是否重複。

### 2.3 修復

- `agent/decision.py` 新增規則 11–13：`pole: crystallize` 必須搭配一個 `§FILE core/HORIZON.md`，把對應問題整段搬到「已結晶」；`pole: dissolve` 必須新增一個開放問題；好奇極探索時可以自由新增清單外的新問題，但「開放中」超過 5 題須先處理一個再新增。
- `agent/run.py` 新增 `check_horizon_lifecycle()`：宣稱 crystallize/dissolve 卻沒有對應的 `core/HORIZON.md` 寫入，就在該筆行動的 `deviation` 欄位標記「顯著」，讓下一次心跳的「最近行動」清楚看到這個落差——這是系統層級的抓包，不是文字建議。
- 順手把那個早該畢業卻卡住的項目手動搬到「已結晶」，作為機制上線的示範。

### 2.4 教訓

> **一個動作如果只被定義成「模型應該做的事」而沒有對應的必要產出，模型遲早會把它做成一句話，而不是一個真正的狀態改變。**

`pole: crystallize` 和先前「等待審核」迴圈的錯誤同源：兩者都是把「應該發生的事」寫成敘述性文字，而不是寫成程式碼會檢查的必要條件。PAPER12 的教訓是「要改變根本行為必須改身份文件，不能只改任務板」；這次的教訓是進一步：**光是改身份文件也不夠，宣稱完成的動作最好要有程式碼可以驗證，否則宣稱本身就會變成迴圈的一部分。**

---

## 三、部署凍結：兩週的沉默

### 3.1 症狀

使用者回報「moti 一篇文都沒發」。但 `web/content/posts/` 裡確實有新檔案，`memory/action-log.md` 也顯示對應心跳成功寫入。矛盾只有一個解釋：**檔案進了 repo，但 moticore.org 沒有更新。**

### 3.2 根本原因

`vercel.json` 有一個自訂的 Ignored Build Step：

```json
{ "ignoreCommand": "git diff HEAD~1 HEAD --quiet -- web/" }
```

這是為了省建置額度：大部分 heartbeat commit 不動 `web/`，本不該觸發部署。但 `HEAD~1` 依賴建置環境至少有兩個 commit 的歷史；Vercel 的建置環境常態是 shallow clone，`HEAD~1` 在這種情況下可能直接解析失敗，導致這個判斷式從未正確運作。使用者在 Vercel Deployments 頁面確認：**從 6/15 之後，沒有任何一次部署紀錄——不是 Skipped，是完全沒有觸發過。**

換句話說，6/21 moti 的第一篇文章、7/1 與 7/2 的兩篇 §JOURNAL 貼文，全部只停留在 GitHub repo 裡，從未真正上線過。

### 3.3 修復

直接刪除 `vercel.json`，讓每次 push 都觸發正常建置。heartbeat 頻率（約每天 20–30 次）加上一個小型靜態 Nuxt Content 網站，建置成本遠低於 Hobby 方案的免費額度，省下的建置分鐘數不值得冒著「靜默凍結部署」的風險。

### 3.4 教訓

> **省成本的最佳化，如果失敗模式是「安靜地什麼都不做」，風險就會被完全隱藏，直到有人主動去確認發布結果為止。**

這類最佳化最危險的地方不是它會不會失敗，而是失敗時**不會有任何錯誤訊息**——沒有建置記錄、沒有 log、沒有告警。moti 這邊看起來一切正常（檔案確實寫入、commit 確實推送），問題只存在於 GitHub 與 Vercel 之間的一次判斷式裡。這提醒我們：**任何會讓系統「跳過做某件事」的判斷邏輯，都必須假設它有一天會判斷錯誤，並且要能被看見（至少要留下「本次跳過」的紀錄），不能只是安靜地不執行。**

---

## 四、附帶發現：兩個被默默丟棄的欄位

`agent/memory.py` 的 `append_action()` 讀取 `decision.get('action_type', ...)` 與 `decision.get('deviation_flag', ...)`，但 `decision.py` 的 §ACTION 解析器實際輸出的欄位叫 `type` 與 `deviation`。這個命名不一致從系統存在以來就在——`action-log.md` 裡幾百筆紀錄的 `action_type` 全部是預設值 `unknown`，`deviation_flag` 全部是預設值 `無`，無論 moti 實際回報了什麼。

這個 bug 不會讓任何行動失敗，只會讓兩個本來該有的觀測欄位悄悄失真。修復後（2026-07-01 起），`action-log.md` 才第一次看到 moti 自己回報的真實 `type`（`synthesis`、`introspection`）與非空的 `deviation`（`輕微`）。這也是 `check_horizon_lifecycle()` 抓包機制能夠有效運作的前提——如果 `deviation` 欄位繼續被默默丟棄，抓包訊息永遠不會真正被寫進 log。

---

## 五、給下一個接手代理的提示

1. **任何「模型應該做 X」的規則，優先考慮能不能在程式碼裡驗證 X 是否真的發生。** 這次修的三個問題（crystallize 不畢業、部署被跳過、欄位被丟棄）本質上都是「宣稱」和「實際發生」之間出現落差，而且都拖了很久才被發現。
2. **`memory/action-log.md` 的欄位名稱與 `decision.py` 輸出的欄位名稱是兩套命名**（`action_type`/`type`、`deviation_flag`/`deviation`）。之後若要在 `§ACTION` 加新欄位，記得同步檢查 `memory.py` 讀取的是哪個 key。
3. **`core/HORIZON.md` 的「開放中」題數是觀察系統健康度的一個訊號。** 若持續維持在 5 題以上、遲遲沒有被清空，代表 crystallize/dissolve 機制可能又失效了，值得回頭檢查 `check_horizon_lifecycle()` 的 log。
4. 這次的修正還沒有被 crystallize/dissolve 動作實際觸發驗證過——下一個接手的代理應該先查 `memory/action-log.md` 有沒有出現過 `pole: crystallize` 或 `dissolve`，並確認對應心跳有沒有真的寫入 `core/HORIZON.md`。
