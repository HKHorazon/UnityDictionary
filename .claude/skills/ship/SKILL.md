---
name: ship
description: "推送前先審查專案嚴重問題，確認後才 commit + push 到 GitHub，最後驗證線上版本真的更新且匿名訪客看得到。當使用者輸入 /ship 時使用。"
---

# Ship

推送到 GitHub 前的檢查、推送、部署驗證。

專案是 **Vite + Vue 3**，資料**不在 repo 裡**，是前端即時抓 Google Sheets 的 gviz
端點。所以光檢查檔案存不存在沒有意義，`npm run build` 過了也不代表網站活著——
資料來源掛掉或共用權限改掉，build 一樣會過，但訪客只會看到「資料載入失敗」。

## 1. 審查嚴重問題

### A. 入口與設定檔

```bash
for f in index.html vite.config.js package.json src/main.js src/App.vue \
         src/style.css src/data/constants.json .github/workflows/deploy.yml; do
  [ -f "$f" ] && echo "  ok   $f" || echo "  MISSING: $f"
done
```

### B. JSON 合法性

```bash
for f in src/data/constants.json src/data/keywords.json package.json; do
  python -c "import json,sys; json.load(open(sys.argv[1],encoding='utf-8')); print('  ok  ', sys.argv[1])" "$f" \
    || echo "  BAD: $f"
done
```

### C. build 必須過

```bash
npm run build
```

### D. 產出的引用路徑要帶 `/UnityDictionary/` 前綴

GitHub Pages 開在子路徑下，少了前綴整站會白畫面。`vite.config.js` 的
`base: '/UnityDictionary/'` 負責這件事，驗證產出而不是驗證設定：

```bash
grep -oE '(src|href)="[^"]*"' dist/index.html
```

`assets/` 那幾條都必須是 `/UnityDictionary/assets/...`。

### E. 沒有 localhost 或後端呼叫

```bash
grep -rnE "localhost|127\.0\.0\.1" src/ --include=*.vue --include=*.js
```

### F. 資料來源匿名讀得到（最容易漏掉的一項）

網站前端是**匿名**打 gviz 的。你自己在瀏覽器開得起來，是因為你登入了 Google，
完全不能當作訪客也看得到。一定要用不帶 cookie 的請求驗：

```bash
URL=$(python -c "import json,pathlib;print(json.loads(pathlib.Path('src/data/constants.json').read_text(encoding='utf-8'))['sheetsUrl'])")
curl -s "$URL" | head -c 60
```

開頭要看到 `/*O_o*/` 和 `google.visualization.Query.setResponse(`。
看到 HTML 或 `<!DOCTYPE` 就是**權限沒開**，試算表要設成
「知道連結的任何人／檢視者」。

順便確認網址結尾有 **`&headers=1`**。少了它 gviz 不會把第一列當表頭，
回傳的欄位 label 全是空字串，`parseGviz()` 取不到 `id`，
最後被 `.filter(e => e.id)` 濾光，整站變成「找不到符合的條目」。

## 2. 若有嚴重問題 → 中斷

```
發現嚴重問題，已中斷推送：

- [問題描述]
- [問題描述]

請修復後再執行 /ship。
```

**立即停止，不繼續後續步驟。**

## 3. 收集 git 資訊

```bash
git branch --show-current
git log origin/$(git branch --show-current)..HEAD --oneline
git status --short
git remote get-url origin
```

順手確認憑證沒被追蹤（有動到 `videos/` 時特別重要）：

```bash
git check-ignore -v videos/client_secret.json videos/.youtube-token.json
```

兩個都要印得出對應的 `.gitignore` 規則。任何一個沒被 ignore 就**立刻中斷**。

## 4. 產生 commit 訊息建議

依 `git diff HEAD` 的內容生成繁體中文訊息：第一行動詞開頭的摘要，
改動不只一件事時空一行後用 `-` 列點。commit 訊息結尾加上：

```
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```

## 5. 詢問使用者確認

```
準備推送：

- Branch：main
- 遠端：https://github.com/HKHorazon/UnityDictionary.git
- 未 commit 變更：3 個檔案
- 建議 commit 訊息：「…」

確認推送？(輸入 y 確認 / 任何其他內容取消)
```

等待使用者回覆。不是 `y` / `yes` 就輸出「已取消推送。」並停止。

若 `git status` 乾淨且沒有未推送的 commit，不要問，直接跳到第 7 步驗證線上狀態。

## 6. 推送

```bash
git add -A
git commit -m "建議的訊息"
git push origin $(git branch --show-current)
```

## 7. 驗證真的部署上去了

**不要只說「1-2 分鐘後會更新」就結束。** 比對線上的 bundle hash 與本機 build，
一致才是新版（Vite 的 hash 由內容決定，內容一樣 hash 就一樣）：

```bash
LOCAL=$(grep -oE 'assets/index-[A-Za-z0-9_-]+\.js' dist/index.html)
for i in $(seq 1 24); do
  LIVE=$(curl -s "https://hkhorazon.github.io/UnityDictionary/" | grep -oE 'assets/index-[A-Za-z0-9_-]+\.js')
  [ "$LIVE" = "$LOCAL" ] && { echo "已部署：$LIVE"; break; }
  sleep 15
done
```

接著用**全新的瀏覽器 context**（沒有你的 Google 登入狀態）確認訪客看到的畫面，
這是唯一能抓到「共用權限沒開」的檢查：

```python
from playwright.sync_api import sync_playwright

URL = "https://hkhorazon.github.io/UnityDictionary/"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    for w, h in [(1920, 1080), (390, 844)]:
        ctx = b.new_context(viewport={"width": w, "height": h})
        pg = ctx.new_page()
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(URL)
        pg.wait_for_load_state("networkidle")
        pg.wait_for_timeout(2000)
        print(f"{w}x{h}: cards={pg.locator('.t-card').count()} "
              f"aside={pg.locator('.side-nav').is_visible()} "
              f"hero={pg.locator('.hero').is_visible()} "
              f"載入失敗={pg.get_by_text('資料載入失敗').count() > 0} "
              f"err={errs or 'none'}")
        ctx.close()
    b.close()
```

`cards` 要等於試算表裡有 `youtubeId` 的筆數，`載入失敗` 要是 `False`，
`err` 要是 `none`。桌機 `aside` 為 True、手機為 False。

## 8. 回報

```
已推送至 https://github.com/HKHorazon/UnityDictionary.git (main)

檢查：build ok / 路徑前綴 ok / 資料來源匿名可讀 ok
部署：assets/index-xxxx.js 與本機一致
實測：桌機 3 張卡、手機 3 張卡，無 console error

網址：https://hkhorazon.github.io/UnityDictionary/
```

---

## 已知問題與注意事項

### 網站空白／「找不到符合的條目」

九成是 Google Sheet 那端，不是程式碼：

1. `sheetsUrl` 少了 `&headers=1` → 欄位 label 全空，`parseGviz()` 取不到 `id`
2. 試算表共用權限不是「知道連結的任何人」→ 訪客拿不到資料
3. 換過試算表但 `src/data/constants.json` 的 `sheetsUrl` 沒跟著改

三個都用第 1 步的 F 項驗得出來。

### 資料要怎麼更新

不要手動貼試算表，用：

```bash
python videos/upload.py --sheet
```

它只會寫入 `youtubeId` 欄是合法 11 碼的條目。詳見 `videos/README.md`。

### GitHub Actions `npm ci` 失敗（跨平台 lock file 衝突）

**症狀**：CI 失敗，`npm ci can only install packages when your package.json and
package-lock.json are in sync`，缺少 `@emnapi/core` 或 `@emnapi/runtime`。

**原因**：本地 Windows 與 CI（Node 24 / Linux）對 `@emnapi` 這類原生模組會解析出
不同的 optional dependency 版本，造成 lock file 不同步。

**修法**：`.github/workflows/deploy.yml` 的 `npm ci` 改成 `npm install`，
`node-version` 升到 24，`upload-pages-artifact` 升到 v4。（目前已經是這個狀態。）
