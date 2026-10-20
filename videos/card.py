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
h1 {{ font-size: 104px; font-weight: 700; margin: 28px 0 44px; line-height: 1.15; }}
ol {{ font-size: 40px; line-height: 1.6; color: #b1bac4; margin: 0; padding-left: 1.4em; }}
ol b {{ color: #e6edf3; }}
img {{ width: 560px; border-radius: 24px; border: 2px solid #86efac33; }}
</style>
<div class="text">
  <div class="label">Unity短片辭典</div>
  <h1>{title}</h1>
  {body}
</div>
{thumb}
"""

# 投影片的條列內容：(標題, [清單每一行])，清單用 <b>…</b> 標粗體。
# 照影片實際講的內容寫；沒寫到的條目會把 tsv 說明照句號拆成條列頂著用。
CUSTOM: dict[str, tuple[str, list[str]]] = {
    "BA01": ("下載與安裝 Unity Hub", [
        "<b>搜尋 Unity</b>：到官網找「下載」",
        "<b>登入帳號</b>：Email、Google、Apple 都可以",
        "<b>選系統</b>：Windows 就下載 Windows 版",
        "<b>執行安裝</b>：裝好會有白色的 Unity Hub",
        "<b>Hub 是管理器</b>：Unity 編輯器之後再從 Hub 裝",
    ]),
    "BA02": ("建立新專案", [
        "<b>打開 Unity Hub</b>：白色的那個圖示",
        "<b>New Project</b>：選範本，推薦 2D 或 3D",
        "<b>上方選版本</b>：看你裝了哪幾種",
        "<b>專案名稱</b>：自己取，例如 Project1",
        "<b>存放位置</b>：會在裡面再建一個資料夾",
        "<b>Create</b>：按下去就開始建立",
    ]),
    "BA03": ("開啟既有專案與版本", [
        "<b>清單裡有</b>：點一下就打開",
        "<b>清單裡沒有</b>：按 Add 從硬碟加入",
        "<b>選對資料夾</b>：看得到 Assets 的那一層",
        "<b>換版本</b>：開啟前可以在清單裡改",
        "<b>跳出警告</b>：代表這個版本你沒裝",
    ]),
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
    "BA06": ("移動、旋轉、縮放", [
        "<b>Transform</b>：每個物件都有，管位置、旋轉、縮放",
        "<b>打數字</b>：欄位可以直接打算式，例如 1+2",
        "<b>移動工具</b>：拖箭頭，點小方塊可在平面上移動",
        "<b>縮放</b>：預設 1、1、1，鎖頭鎖住就等比例",
        "<b>旋轉</b>：數值是角度，超過 360 會自動換算",
        "<b>第六個工具</b>：移動、旋轉、縮放一次搞定",
    ]),
    "BA07": ("匯入素材", [
        "<b>放哪裡</b>：Project 的 Assets 資料夾，不是 Packages",
        "<b>先分類</b>：開資料夾整理，之後才好找",
        "<b>右鍵匯入</b>：Import New Asset 選檔案",
        "<b>直接拖</b>：檔案拖進視窗，可以框選一起拖",
        "<b>匯入設定</b>：點素材，Inspector 依需求調整",
        "<b>預覽</b>：聲音、影片在下方直接看",
    ]),
    "BA08": ("Asset Store 商店", [
        "<b>Asset Store</b>：買素材、模板，也有很多免費的",
        "<b>登入</b>：用你的 Unity 帳號就好",
        "<b>Add to My Assets</b>：先加到帳號，付費的要先購買",
        "<b>Download → Import</b>：下載完還要匯入才會進專案",
        "<b>Package Manager</b>：In Project、Unity Registry、My Assets",
        "<b>Built-in／Services</b>：內建功能與雲端存檔等服務",
    ]),
}


def render(row: dict) -> Path:
    """回傳投影片 PNG 的路徑。"""
    CARDS.mkdir(parents=True, exist_ok=True)
    out = CARDS / f"{row['id']}.png"
    svg = THUMBS / row["thumb"]
    thumb = f'<img src="{svg.as_uri()}">' if row["thumb"].endswith(".svg") and svg.exists() else ""
    title, items = CUSTOM.get(row["id"]) or (
        row["title"], [html.escape(s) for s in row["description"].split("。") if s.strip()])
    body = "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"
    page = PAGE.format(thumb=thumb,
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
