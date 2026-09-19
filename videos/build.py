"""去頭去尾 + 音量正規化，1.raw/*.mkv → 3.output/*.mp4。

    python videos/build.py            # 全部
    python videos/build.py 1.mkv      # 只做指定的

切點寫在 trim.json；沒列到的檔案就整支照做，只正規化音量。
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
RAW = ROOT / "1.raw"
OUT = ROOT / "3.output"
TRIM = json.loads((ROOT / "trim.json").read_text(encoding="utf-8"))

TARGET = "I=-14:TP=-1.5:LRA=11"   # YouTube 的播放響度標準


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
    names = sys.argv[1:]
    videos = [RAW / n for n in names] if names else sorted(RAW.glob("*.mkv"))
    for src in videos:
        cfg = TRIM.get(src.name, {})
        start, end = float(cfg.get("start", 0)), cfg.get("end")
        m = measure(src, start, end)
        dst = OUT / (src.stem + ".mp4")
        span = f"{start}s → {end or '結尾'}"
        print(f"{src.name}: 保留 {span}，{m['input_i']} LUFS → -14 LUFS", flush=True)
        # ponytail: 切點不在關鍵格上，所以影像一定要重編；crf 18 對螢幕錄影是視覺無損
        subprocess.run(
            ["ffmpeg", "-v", "error", "-ss", str(start),
             *(["-to", str(end)] if end else []), "-i", str(src),
             "-af", f"loudnorm={TARGET}:"
                    f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                    f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                    f"offset={m['target_offset']}:linear=true",
             "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-y", str(dst)],
            check=True,
        )
        print(f"  → {dst}")


if __name__ == "__main__":
    main()
