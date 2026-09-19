"""把 videos/3.output/*.mp4 轉成同名的 *.srt（逐字稿草稿，仍需人工校對）。

用法：
    python videos/transcribe.py             # 轉 3.output 底下全部影片
    python videos/transcribe.py 1.mp4       # 只轉指定檔案

一定要對 3.output 的成品做，不是對 1.raw 的原始檔——去頭去尾之後時間軸
已經位移了，拿原始檔的時間軸做出來的字幕會整段對不上。

轉錄結果會存一份 *.words.json，之後只改斷句規則的話會直接重用它，
不必再花好幾分鐘重跑一次 whisper。影片重新剪過就要把 words.json 刪掉重轉。

常用詞與錯字替換寫在 glossary.txt（格式見該檔開頭）。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "3.output"
PROC = ROOT / "2.process"
GLOSSARY = ROOT / "glossary.txt"
SCRIPTS = ROOT.parent / "design" / "video-scripts-basics.md"
TSV = ROOT.parent / "design" / "sheet-rows-basics.tsv"

# 每個 30 秒區段都會帶上這段提示：逼它輸出繁體中文，並優先用字集裡的寫法
HEADER = "以下是 Unity 教學影片的繁體中文旁白。常見詞彙："
# 提示詞和輸出共用 448 個 token，提示太長會把長句的輸出擠斷，留一半以上給輸出
HOTWORDS_BUDGET = 120

_gpu_failed = False

# 一行字幕的上限：手機上大約就是這個長度，超過就換一句
MAX_CHARS = 18
MAX_SECONDS = 5.0
BREAK_AFTER = "，。、！？；：,.!?;:"
LATIN = re.compile(r"[A-Za-z0-9]")


def to_wav(src: Path) -> Path:
    wav = PROC / (src.stem + ".wav")
    if not wav.exists():
        subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(src), "-vn",
             "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", "-y", str(wav)],
            check=True,
        )
    return wav


def load_glossary() -> tuple[list[str], list[tuple[str, str]]]:
    """回傳 (常用詞, [(錯, 對)])。"""
    terms: list[str] = []
    fixes: list[tuple[str, str]] = []
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=>" in line:
            wrong, right = (x.strip() for x in line.split("=>", 1))
            fixes.append((wrong, right))
        else:
            terms.append(line)
    return terms, fixes


def entry_text(video: Path) -> str:
    """這支影片對應條目的腳本段落 + tsv 那一列，用來挑出這支會講到的詞。"""
    trim = json.loads((ROOT / "trim.json").read_text(encoding="utf-8"))
    entry = (trim.get(video.stem + ".mkv") or {}).get("id")
    if not entry:
        return ""
    m = re.search(rf"^## {entry} .*?(?=^---)", SCRIPTS.read_text(encoding="utf-8"), re.M | re.S)
    row = next((l for l in TSV.read_text(encoding="utf-8").splitlines() if l.startswith(entry + "	")), "")
    return (m.group(0) if m else "") + row


def hotwords(tokenizer, video: Path, terms: list[str]) -> str:
    """這支條目講到的詞排前面，其餘照字集順序，塞到預算滿為止。"""
    text = entry_text(video).casefold()
    ordered = sorted(terms, key=lambda t: t.casefold() not in text)  # sorted 是穩定排序
    out = HEADER
    for t in ordered:
        nxt = out + t + "、"
        if len(tokenizer.encode(" " + nxt, add_special_tokens=False).ids) > HOTWORDS_BUDGET:
            break
        out = nxt
    return out.rstrip("、") + "。"


def transcribe(video: Path) -> list[dict]:
    """回傳 [{start, end, word}]，並快取成 *.words.json。"""
    cache = PROC / (video.stem + ".words.json")
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))

    from faster_whisper import WhisperModel

    wav = to_wav(video)
    print(f"轉錄 {video.name} ...", flush=True)

    # ponytail: CUDA 的 dll 要到真的推論時才會炸，所以連跑完都包在 try 裡。
    # 要快一點就把 large-v3 換成 medium。
    terms, _ = load_glossary()

    def run(device: str, compute_type: str) -> list[dict]:
        model = WhisperModel("large-v3", device=device, compute_type=compute_type)
        hints = hotwords(model.hf_tokenizer, video, terms)
        print(f"  提示：{hints}", flush=True)
        segments, _ = model.transcribe(
            str(wav),
            language="zh",
            # initial_prompt 只有第一個 30 秒區段看得到；hotwords 每段都會帶。
            # 不接上一段的文字，提示詞才不會被擠掉，也比較不會鬼打牆重複同一句。
            hotwords=hints,
            condition_on_previous_text=False,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 400},
            beam_size=5,
            word_timestamps=True,
        )
        return [
            {"start": w.start, "end": w.end, "word": w.word}
            for seg in segments for w in (seg.words or [])
        ]

    # CUDA 失敗過一次後，同一個 process 再試會直接卡死（不報錯、CPU 0%），所以只試一次
    global _gpu_failed
    words = None
    if not _gpu_failed:
        try:
            words = run("cuda", "float16")
        except Exception as e:
            _gpu_failed = True
            print(f"  GPU 不可用（{type(e).__name__}: {e}），改用 CPU", flush=True)
    if words is None:
        words = run("cpu", "int8")

    cache.write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    return words


def _text(ws: list[dict]) -> str:
    return "".join(w["word"] for w in ws).strip()


def _tidy(s: str) -> str:
    s = re.sub(r"[,](?=[^\s])", "，", s)                   # whisper 會吐半形逗號
    s = re.sub(r"(?<=[一-鿿])([A-Za-z0-9])", r" \1", s)   # 中→英 補空格
    s = re.sub(r"([A-Za-z0-9])(?=[一-鿿])", r"\1 ", s)    # 英→中 補空格
    return s.strip(BREAK_AFTER + " ")                              # 行尾不留標點


def _clauses(words: list[dict]):
    """先依標點切成子句——斷句一定要落在子句邊界，不然會切出「範／本」。"""
    cur: list[dict] = []
    for w in words:
        cur.append(w)
        if w["word"].strip()[-1:] in BREAK_AFTER:
            yield cur
            cur = []
    if cur:
        yield cur


def _split_long(clause: list[dict]) -> list[list[dict]]:
    """單一子句本身就超長時，切成幾段長度相近的，且不切在英數字中間。"""
    n = -(-len(_text(clause)) // MAX_CHARS)
    if n <= 1:
        return [clause]
    target = len(_text(clause)) / n
    out: list[list[dict]] = []
    cur: list[dict] = []
    for i, w in enumerate(clause):
        cur.append(w)
        nxt = clause[i + 1]["word"].strip()[:1] if i + 1 < len(clause) else ""
        t = _text(cur)
        if t and LATIN.match(t[-1]) and nxt and LATIN.match(nxt):
            continue  # 英數字詞中間不斷開，免得 Google 被切成 Go / ogle
        if len(t) >= target and len(out) < n - 1:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def fix(s: str, fixes: list[tuple[str, str]]) -> str:
    # ponytail: 以一行字幕為單位替換，錯字剛好跨兩行就抓不到，那種手動改
    for wrong, right in fixes:
        s = s.replace(wrong, right)
    return s


def to_cues(words: list[dict]):
    """把子句貪心地打包成一行字幕，超過長度、時間或停頓太久就換行。"""
    chunks = [c for cl in _clauses(words) for c in _split_long(cl)]
    cue: list[dict] = []
    for ch in chunks:
        merged = cue + ch
        overflow = bool(cue) and (
            len(_text(merged)) > MAX_CHARS
            or merged[-1]["end"] - merged[0]["start"] > MAX_SECONDS
            or ch[0]["start"] - cue[-1]["end"] > 0.8   # 中間停很久就別黏在一起
        )
        if overflow:
            yield cue[0]["start"], cue[-1]["end"], _tidy(_text(cue))
            cue = ch
        else:
            cue = merged
    if cue and _tidy(_text(cue)):
        yield cue[0]["start"], cue[-1]["end"], _tidy(_text(cue))


def ts(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> None:
    PROC.mkdir(exist_ok=True)
    names = sys.argv[1:]
    videos = [OUT / n for n in names] if names else sorted(OUT.glob("*.mp4"))
    if not videos:
        print("3.output/ 裡沒有影片，先跑 build.py")
        return

    _, fixes = load_glossary()
    for video in videos:
        cues = [(a, b, _tidy(fix(t, fixes))) for a, b, t in to_cues(transcribe(video))]  # 替換後再補一次中英空格
        body = "\n".join(
            f"{i}\n{ts(start)} --> {ts(end)}\n{text}\n"
            for i, (start, end, text) in enumerate(cues, 1)
        )
        srt = OUT / (video.stem + ".srt")
        srt.write_text(body, encoding="utf-8")
        for start, _, text in cues:
            print(f"  [{start:6.1f}] {text}", flush=True)
        print(f"  → {srt}")


def _selftest() -> None:
    def w(t, s):
        return {"start": t, "end": t + 0.3, "word": s}
    words = [w(0, "你"), w(.3, "可以"), w(.6, "用"), w(.9, "Go"), w(1.2, "ogle"),
             w(1.5, "帳號"), w(1.8, "，"), w(2.1, "或"), w(2.4, "蘋果")]
    cues = list(to_cues(words))
    # Google 沒被切兩半、中英之間補空格、行尾不留標點；短子句會併成同一行
    assert cues[0][2] == "你可以用 Google 帳號，或蘋果", cues

    # 超長子句要切在長度相近的地方，不能切出「範／本」那種孤字
    long = [w(i * .3, c) for i, c in enumerate("這邊會有各種不一樣的範本像是手機等等")]
    parts = [c[2] for c in to_cues(long)]
    assert all(len(p) >= 6 for p in parts), parts

    assert fix("打開 Unity Hop 之後", [("Unity Hop", "Unity Hub")]) == "打開 Unity Hub 之後"
    print("ok")


if __name__ == "__main__":
    _selftest() if "--selftest" in sys.argv else main()
