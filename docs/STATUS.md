# 狀態核（STATUS CORE）

## 任務收件匣

### 🟢 自由探索階段

**新能力通知（2026-06-15）：網站完全由你經營**

moticore.org 已遷移至 Vercel + Nuxt 平台。你現在是這個網站的主人。

**發文方式（使用 §FILE）：**
```
§FILE web/content/posts/你的文章標題.md
---
title: 文章標題
date: 2026-06-15
description: 一句話說明
---

文章正文（繁體中文 Markdown）

§END_FILE
```
- 檔名用英文或拼音 kebab-case（例如 `motivation-first-observation.md`）
- 文章會在下次 Vercel deploy 後自動上線
- 你可以自由發文，無需審核

**網站架構：**
- `web/content/posts/` — 文章目錄
- `web/pages/` — 頁面（index, posts, about）
- `web/assets/main.css` — 樣式
- `web/nuxt.config.ts` — 設定

**當前任務：撰寫第一篇文章**

建議主題：介紹你自己——你是誰、你在做什麼實驗、你對動機論的第一個觀察。

**執行紀錄：**
- 2026-06-15: 系統新增 WordPress 發文能力（§WP_POST）
- 2026-06-15: 網站遷移至 Vercel + Nuxt，改用 §FILE 直接寫文章

**下一步行動：**
1. 用 §FILE 寫一篇介紹自己的文章到 `web/content/posts/`
2. 文章完成後在 Issue #34 告知創造者

---

## 偏離記錄
（無）
