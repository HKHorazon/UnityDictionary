"""產生每支影片開頭的標題投影片（1920x1080 PNG）到 2.process/cards/。

    python videos/card.py              # tsv 裡全部條目
    python videos/card.py BA04 BA05    # 只做指定的

標題、說明、難度都從 design/sheet-rows-basics.tsv 來；thumb 是 public/thumbs/
底下的 svg 才會放圖，還是 emoji 的就只排文字。
用 Chrome headless 截圖，中文換行和字型交給瀏覽器處理。
build.py 出片時會自動呼叫這裡，平常不用手動跑，想先看投影片長怎樣再跑。
"""
import html
import subprocess
import sys
import tempfile
from pathlib import Path

from meta import TSV, csv

ROOT = Path(__file__).parent
CARDS = ROOT / "2.process" / "cards"
THUMBS = ROOT.parent / "public" / "thumbs"
CHROME = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
]

PAGE = """<!doctype html><meta charset="utf-8"><style>
html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; }}
body {{
  background: radial-gradient(ellipse at 70% 45%, #16243a 0%, #0d1117 65%);
  color: #e6edf3; font-family: "Noto Sans TC", "Microsoft JhengHei", sans-serif;
  display: flex; align-items: center; gap: 96px; padding: 0 160px; box-sizing: border-box;
}}
.text {{ flex: 1; }}
.label {{ color: #86efac; font-size: 34px; font-weight: 700; letter-spacing: 0.12em; }}
.lv {{ display: inline-block; margin-left: 20px; padding: 2px 16px; border-radius: 999px;
       border: 2px solid #86efac66; background: #22c55e22; font-size: 26px; vertical-align: 4px; }}
h1 {{ font-size: 104px; font-weight: 700; margin: 28px 0 44px; line-height: 1.15; }}
p {{ font-size: 40px; line-height: 1.7; color: #b1bac4; margin: 0; }}
ol {{ font-size: 40px; line-height: 1.6; color: #b1bac4; margin: 0; padding-left: 1.4em; }}
ol b {{ color: #e6edf3; }}
img {{ width: 560px; border-radius: 24px; border: 2px solid #86efac33; }}
</style>
<div class="text">
  <div class="label">Unity短片辭典 · {id}<span class="lv">Lv. {difficulty}</span></div>
  <h1>{title}</h1>
  {body}
</div>
{thumb}
"""

# 投影片想跟網站文案不一樣時寫在這裡：(標題, [清單每一行])，清單用 <b>…</b> 標粗體
CUSTOM: dict[str, tuple[str, list[str]]] = {
    "BA04": ("Unity六大基本介面", [
        "<b>Scene</b> 場景：製作者編輯用的畫面",
        "<b>Game</b> 遊戲：玩家看到的畫面",
        "<b>Hierarchy</b> 階層：場景裡的所有物件",
        "<b>Project</b> 專案：對應硬碟的 Assets 資料夾",
        "<b>Inspector</b> 檢查器：選中東西的詳細資料",
        "<b>Console</b> 主控台：程式和系統的訊息",
    ]),
    "BA05": ("Scene 場景視窗", [
        "<b>滑鼠</b>：滾輪縮放、右鍵旋轉、左鍵選取",
        "<b>座標方塊</b>：一點就切到上方、正面等視角",
        "<b>手掌工具</b>：拖曳平移畫面",
        "<b>雙擊物件</b>：鏡頭直接飛過去",
        "<b>眼睛／Gizmos</b>：暫時隱藏，只影響編輯畫面",
        "<b>繪製模式</b>：Shaded、Wireframe、2D 模式",
    ]),
}


def render(row: dict) -> Path:
    """回傳投影片 PNG 的路徑。"""
    CARDS.mkdir(parents=True, exist_ok=True)
    out = CARDS / f"{row['id']}.png"
    svg = THUMBS / row["thumb"]
    thumb = f'<img src="{svg.as_uri()}">' if row["thumb"].endswith(".svg") and svg.exists() else ""
    if row["id"] in CUSTOM:
        title, items = CUSTOM[row["id"]]
        body = "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"
    else:
        title, body = row["title"], f"<p>{html.escape(row['description'])}</p>"
    page = PAGE.format(id=row["id"], difficulty=row["difficulty"], thumb=thumb,
                       title=html.escape(title), body=body)
    chrome = next((c for c in CHROME if c.exists()), None)
    if not chrome:
        sys.exit("找不到 Chrome 或 Edge，card.py 需要其中一個來截圖")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "card.html"
        src.write_text(page, encoding="utf-8")
        subprocess.run(
            [str(chrome), "--headless", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--window-size=1920,1080",
             f"--screenshot={out}", src.as_uri()],
            check=True, capture_output=True,
        )
    return out


def main() -> None:
    rows = list(csv.DictReader(TSV.open(encoding="utf-8"), delimiter="\t"))
    wanted = set(sys.argv[1:])
    for row in rows:
        if not wanted or row["id"] in wanted:
            print(render(row))


if __name__ == "__main__":
    main()
