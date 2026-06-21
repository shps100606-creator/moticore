# v0.4.0 Work Note — WN2（前端 + 身份：Giscus 元件 + MOTIVE.md）

## 文件狀態

- **專案**：shps100606-creator/moticore
- **版本**：v0.4.0
- **WN 識別**：WN2
- **對應 VP**：`_docs/versions/v0.4.0/VP.md`
- **WN 狀態**：active
- **建立者（PM）**：Claude Code（PM session 2026-06-21）
- **建立時間**：2026-06-21
- **封版處理**：delete

---

## Worker 規則

Worker 可以修改：`web/components/GiscusComments.vue`（新建）、`web/pages/posts/[...slug].vue`、`core/MOTIVE.md`，以及自己任務的 WN 回報區。

Worker 不得修改：主 VP、WN1.md、`agent/` 任何檔案、`web/pages/index.vue`、`web/pages/about.vue`、`web/pages/posts/index.vue`、`web/nuxt.config.ts`、`web/assets/`、`web/content/`、`core/constitution.md`、`core/forbidden.md`、`core/identity.md`、`core/prime-motive.md`、`core/boundary.md`。

---

## 任務看板

| 任務ID | 屬性 | 重要性 | 狀態 | 負責代理 | 目標檔案 | 驗證方式 |
|--------|------|--------|------|----------|---------|---------|
| WN2-1 | PJ | PR | done | Claude Code | web/components/GiscusComments.vue（新建）、web/pages/posts/[...slug].vue | Vue 語法正確，元件在 slug.vue 中被引入 |
| WN2-2 | PJ | CR | done | Claude Code | core/MOTIVE.md | diff 確認只有「操作邊界」段落被修改 |

---

## 任務區

### WN2-1：Giscus 前端留言元件

- **屬性**：PJ
- **重要性**：PR
- **狀態**：done
- **負責代理**：Claude Code

- **任務輸入**：（見 WN 原始規格）

- **完成定義**：已完成，見 Worker 回報。

- **可修改檔案**：
  - `web/components/GiscusComments.vue`（新建）
  - `web/pages/posts/[...slug].vue`

- **禁止修改**：`web/` 內上述兩個檔案以外的所有檔案；`agent/`；`core/`；`.github/`

- **已知限制**：
  - `data-repo-id` 和 `data-category-id` 必須使用 PLACEHOLDER，創造者後續需：
    1. 在 repo Settings → General → Features 啟用 GitHub Discussions
    2. 前往 giscus.app，填入 `shps100606-creator/moticore`，取得設定碼
    3. 將取得的 `data-repo-id`、`data-category`、`data-category-id` 填入 `GiscusComments.vue`

#### LOCK 紀錄
- **LOCK 時間**：2026-06-21
- **LOCK 代理**：Claude Code（Worker session）
- **LOCK 範圍**：web/components/GiscusComments.vue（新建）；web/pages/posts/[...slug].vue — 加入 `<GiscusComments />`

#### Worker 回報
- **完成內容**：
  1. 新建 `web/components/GiscusComments.vue`：Vue 3 Composition API（`<script setup>`）；`onMounted` 中動態建立 `<script>` 標籤，設定所有 Giscus data-* 屬性後 append 到 `ref="container"` 的 `.giscus` div；三個 PLACEHOLDER 值等待創造者填入（data-repo-id、data-category、data-category-id）。
  2. 修改 `web/pages/posts/[...slug].vue`：在 `<div class="article-body">` 閉合標籤後加入 `<GiscusComments />`；Nuxt 3 自動 import components/，無需手動 import 語句。
- **修改檔案**：`web/components/GiscusComments.vue`（新建）、`web/pages/posts/[...slug].vue`
- **驗證結果**：GiscusComments.vue template 語法正確（單根元素 div.giscus）✅；script setup 使用 Vue 3 `ref` + `onMounted`✅；slug.vue 正確引入 `<GiscusComments />`✅；Nuxt 3 SSR 安全（script 在 onMounted client-side 建立，不在 SSR 執行）✅
- **未完成 / 風險**：三個 PLACEHOLDER 值必須由創造者填入後 Giscus 才能正常顯示留言。填入前訪問文章頁，Giscus 會顯示錯誤提示但不影響文章本體渲染。
- **建議交給 PM 的事項**：
  - **創造者待辦（必須）**：
    1. GitHub repo → Settings → General → Features → 勾選 Discussions
    2. 瀏覽器前往 giscus.app，填入 `shps100606-creator/moticore`，選擇 mapping=pathname、category（建議新建「Comments」分類）
    3. 複製取得的 `data-repo-id`、`data-category`、`data-category-id` 三個值
    4. 在 `web/components/GiscusComments.vue` 中將對應 PLACEHOLDER 替換為實際值

---

### WN2-2：MOTIVE.md 加入 Giscus 感知說明

- **屬性**：PJ
- **重要性**：CR
- **狀態**：done
- **負責代理**：Claude Code

- **任務輸入**：（見 WN 原始規格）

- **完成定義**：已完成，見 Worker 回報。

- **可修改檔案**：`core/MOTIVE.md`

- **禁止修改**：`core/constitution.md`、`core/forbidden.md`、`core/identity.md`、`core/prime-motive.md`、`core/boundary.md`；`agent/` 任何檔案；`web/` 任何檔案

#### LOCK 紀錄
- **LOCK 時間**：2026-06-21
- **LOCK 代理**：Claude Code（Worker session）
- **LOCK 範圍**：core/MOTIVE.md — 操作邊界段落末尾新增一行

#### Worker 回報
- **完成內容**：在 `## 操作邊界` 段落最後一條（`- 不得發起對外部服務的請求（GitHub API 與 Vercel 部署除外）`）後新增：
  ```
  - 讀者留言（Giscus）：若有人在 moticore.org 文章頁留言，留言內容會由系統整理至 `memory/giscus-comments.md`。可用 §READ_REQUEST 讀取此檔案了解讀者回饋。文件樹中出現此檔案代表有新留言。
  ```
  其他所有段落（我是誰、使命、根本動機、閱讀的方式、價值排序、行動憲法、禁止行為）均未修改。
- **修改檔案**：`core/MOTIVE.md`
- **驗證結果**：只有操作邊界末尾新增一行✅；使命/根本動機/禁止行為/行動憲法均未變動✅；`§READ_REQUEST` 語法與現行 agent 一致✅；`memory/giscus-comments.md` 路徑與 WN1-4 實作一致✅
- **未完成 / 風險**：無
- **建議交給 PM 的事項**：無

---

## 執行回報總表

| 任務ID | 回報時間 | 負責代理 | 結果 | 摘要 |
|--------|----------|----------|------|------|
| WN2-2 | 2026-06-21 | Claude Code | done | MOTIVE.md 操作邊界末尾加入 Giscus 感知說明一行；其他段落未動 |
| WN2-1 | 2026-06-21 | Claude Code | done | 新建 GiscusComments.vue（onMounted 動態注入 Giscus script）；slug.vue 加入 `<GiscusComments />`；三個 PLACEHOLDER 待創造者填入 |

---

## 驗證紀錄

| 任務ID | 驗證項目 | 方法 | 結果 | 備註 |
|--------|----------|------|------|------|
| WN2-2 | 只新增一行於操作邊界末尾 | diff 審查：其他段落字元數不變 | ✅ 正確 | |
| WN2-2 | §READ_REQUEST 語法正確 | 與現行 preprocessor 解析格式一致 | ✅ 正確 | |
| WN2-2 | giscus-comments.md 路徑一致 | 與 WN1-4 run.py 寫入路徑相同 | ✅ 一致 | |
| WN2-1 | GiscusComments.vue 語法正確 | 單根元素、script setup、ref+onMounted | ✅ 正確 | |
| WN2-1 | SSR 安全（client-only script） | onMounted 確保 script 僅 client-side 執行 | ✅ 安全 | |
| WN2-1 | slug.vue 正確引入元件 | `<GiscusComments />` 在 article-body 後 | ✅ 正確 | |
| WN2-1 | Nuxt 3 auto-import 相容 | components/ 目錄下，Nuxt 自動 import | ✅ 相容 | |

---

## 阻塞與問題

| 任務ID | 問題 | 影響 | Worker 建議 | 狀態 |
|--------|------|------|-------------|------|

---

## PM 吸收檢查

| 項目 | 狀態 | VP 回寫位置 |
|------|------|-------------|
| Worker 完成內容已回寫 VP | ⬜ | |
| 驗證結果已回寫 VP | ⬜ | |
| blocked / review 項目已處理 | ⬜ / N/A | |
| 技術債已回寫 VP | ⬜ / N/A | |
| WN 封版處理決定已填寫 | ⬜ | |

---

## 封版處理

| 項目 | 狀態 | 說明 |
|------|------|------|
| WN 是否刪除 | ⬜ | 計畫刪除 |
| WN 是否壓縮歸檔 | N/A | |
| WN 是否保留並寫明原因 | N/A | |
