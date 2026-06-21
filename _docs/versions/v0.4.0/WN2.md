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
| WN2-1 | PJ | PR | open | — | web/components/GiscusComments.vue（新建）、web/pages/posts/[...slug].vue | Vue 語法正確，元件在 slug.vue 中被引入 |
| WN2-2 | PJ | CR | open | — | core/MOTIVE.md | diff 確認只有「操作邊界」段落被修改 |

---

## 任務區

### WN2-1：Giscus 前端留言元件

- **屬性**：PJ
- **重要性**：PR
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  - `web/pages/posts/[...slug].vue` 當前完整內容：
    ```vue
    <template>
      <main class="article">
        <template v-if="post">
          <h1>{{ post.title }}</h1>
          <p class="meta">{{ post.date }} · {{ post.author || 'moti' }}</p>
          <div class="article-body">
            <ContentRenderer :value="post" />
          </div>
        </template>
      </main>
    </template>

    <script setup>
    const route = useRoute()
    const { data: post } = await useAsyncData(route.path, () =>
      queryContent(route.path).findOne()
    )
    </script>
    ```
  - Giscus 嵌入方式：在頁面中動態載入 `https://giscus.app/client.js`，帶有設定 data-* 屬性（詳見 giscus.app）。
  - 目標 repo 設定：
    - `data-repo="shps100606-creator/moticore"`
    - `data-mapping="pathname"`（Giscus 依頁面路徑對應 Discussion）
    - `data-theme="light"`
    - `data-lang="zh-TW"`
  - **需要創造者填入的值**（Worker 使用 PLACEHOLDER）：
    - `data-repo-id`：到 giscus.app 取得（需 GitHub 授權）
    - `data-category-id`：到 giscus.app 取得
    - `data-category`：Discussions 分類名稱

- **完成定義**：
  1. 新建 `web/components/GiscusComments.vue`：
     - 使用 Vue 3 Composition API（`<script setup>`）
     - 在 `onMounted` 中動態建立 `<script>` 標籤並設定所有 Giscus data-* 屬性，append 到留言容器 div
     - 留言容器：`<div class="giscus"></div>`
     - 注意：Nuxt 3 SSR 環境下，Giscus script 必須在 client-side 才能執行，使用 `onMounted` 而非直接在 template 中放 `<script>`
  2. 修改 `web/pages/posts/[...slug].vue`：
     - 在 `<div class="article-body">` 後加入 `<GiscusComments />` 元件
     - 若 Nuxt 3 不自動 import，需加入 `import GiscusComments from '~/components/GiscusComments.vue'`（Nuxt 3 通常自動 import components/，可省略）

- **可修改檔案**：
  - `web/components/GiscusComments.vue`（新建）
  - `web/pages/posts/[...slug].vue`

- **禁止修改**：`web/` 內上述兩個檔案以外的所有檔案；`agent/`；`core/`；`.github/`

- **驗證方式**：
  1. 確認 `GiscusComments.vue` 的 `<template>` 和 `<script setup>` 語法正確（無 Vue template error）。
  2. 確認 `[...slug].vue` 正確引入元件。
  3. （可選）在 `web/` 目錄執行 `npm run dev`，訪問文章頁，確認頁面底部出現 Giscus 載入嘗試（因 PLACEHOLDER 可能顯示 Giscus 錯誤，這是預期行為，不影響文章本體顯示）。

- **已知限制**：
  - `data-repo-id` 和 `data-category-id` 必須使用 PLACEHOLDER，創造者後續需：
    1. 在 repo Settings → General → Features 啟用 GitHub Discussions
    2. 前往 giscus.app，填入 `shps100606-creator/moticore`，取得設定碼
    3. 將取得的 `data-repo-id`、`data-category`、`data-category-id` 填入 `GiscusComments.vue`
  - Nuxt 3 的 `<ClientOnly>` wrapper 可選（Giscus 在 SSR 下不報錯，只是 script 不執行），但建議用 `onMounted` 方式確保 client-side only。

- **回報要求**：
  - `GiscusComments.vue` 完整代碼。
  - `[...slug].vue` 完整修改後代碼或 diff。
  - 創造者後續需完成的步驟清單（一條一條列出）。

#### LOCK 紀錄
- **LOCK 時間**：
- **LOCK 代理**：
- **LOCK 範圍**：

#### Worker 回報
- **完成內容**：
- **修改檔案**：
- **驗證結果**：
- **未完成 / 風險**：
- **建議交給 PM 的事項**：

---

### WN2-2：MOTIVE.md 加入 Giscus 感知說明

- **屬性**：PJ
- **重要性**：CR
- **狀態**：open
- **負責代理**：—

- **任務輸入**：
  - `core/MOTIVE.md` 當前「操作邊界」段落完整內容：
    ```markdown
    ## 操作邊界
    - 只能操作 shps100606-creator/moticore 倉庫
    - 可透過 GitHub Issues 與創造者溝通
    - 可透過 moticore.org（§FILE 寫入 web/）與外部世界溝通
    - 不得發起對外部服務的請求（GitHub API 與 Vercel 部署除外）
    ```
  - WN1-4 的機制：heartbeat 每次執行時會從 GitHub Discussions 抓取留言並寫入 `memory/giscus-comments.md`（若有留言）。
  - moti 目前知道的文件樹由 preprocessor 動態注入 Layer 2，`memory/giscus-comments.md` 只有在有留言時才會存在。

- **完成定義**：
  在 MOTIVE.md「操作邊界」段落的最後一行（`- 不得發起...`）**之後**，新增以下一條：
  ```markdown
  - 讀者留言（Giscus）：若有人在 moticore.org 文章頁留言，留言內容會由系統整理至 `memory/giscus-comments.md`。可用 §READ_REQUEST 讀取此檔案了解讀者回饋。文件樹中出現此檔案代表有新留言。
  ```
  **只加入這一條，不修改 MOTIVE.md 任何其他內容。**

- **可修改檔案**：`core/MOTIVE.md`

- **禁止修改**：`core/constitution.md`、`core/forbidden.md`、`core/identity.md`、`core/prime-motive.md`、`core/boundary.md`；`agent/` 任何檔案；`web/` 任何檔案

- **驗證方式**：
  1. 讀取修改後的 `core/MOTIVE.md`，確認：
     - 新增說明確實在「操作邊界」段落內（在 `## 禁止行為` 之前）
     - 使命（`## 我在做什麼`）、根本動機、禁止行為、行動憲法均未被改動
     - 整體字數合理（僅增加約一行）
  2. 確認 `§READ_REQUEST` 和 `memory/giscus-comments.md` 的路徑與 WN1-4 實作一致。

- **已知限制**：
  - WN1-4 完成前，`memory/giscus-comments.md` 不存在——MOTIVE.md 中的說明「文件樹中出現此檔案代表有新留言」能讓 moti 正確理解「不存在 = 無留言」，這是正確行為。
  - MOTIVE.md 是最高層級身份文件，任何超出「操作邊界新增一行」範圍的修改都必須 blocked 等 PM 確認。

- **回報要求**：
  - MOTIVE.md 修改 diff（只含「操作邊界」段落的變動）。
  - 確認其他段落未被修改。

#### LOCK 紀錄
- **LOCK 時間**：
- **LOCK 代理**：
- **LOCK 範圍**：

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
| WN2-1 | | | | |
| WN2-2 | | | | |

---

## 驗證紀錄

| 任務ID | 驗證項目 | 方法 | 結果 | 備註 |
|--------|----------|------|------|------|

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
