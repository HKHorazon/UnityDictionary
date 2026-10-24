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
    "BA10": ("燈光與天空", [
        "<b>Directional Light</b>：直射光模擬太陽，只看角度不看位置",
        "<b>Point Light</b>：點光源，從一點照亮附近",
        "<b>Spot Light</b>：探照燈，照出一個錐形",
        "<b>Area Light</b>：區域光，要烘焙才看得到",
        "<b>天空的光</b>：Window > Rendering > Lighting 調環境光",
        "<b>Light Explorer</b>：所有燈光集中一起調",
    ]),
    "BA09": ("Material 材質球", [
        "<b>建立</b>：Project 右鍵 Create > Material",
        "<b>Shader</b>：決定材質怎麼畫，URP 預設用 Lit",
        "<b>顏色與貼圖</b>：調 Base Map 的顏色，或放上圖片",
        "<b>套用</b>：拖到場景物件、Hierarchy 或 Inspector 上",
        "<b>共用</b>：同一個材質會一起改，要不同顏色就再建一個",
    ]),
    "BA11": ("相機與 Game 視窗", [
        "<b>Main Camera</b>：它拍到的就是玩家看到的畫面",
        "<b>多台相機</b>：可以有好幾台，標成 MainCamera 的為主",
        "<b>Align With View</b>：相機直接對齊目前的 Scene 視角",
        "<b>背景</b>：沒東西的地方可以用天空或純色",
        "<b>Projection</b>：透視調 FOV，正交調框框大小",
        "<b>最近距離</b>：太靠近相機的東西拍不到（預設 0.3）",
    ]),
}

# 還沒錄的章節先放草稿，給錄影時參考要講什麼；錄完照影片實際內容寫進 CUSTOM 蓋過去
DRAFT: dict[str, tuple[str, list[str]]] = {
    "BA12": ("第一支腳本", [
        "<b>建立</b>：Project 右鍵 Create > MonoBehaviour Script",
        "<b>檔名＝class 名</b>：改名要兩邊一起改",
        "<b>Start</b>：物件出現時跑一次",
        "<b>Update</b>：每一格畫面都跑一次",
        "<b>掛上物件</b>：沒掛在物件上的腳本不會執行",
        "<b>Debug.Log</b>：在 Console 印出訊息",
    ]),
    "BA13": ("Prefab 預製物件", [
        "<b>製作</b>：把 Hierarchy 的物件拖回 Project",
        "<b>藍色</b>：名字變藍就是 Prefab",
        "<b>大量複製</b>：從 Project 拖出來，都是同一個模子",
        "<b>改 Prefab</b>：雙擊進入編輯，所有複本一起變",
        "<b>單獨修改</b>：在場景上直接改，改過的欄位變粗體",
    ]),
    "BA14": ("父子關係", [
        "<b>建立</b>：在 Hierarchy 把 A 拖到 B 上",
        "<b>相對座標</b>：子物件的 Transform 相對於父物件",
        "<b>跟著動</b>：父物件移動、旋轉、縮放，子物件跟著走",
        "<b>空物件當資料夾</b>：把零件收在一起",
        "<b>小心縮放</b>：父物件 Scale 不是 1，子物件會變形",
    ]),
    "BA15": ("Animation 動畫", [
        "<b>Animation 視窗</b>：Window > Animation > Animation",
        "<b>Create</b>：建立 Animation Clip，自動加上 Animator",
        "<b>錄製</b>：在不同時間點改數值，記成關鍵影格",
        "<b>Curves</b>：調整動作的快慢曲線",
        "<b>關掉錄製</b>：不然之後的修改也會被錄進去",
        "<b>位置被拉回</b>：包一層父物件再移動",
    ]),
    "BA16": ("UI Canvas 與按鈕", [
        "<b>建立 UI</b>：右鍵 UI，自動建好 Canvas、EventSystem",
        "<b>Canvas</b>：放 UI 的畫布，切 2D 模式比較好看",
        "<b>Rect Transform</b>：Anchor 決定黏在螢幕哪個角",
        "<b>Button</b>：On Click 綁定要執行的函式",
        "<b>Canvas Scaler</b>：Scale With Screen Size 等比例縮放",
    ]),
    "BA17": ("3D 碰撞", [
        "<b>Rigidbody</b>：讓物件受重力和物理影響",
        "<b>Collider</b>：決定碰撞的形狀",
        "<b>碰撞條件</b>：兩邊都要 Collider，一邊要 Rigidbody",
        "<b>OnCollisionEnter</b>：撞到時執行，知道撞到誰",
        "<b>Is Trigger</b>：可穿過的感應區，用 OnTriggerEnter",
        "<b>不要硬搬</b>：有 Rigidbody 就不要直接改 Transform",
    ]),
    "BA18": ("2D 碰撞", [
        "<b>2D 元件</b>：Rigidbody 2D、Box Collider 2D",
        "<b>2D 函式</b>：OnCollisionEnter2D、OnTriggerEnter2D",
        "<b>不能混用</b>：2D 和 3D 物理不會互相碰撞",
        "<b>沒反應也不報錯</b>：先檢查元件和函式有沒有 2D",
        "<b>Freeze Rotation Z</b>：角色不會被撞得轉圈",
    ]),
    "BA19": ("Tilemap 2D 地圖", [
        "<b>建立</b>：2D Object > Tilemap > Rectangular",
        "<b>Tile Palette</b>：把切好的圖拖進去變成 Tile",
        "<b>畫地圖</b>：筆刷、橡皮擦、填滿、框選",
        "<b>分層</b>：背景、地面分開，Order in Layer 決定前後",
        "<b>碰撞</b>：Tilemap Collider 2D + Composite Collider 2D",
        "<b>Pixels Per Unit</b>：要跟格子大小一致",
    ]),
    "BA20": ("TMP 中文字型", [
        "<b>方框</b>：預設字型 LiberationSans 沒有中文",
        "<b>中文字型</b>：挑可以商用的，例如 Noto Sans TC",
        "<b>Font Asset</b>：字型右鍵 Create > TextMeshPro > Font Asset",
        "<b>動態字型</b>：用到哪個字就自動加進去",
        "<b>Fallback</b>：加進預設字型，所有文字都能顯示中文",
        "<b>授權</b>：不要直接用 Windows 的微軟正黑體",
    ]),
    "BA21": ("Animator 狀態機", [
        "<b>Animator Controller</b>：管理多段動畫的切換",
        "<b>狀態</b>：每段動畫一個，橘色是預設",
        "<b>Make Transition</b>：拉箭頭連接兩個狀態",
        "<b>Parameters</b>：用 Trigger、Bool 當切換條件",
        "<b>SetTrigger</b>：從程式觸發切換",
        "<b>Has Exit Time</b>：等播完才切換，反應慢就取消",
    ]),
    "BA22": ("打包成執行檔", [
        "<b>Build Profiles</b>：File > Build Profiles（舊版叫 Build Settings）",
        "<b>場景清單</b>：要玩的場景都要加進去",
        "<b>開場場景</b>：清單最上面那個",
        "<b>選平台</b>：Windows、Android、WebGL…",
        "<b>Build</b>：輸出到一個空資料夾",
        "<b>一起帶走</b>：exe 和 _Data 資料夾缺一不可",
    ]),
    "BA23": ("新版 Input System", [
        "<b>新舊系統</b>：Unity 6 預設新版，Input.GetKey 會報錯",
        "<b>Input Actions</b>：先定義動作，再綁按鍵",
        "<b>Move／Jump</b>：InputSystem_Actions 已經內建",
        "<b>FindAction</b>：程式拿到動作，用 ReadValue 讀值",
        "<b>換鍵免改程式</b>：只改 Actions，手把也能用",
    ]),
    "BA24": ("ScriptableObject", [
        "<b>資料檔</b>：類別繼承 ScriptableObject",
        "<b>CreateAssetMenu</b>：讓 Create 選單建得出來",
        "<b>Inspector 調數值</b>：企劃不用碰程式",
        "<b>共用</b>：多個物件用同一份，改一次全部生效",
        "<b>Play 中改值不復原</b>：跟一般元件相反",
        "<b>不能當存檔</b>：打包後改了不會存回去",
    ]),
}


def render(row: dict) -> Path:
    """回傳投影片 PNG 的路徑。"""
    CARDS.mkdir(parents=True, exist_ok=True)
    out = CARDS / f"{row['id']}.png"
    svg = THUMBS / row["thumb"]
    thumb = f'<img src="{svg.as_uri()}">' if row["thumb"].endswith(".svg") and svg.exists() else ""
    title, items = CUSTOM.get(row["id"]) or DRAFT.get(row["id"]) or (
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
