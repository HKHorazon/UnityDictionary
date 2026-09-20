# 影片製作流程

```
videos/
  1.raw/       OBS 錄下的原始檔（*.mkv），不要動它
  2.process/   轉錄的中間檔（*.wav、*.words.json），可以隨時刪
  3.output/    成品：*.mp4 + *.srt + *.txt，上傳 YouTube 就用這一包
  trim.json    每支影片的去頭去尾秒數 + 對應的條目 ID
  build.py     去頭去尾 + 音量正規化
  transcribe.py  產字幕草稿
  meta.py      產標題／說明／標籤
  upload.py    上傳後套 meta + 傳字幕（影片檔要自己拖上 Studio）
```

## 步驟

1. **錄影** — 錄完丟進 `1.raw/`。

2. **標切點** — 在 `trim.json` 加一筆，寫下要保留的區間和對應的條目 ID：

   ```json
   "4.mkv": { "start": 1.5, "end": 88.0, "id": "BA04" }
   ```

   OBS 通常會在開頭和結尾各露出 1～4 秒（alt-tab 去按開始／停止錄影）。
   切點怎麼找見下面「找 OBS 切點」。

3. **出片** — 去頭去尾 + 把音量拉到 YouTube 標準：

   ```bash
   python videos/build.py            # 全部
   python videos/build.py 4.mkv      # 只做指定的
   ```

   輸出 `3.output/4.mp4`。錄出來通常只有 -43 LUFS，YouTube 標準是 -14，
   差快 30 dB，一定要跑這步。

4. **字幕** — 對 `3.output` 的成品轉錄（不是對原始檔，去頭之後時間軸已經位移）：

   ```bash
   python videos/transcribe.py
   ```

   輸出 `3.output/4.srt`。**這是草稿，一定要校對**：whisper 會把 Unity 專有
   名詞聽錯，聽不清楚的地方也會自己編一個相近的詞出來。

5. **上傳資料** — 產生標題／說明／標籤：

   ```bash
   python videos/meta.py
   ```

   輸出 `3.output/4.txt`，直接複製貼上 YouTube。文案的來源是
   `design/sheet-rows-basics.tsv`，要改文字改那裡，不要改 `meta.py`。

6. **上傳 YouTube** — 影片檔一定要自己在 Studio 拖上去，**不要用 API 傳**：
   未通過 Google 審核的 API 專案，用 `videos.insert` 傳的片會被永久鎖成私人，
   事後在 Studio 也改不回公開，只能整支重傳。

   拖 `3.output/*.mp4` 進 Studio → 先存成「私人」→ 從網址列抄下影片 ID
   （`studio.youtube.com/video/`**`這一段`**`/edit`）→ 貼進
   `design/sheet-rows-basics.tsv` 的 `youtubeId` 欄。

7. **套資料** — 標題／說明／標籤／字幕由程式推上去：

   ```bash
   python videos/upload.py            # tsv 裡有 youtubeId 的條目全做
   python videos/upload.py BA01 BA02  # 只做指定條目
   ```

   做完回 Studio 檢查一遍再按發布。`upload.py` 不碰隱私狀態，發布永遠是你手動按的。
   重跑是安全的：字幕軌同語言已存在就換內容，不會長出第二條。

8. **回填** — 上一步已經寫在 tsv 裡了，把整張表貼回 Google Sheet 就更新
   （網站是從 sheet 動態抓的，不用重 build）。

## 設定 YouTube API（只要做一次）

`upload.py` 第一次跑之前要生一組 OAuth 憑證：

1. 到 [Google Cloud Console](https://console.cloud.google.com/) 建一個專案。
2. 「API 和服務 > 程式庫」搜 **YouTube Data API v3**，按啟用。
3. 「API 和服務 > OAuth 同意畫面」選 **外部**，填應用程式名稱和你的信箱就好。
   然後到「目標對象」按 **發布應用程式**，把狀態從「測試中」改成「正式版」。

   這一步不是送審，app 還是未驗證狀態，授權畫面一樣會跳警告。差別在「測試中」
   發出來的 refresh token 只有 7 天壽命，每週都要重新授權一次；「正式版」沒有
   這個限制（未驗證的 app 上限 100 個使用者，自己用綽綽有餘）。

   要留在「測試中」也行，那就得在「目標對象」把自己的 Google 帳號加進測試使用者
   ——沒加會在授權時被 403 擋掉。
4. 「憑證 > 建立憑證 > OAuth 用戶端 ID」，類型選 **桌面應用程式**，下載 JSON。
5. 把下載的檔案改名成 `client_secret.json` 放進 `videos/`。

第一次執行會開瀏覽器要你登入授權，畫面會跳「Google 尚未驗證這個應用程式」，
按「進階 > 前往（不安全）」——那是你自己的專案，不是別人的。授權後 token 快取在
`videos/.youtube-token.json`，之後都不用再登入。兩個檔都在 `.gitignore` 裡，
**不要 commit**。

改過發布狀態的話要刪掉 `videos/.youtube-token.json` 重新授權一次，舊 token 不會
自動延長。想確認有沒有連對頻道就跑 `python videos/upload.py --check`。

配額：每天 10000 單位，`upload.py` 一支片大約花 450 單位，夠跑 20 支。

## 找 OBS 切點

**不要**用 `-ss` 快轉定位或 `fps=` 濾鏡取樣去判斷時間——OBS 錄的 mkv 是 VFR
而且封包順序是亂的（pts 會是 0.000 / 0.033 / 0.017 / 0.067），抓出來的畫面
對不上你以為的秒數，我已經被這個坑過一次。把時間戳燒在畫面上再看：

```bash
ffmpeg -i 1.raw/4.mkv -t 6.5 \
  -vf "select='not(mod(n,15))',scale=420:-2,drawtext=fontfile='C\:/Windows/Fonts/arialbd.ttf':text='%{pts\:hms}':x=8:y=8:fontsize=26:fontcolor=yellow:box=1:boxcolor=black@0.8" \
  -fps_mode passthrough head_%02d.jpg
```

結尾把 `-t 6.5` 換成 `-sseof -6.5`。切完記得再對 `3.output` 的成品驗一次
第一格和最後一格。

## 備註

- `transcribe.py` 用 large-v3 模型，首次執行會下載約 3GB（會佔滿頻寬一陣子）。
  要快一點就把程式裡的 `large-v3` 換成 `medium`。
- 沒有 GPU 就會自動退回 CPU，一支 90 秒的片大約要幾分鐘。
- `*.words.json` 是詞級時間軸的快取，只改斷句規則時會直接重用，不會重跑
  whisper。影片重新剪過就要刪掉它。
- 音量正規化會把底噪一起放大。根本解是錄音時就把麥克風增益開夠。
