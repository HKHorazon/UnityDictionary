"""去頭去尾 + 音量正規化 + 開頭標題投影片，1.raw/N.mkv|mp4 → 3.output/N/N.mp4。

每支影片一個資料夾 3.output/N/，成品影片、字幕、上傳資料、投影片（N-card.png）都放在裡面。

    python videos/build.py            # 全部
    python videos/build.py 1.mkv      # 只做指定的

切點寫在 trim.json；沒列到的檔案就整支照做，只正規化音量。
trim.json 有 id 的才會加投影片：先靜音放 CARD_SECONDS 秒，再接影片。
有 cover 的話投影片會繼續蓋在影片上直到原始檔的 cover 秒（聲音照放），
拿來遮開頭露出的 OBS 畫面；cover_end 則是從那一秒起淡入蓋到結尾，遮結尾的 OBS。
cuts 是要剪掉的中間片段 [[開始, 結束], ...]（原始檔時間軸），畫面和聲音一起剪；
剪完字幕時間軸要跟著往前推，字幕要重轉或手動調整。

聲音先用 DeepFilterNet 去掉鍵盤聲和底噪（整支原始檔做一次，快取在 2.process/*.denoised.wav），
再做音量正規化。原始檔換過就把快取刪掉重做。
"""
import csv
import shutil
import json
import subprocess
import sys
from pathlib import Path

from card import render
from meta import TSV

ROOT = Path(__file__).parent
RAW = ROOT / "1.raw"
PROC = ROOT / "2.process"
OUT = ROOT / "3.output"
TRIM = json.loads((ROOT / "trim.json").read_text(encoding="utf-8"))

TARGET = "I=-14:TP=-1.5:LRA=11"   # YouTube 的播放響度標準
CARD_SECONDS = 4.0                 # 投影片單獨停留的秒數，字幕時間軸會跟著往後推這麼多
FADE = 0.4                         # 投影片淡出到影片的秒數

# DeepFilterNet 只有舊版 Python 裝得起來，用 uv 開一個 3.10 的臨時環境跑
DEEPFILTER = ["uv", "run", "-p", "3.10", "--with", "deepfilternet", "--with", "torch==2.1.2",
              "--with", "torchaudio==2.1.2", "--with", "soundfile", "deepFilter"]


def denoise(src: Path) -> Path:
    """整支原始檔的聲音去噪，回傳快取的 wav（時間軸跟原始檔一樣）。"""
    out = PROC / f"{src.stem}.denoised.wav"
    if out.exists():
        return out
    PROC.mkdir(exist_ok=True)
    wav = PROC / f"{src.stem}.noisy.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", "48000",
                    "-y", str(wav)], check=True)
    subprocess.run([*DEEPFILTER, str(wav), "-o", str(PROC)], check=True, capture_output=True)
    (PROC / f"{wav.stem}_DeepFilterNet3.wav").replace(out)
    wav.unlink()
    return out


def measure(src: Path, start: float, end: float | None) -> dict:
    """第一趟只量測，而且只量會留下來的那一段，不然被切掉的靜音會拉歪結果。"""
    cut = ["-ss", str(start)] + (["-to", str(end)] if end else [])
    log = subprocess.run(
        ["ffmpeg", "-hide_banner", *cut, "-i", str(src),
         "-af", f"loudnorm={TARGET}:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stderr
    return json.loads(log[log.rindex("{"):log.rindex("}") + 1])


def main() -> None:
    OUT.mkdir(exist_ok=True)
    rows = {r["id"]: r for r in csv.DictReader(TSV.open(encoding="utf-8"), delimiter="\t")}
    names = sys.argv[1:]
    videos = [RAW / n for n in names] if names else sorted([*RAW.glob("*.mkv"), *RAW.glob("*.mp4")])
    for src in videos:
        cfg = TRIM.get(src.name, {})
        start, end = float(cfg.get("start", 0)), cfg.get("end")
        audio = denoise(src)
        m = measure(audio, start, end)
        folder = OUT / src.stem
        folder.mkdir(parents=True, exist_ok=True)
        dst = folder / (src.stem + ".mp4")
        span = f"{start}s → {end or '結尾'}"
        print(f"{src.name}: 保留 {span}，{m['input_i']} LUFS → -14 LUFS", flush=True)
        norm = (f"loudnorm={TARGET}:"
                f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                f"offset={m['target_offset']}:linear=true")
        cut = ["-ss", str(start), *(["-to", str(end)] if end else [])]
        clip = [*cut, "-i", str(src)]

        if cfg.get("id") in rows:
            card = str(shutil.copy(render(rows[cfg["id"]]), folder / f"{src.stem}-card.png"))
            # 蓋在影片上的那段：到 cover 為止全不透明，之後 FADE 秒淡出；沒 cover 就只有淡出
            over = max(float(cfg.get("cover", start)) - start, 0) + FADE
            same = "fps=60,scale=1920:1080,setsar=1,format=yuv420p"
            inputs = [*clip,
                      "-loop", "1", "-framerate", "60", "-t", str(CARD_SECONDS), "-i", card,
                      "-loop", "1", "-framerate", "60", "-t", str(over), "-i", card]
            tail = ""
            if "cover_end" in cfg:
                # 結尾那段：從 cover_end 前 FADE 秒開始淡入，一路蓋到影片結束
                at = float(cfg["cover_end"]) - start - FADE
                stop = float(end) if end else float(subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                    capture_output=True, text=True, check=True).stdout)
                dur = stop - start - at
                inputs += ["-loop", "1", "-framerate", "60", "-t", str(dur), "-i", card]
                tail = (f"[3:v]format=rgba,fade=t=in:d={FADE}:alpha=1,setpts=PTS+{at}/TB[e];"
                        f"[m0][e]overlay=eof_action=pass[m1];")
            ai = inputs.count("-i")            # 去噪後的聲音接在最後一個輸入
            drop = "+".join(f"between(t,{a - start},{b - start})" for a, b in cfg.get("cuts", []))
            vcut = f",select='not({drop})',setpts=N/FRAME_RATE/TB" if drop else ""
            acut = f",aselect='not({drop})',asetpts=N/SR/TB" if drop else ""
            inputs += [*cut, "-i", str(audio)]
            graph = (
                f"[0:v]{same}[v];"
                f"[2:v]format=rgba,fade=t=out:st={over - FADE}:d={FADE}:alpha=1[o];"
                f"[v][o]overlay=eof_action=pass[m0];{tail or '[m0]null[m1];'}"
                f"[m1]{same}{vcut}[main];"
                f"[1:v]{same}[pre];"
                f"anullsrc=r=48000:cl=stereo,atrim=duration={CARD_SECONDS}[sil];"
                f"[{ai}:a]{norm},aresample=48000,aformat=channel_layouts=stereo{acut}[a];"
                f"[pre][sil][main][a]concat=n=2:v=1:a=1[vout][aout]"
            )
            filters = ["-filter_complex", graph, "-map", "[vout]", "-map", "[aout]"]
            print(f"  + 投影片 {CARD_SECONDS}s，蓋到影片第 {over:.1f}s", flush=True)
        else:
            inputs = [*clip, *cut, "-i", str(audio)]
            filters = ["-map", "0:v", "-map", "1:a", "-af", norm]

        # ponytail: 切點不在關鍵格上，所以影像一定要重編；crf 18 對螢幕錄影是視覺無損
        subprocess.run(
            ["ffmpeg", "-v", "error", *inputs, *filters,
             "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-y", str(dst)],
            check=True,
        )
        print(f"  → {dst}")


if __name__ == "__main__":
    main()
