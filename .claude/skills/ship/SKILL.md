---
name: ship
description: "推送前先審查專案嚴重問題，確認後才 commit + push 到 GitHub。當使用者輸入 /ship 時使用。"
---

# Ship

推送專案到 GitHub 前的安全檢查與確認流程。

## 步驟

### 1. 審查嚴重問題

同步執行以下檢查：

**A. 檔案完整性**
```bash
ls index.html 2>/dev/null || echo "MISSING: index.html"
ls data/entries.json 2>/dev/null || echo "MISSING: data/entries.json"
```

**B. JSON 合法性**
```bash
python -c "import json; json.load(open('data/entries.json'))" 2>&1
```

**C. HTML 引用的 JS/CSS 路徑存在**
- 掃描 index.html 中的 `<script src>` 與 `<link href>`，確認對應檔案存在

**D. GitHub Pages 相容性**
- 無絕對路徑引用（`src="/"` 開頭）
- 無後端 API 呼叫

### 2. 若有嚴重問題 → 中斷

列出所有嚴重問題，輸出格式：

```
發現嚴重問題，已中斷推送：

- [問題描述]
- [問題描述]

請修復後再執行 /ship。
```

**立即停止，不繼續後續步驟。**

### 3. 若無嚴重問題 → 收集 git 資訊

執行以下指令：

```bash
# 目前 branch
git branch --show-current

# 與遠端的差異（未 push 的 commits）
git log origin/$(git branch --show-current)..HEAD --oneline 2>/dev/null || git log --oneline -5

# 未 commit 的變更
git status --short

# 遠端 URL
git remote get-url origin 2>/dev/null
```

### 4. 產生 commit 訊息建議

根據 `git diff --staged` 或 `git diff HEAD` 的內容，自動生成一個簡短的繁體中文 commit 訊息建議（一行，動詞開頭，例如「新增搜尋功能與分類篩選」）。

### 5. 詢問使用者確認

輸出格式：

```
準備推送：

- Branch：main
- 遠端：https://github.com/HKHorazon/UnityDictionary.git
- 未 commit 變更：3 個檔案
- 建議 commit 訊息：「新增首頁骨架與資料結構」

確認推送？(輸入 y 確認 / 任何其他內容取消)
```

等待使用者回覆。

### 6. 使用者確認後執行推送

若使用者回覆 `y` 或 `yes`：

```bash
git add -A
git commit -m "建議的訊息"
git push origin $(git branch --show-current)
```

推送成功後輸出：
```
已推送至 https://github.com/HKHorazon/UnityDictionary.git (main)
GitHub Pages 通常需要 1-2 分鐘更新。
```

若使用者回覆其他內容：
```
已取消推送。
```
