---
name: ship-local
description: "啟動本地靜態伺服器，回報可瀏覽的網址，並檢查專案有無嚴重缺失。當使用者輸入 /ship-local 時使用。"
---

# Ship Local

啟動本地伺服器並審查專案狀態。

## 步驟

### 1. 確認可用的靜態伺服器指令

依序嘗試，找到第一個可用的：

```bash
# 優先：npx serve（不需全域安裝）
npx --yes serve . --listen 8080 &

# 備用：python
python -m http.server 8080 &
```

記錄實際使用的指令與 port。

### 2. 啟動伺服器（背景執行）

用 Bash 工具以 `run_in_background: true` 啟動伺服器。等待 1-2 秒讓 port 就緒。

### 3. 回報網址

直接輸出：

```
本地伺服器已啟動：http://localhost:8080
```

### 4. 審查專案（同步執行）

檢查以下項目，找出**嚴重缺失**：

**A. 檔案完整性**
```bash
# 確認 index.html 存在
ls index.html 2>/dev/null || echo "MISSING: index.html"

# 確認 JS/CSS 引用的檔案都存在（掃描 index.html 中的 src/href）
```

**B. JSON 資料**
```bash
# 確認 data/entries.json 存在且為合法 JSON
python -c "import json; json.load(open('data/entries.json'))" 2>&1 || echo "INVALID: data/entries.json"
```

**C. Console 錯誤（靜態分析）**
- 掃描 JS 檔案，找出明顯的語法錯誤（未閉合括號、undefined 變數等）
- 掃描 HTML，確認所有 `<script src>` 與 `<link href>` 路徑存在

**D. GitHub Pages 相容性**
- 確認無絕對路徑（如 `src="/"`開頭但非根目錄的引用）
- 確認無需要後端的 API 呼叫

### 5. 輸出結果

格式：

```
本地伺服器已啟動：http://localhost:8080

嚴重缺失：
- [列出問題，若無則寫「無」]
```

只列**嚴重**問題（會導致頁面空白、功能完全無法使用）。小問題不列出。
