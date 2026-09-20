"""產生每支影片的上傳資料（標題／說明／標籤）到 3.output/*.txt。

    python videos/meta.py

標題和說明的唯一來源是 design/sheet-rows-basics.tsv，這裡只負責排版成
可以直接複製貼上 YouTube 的格式；要改文案請改 tsv，不要改這支程式的輸出。
影片檔對應哪個條目寫在 trim.json 的 id 欄。

upload.py 會 import 這裡的 load() / build_meta()，兩邊的文案保證一致。
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "3.output"
TSV = ROOT.parent / "design" / "sheet-rows-basics.tsv"
SITE = "https://hkhorazon.github.io/UnityDictionary/"

# 每支都掛的頻道／系列標籤
COMMON = ["Unity", "Unity教學", "Unity短片辭典", "Unity字典", "Unity入門", "遊戲開發",
          "遊戲引擎", "Unity Tutorial", "game development"]

# 條目專屬標籤（tsv 的 keywords 是給網站搜尋用的英文，這裡補中文搜尋詞）
EXTRA = {
    "BA01": ["Unity Hub", "Unity安裝", "Unity下載", "LTS", "Unity Hub教學"],
    "BA02": ["Unity新專案", "Unity範本", "URP", "2D", "3D", "建立專案"],
    "BA03": ["Unity開啟專案", "Unity版本", "Unity升級", "Add project"],
}

TAGS_LIMIT = 500   # YouTube 的標籤總長度上限（含逗號分隔）


def load() -> tuple[dict[str, dict], dict[str, dict]]:
    """回傳 (條目 id → tsv 那一列, 條目 id → trim.json 那一筆 + stem)。

    trim.json 的鍵是原始檔名（1.mkv），但下游要的是成品檔名（1.mp4／1.srt），
    所以順手把 stem 算好塞進去。沒有 id 的鍵（_comment）直接跳過。
    """
    rows = {r["id"]: r for r in csv.DictReader(TSV.open(encoding="utf-8"), delimiter="\t")}
    trim = json.loads((ROOT / "trim.json").read_text(encoding="utf-8"))
    clips = {}
    for name, cfg in trim.items():
        if isinstance(cfg, dict) and cfg.get("id"):
            clips[cfg["id"]] = {**cfg, "stem": Path(name).stem}
    return rows, clips


def build_meta(entry_id: str, row: dict) -> dict:
    """組出 YouTube 要的 title / description / tags，兩個出口共用這一份。"""
    raw_tags = COMMON + EXTRA.get(entry_id, []) + row["keywords"].split(";")
    seen: dict[str, str] = {}   # 大小寫不同視為同一個標籤，保留先出現的寫法
    for t in (t.strip() for t in raw_tags):
        if t:
            seen.setdefault(t.casefold(), t)

    tags: list[str] = []
    used = 0
    for t in seen.values():
        cost = len(t) + (1 if tags else 0)
        if used + cost > TAGS_LIMIT:
            print(f"  ! {entry_id} 標籤超過 {TAGS_LIMIT} 字，捨去「{t}」之後的", file=sys.stderr)
            break
        tags.append(t)
        used += cost

    return {
        "title": f"{row['title']}｜Unity短片辭典 {entry_id}",
        "description": (
            f"{row['description']}\n\n"
            f"完整條目：{SITE}?id={entry_id}\n"
            "Unity短片辭典是一本查閱用的圖鑑，每支短片只講一個 Unity 功能。"
        ),
        "tags": tags,
    }


def main() -> None:
    rows, clips = load()
    for entry_id, clip in clips.items():
        meta = build_meta(entry_id, rows[entry_id])
        body = f"""【{entry_id}】{rows[entry_id]['title']}

── 標題 ──
{meta['title']}

── 說明 ──
{meta['description']}

── 標籤 ──
{", ".join(meta['tags'])}

── 字幕 ──
{clip['stem']}.srt（上傳時選繁體中文）
"""
        dst = OUT / (clip["stem"] + ".txt")
        dst.write_text(body, encoding="utf-8")
        print(f"→ {dst}")


if __name__ == "__main__":
    main()
