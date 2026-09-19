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

6. **上傳 YouTube** — 影片用 `3.output/*.mp4`，字幕上傳校對過的 `*.srt`，
   標題說明標籤照 `*.txt`。

7. **回填** — 把影片 ID 填進 `design/sheet-rows-basics.tsv` 的 `youtubeId` 欄，
   整張表貼回 Google Sheet（網站是從 sheet 動態抓的，貼完就更新，不用重 build）。

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
