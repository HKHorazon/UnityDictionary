# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Unity字典 (Unity Dictionary)** — A static GitHub Pages website that serves as a reference dictionary for Unity features. Each entry contains a YouTube short video + a brief description teaching one small Unity concept. Users can browse by category and search entries.

## Tech Stack

- **Vite + Vue 3** (Composition API, `<script setup>`)
- **Tailwind CSS v4** (via `@tailwindcss/vite` plugin, no config file needed)
- Hosted on **GitHub Pages**，push to `main` → GitHub Actions 自動 build + deploy

## Architecture

```
src/
  App.vue           # 根元件，負責 filter/search state
  main.js           # 掛載入口
  style.css         # 只含 @import "tailwindcss"
  data/
    entries.json    # 所有字典條目（直接 import 進 Vue）
.github/workflows/
  deploy.yml        # push main → vite build → GitHub Pages
design/             # 設計稿（不部署）
```

### entries.json schema

```json
[
  {
    "id": "unique-slug",
    "title": "Entry title",
    "category": "Lighting",
    "tags": ["baked", "GI"],
    "youtubeId": "VIDEO_ID",
    "description": "一兩句說明。"
  }
]
```

### Key interactions

- 資料：直接 `import entries from './data/entries.json'`（無需 fetch）
- Search：filter by `title` + `description` + `tags`（case-insensitive）
- Category filter：reactive state 控制，"全部" 顯示所有
- YouTube embed：`https://www.youtube.com/embed/VIDEO_ID` 放在 `<iframe>`

## Development

```bash
npm run dev    # 本地開發伺服器
npm run build  # 產生 dist/（GitHub Actions 會自動執行）
```

## GitHub Pages Deployment

Remote: `https://github.com/HKHorazon/UnityDictionary.git`  
Push to `main` branch; configure GitHub Pages to serve from root (`/`) of `main`.

## 回覆風格

直接給結果，不要前言、不要總結。使用工具後只回報結果，不描述過程。除非使用者主動問，否則不解釋在做什麼。程式碼保持完整，其他回覆保持簡短。

使用者可以用任何語言提問，但回覆一律使用**繁體中文**。

若執行過程中發現潛在的錯誤、漏洞或效能問題，在結果後簡短列出，讓使用者決定是否處理。
