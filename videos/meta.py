"""產生每支影片的上傳資料（標題／說明／標籤）到 3.output/*.txt。

    python videos/meta.py

標題和說明的唯一來源是 design/sheet-rows-basics.tsv，這裡只負責排版成
可以直接複製貼上 YouTube 的格式；要改文案請改 tsv，不要改這支程式的輸出。
影片檔對應哪個條目寫在 trim.json 的 id 欄。
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "3.output"
TSV = ROOT.parent / "design" / "sheet-rows-basics.tsv"
SITE = "https://hkhorazon.github.io/UnityDictionary/"

# 每支都掛的頻道／系列標籤
COMMON = ["Unity", "Unity教學", "Unity字典", "Unity入門", "遊戲開發",
          "遊戲引擎", "Unity Tutorial", "game development"]

# 條目專屬標籤（tsv 的 keywords 是給網站搜尋用的英文，這裡補中文搜尋詞）
EXTRA = {
    "BA01": ["Unity Hub", "Unity安裝", "Unity下載", "LTS", "Unity Hub教學"],
    "BA02": ["Unity新專案", "Unity範本", "URP", "2D", "3D", "建立專案"],
    "BA03": ["Unity開啟專案", "Unity版本", "Unity升級", "Add project"],
}


def main() -> None:
    rows = {r["id"]: r for r in csv.DictReader(TSV.open(encoding="utf-8"), delimiter="\t")}
    trim = json.loads((ROOT / "trim.json").read_text(encoding="utf-8"))

    for name, cfg in trim.items():
        entry_id = cfg.get("id") if isinstance(cfg, dict) else None
        if not entry_id:
            continue   # 跳過 _comment 這種非設定的鍵
        row = rows[entry_id]
        raw_tags = COMMON + EXTRA.get(entry_id, []) + row["keywords"].split(";")
        seen: dict[str, str] = {}   # 大小寫不同視為同一個標籤，保留先出現的寫法
        for t in (t.strip() for t in raw_tags):
            if t:
                seen.setdefault(t.casefold(), t)
        tags = list(seen.values())
        body = f"""【{entry_id}】{row['title']}

── 標題 ──
{row['title']}｜Unity字典 {entry_id}

── 說明 ──
{row['description']}

完整條目：{SITE}?id={entry_id}
Unity字典是一本查閱用的圖鑑，每支短片只講一個 Unity 功能。

── 標籤 ──
{", ".join(tags)}

── 字幕 ──
{Path(name).stem}.srt（上傳時選繁體中文）
"""
        dst = OUT / (Path(name).stem + ".txt")
        dst.write_text(body, encoding="utf-8")
        print(f"→ {dst}")


if __name__ == "__main__":
    main()
