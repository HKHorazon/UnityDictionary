# Unity字典 — 入門篇 24 支腳本（BA01–BA24）

每支 5 分鐘左右，一支講一個主題。
格式固定：**一句問題 → 操作 → 結果 → 一句提醒**。
逐字稿是重點大綱，可以照自己的方式展開講；畫面欄是同步要做的操作。

---

## BA01 安裝 Unity Hub 與編輯器

**逐字稿**
要用 Unity，先裝 Unity Hub。Hub 是管理器，不是 Unity 本身。裝好後到 Installs 分頁按 Install Editor，選一個 LTS 版本——LTS 是長期支援版，最穩。安裝時記得勾 Build Support，之後要出 Windows 執行檔就勾 Windows Build Support。模組事後也能補裝，不用一次裝滿。裝完 Hub 會列出你所有版本，一台電腦可以同時裝好幾版。

**畫面**
Hub → Installs 分頁 → Install Editor → 版本清單（指出 LTS 標記）→ 模組勾選畫面 → 回到 Installs 顯示兩個版本並存。

---

## BA02 建立新專案

**逐字稿**
打開 Hub 的 Projects 分頁，按 New Project。上面選 Unity 版本，中間選範本：做 3D 就選 3D，做 2D 就選 2D，範本的差別只是預設設定，選錯之後也改得回來。下面填專案名稱和存放位置。路徑不要有中文，也不要放在桌面或雲端同步資料夾裡，會出問題。按 Create，第一次開比較久，Unity 正在產生專案檔。

**畫面**
New Project 視窗 → 滑過 3D / 2D 範本 → 打名稱 → 特寫路徑欄（示範一個含中文的壞路徑，打叉）→ Create → 載入畫面。

---

## BA03 開啟既有專案與版本問題

**逐字稿**
Hub 的 Projects 分頁會列出你開過的專案。清單裡沒有的話按 Add，選那個專案資料夾——要選最外層、打開看得到 Assets 的那一層，不是選到 Assets 裡面。旁邊版本欄如果是紅色，代表你沒裝那個版本。你還是可以用手上的版本開，但會跳出升級警告，一旦升上去就回不去了。重要專案，升級前先複製一份。

**畫面**
Projects 清單 → Add → 檔案選擇器裡指出正確的那一層 → 紅色版本欄特寫 → 升級警告視窗。

---

## BA04 認識介面

**錄前準備**
沿用 BA02 建的新 3D 專案，SampleScene 有 Main Camera、Directional Light、Global Volume 就夠。

**逐字稿**
Unity 主畫面就五個區塊。Scene 是你編輯的世界，Game 是玩家實際會看到的畫面，也就是相機拍到的，這兩個最容易搞混。Hierarchy 列出這個場景裡所有物件，Project 是硬碟裡的檔案，Inspector 顯示你現在選中那個東西的所有設定。所以流程永遠是：在 Hierarchy 或 Project 點一下，然後在 Inspector 看、在 Inspector 改。版面被弄亂了，右上角 Layout 選 Default 就回復。

**畫面**
五個區塊依序指出名稱 → 點 Game 分頁、再點回 Scene → 點 Hierarchy 的 Main Camera，Inspector 跟著變 → 點 Project 裡一個檔案，Inspector 又變 → 拖亂一個視窗 → Layout > Default 還原。

**不講**：Play 按鈕、Account／Cloud、Package Manager。

---

## BA05 場景視角操作

**錄前準備**
場景先放 2～3 個 Cube，散開擺。口頭帶一句「方塊怎麼建，下一集會講」。

**逐字稿**
Scene 視窗的視角全靠滑鼠。滾輪縮放，按住中鍵平移——沒有中鍵的話，點左上工具列的手掌按鈕，用左鍵拖也一樣。按住右鍵轉視角。右上角這個座標小方塊可以直接點，一點就切成俯視、正視這些標準角度。最重要的一招：物件不見了、找不到了，就在 Hierarchy 雙擊它，鏡頭馬上飛到它面前。最後看一下 Inspector，Position 一個數字都沒變——這些都只是在移動你的眼睛，物件本身一動也沒動。

**畫面**
依序示範滾輪、中鍵、點手掌按鈕拖曳、右鍵轉視角 → 點右上角座標小方塊切換俯視／正視 → 故意把視角拉到很遠 → 在 Hierarchy 雙擊物件飛回去 → 選中 Cube，指 Inspector 的 Position 沒變。

**不講**：右鍵 + WASD 飛行（最多順口一句）。

---

## BA06 建立物件與移動旋轉縮放

**錄前準備**
沿用 BA05 的場景。

**逐字稿**
上一支是移動你的眼睛，這一支是動物件本身。在 Hierarchy 空白處按右鍵，3D Object 選 Cube，場景中間就出現一個方塊。選中它，看 Inspector 最上面的 Transform：Position 是位置，Rotation 是角度，Scale 是大小，任何物件都一定有這三個。數字可以直接打，也可以用 Scene 視窗左上的工具列，手掌下面依序是移動、旋轉、縮放。選移動，拖箭頭，Position 的數字會跟著變——這就是跟移動視角最大的差別。縮放要注意：拖中間的方塊才是等比例放大，只拖一個軸，東西就會被壓扁。最後一個很多人沒注意的按鈕：Local 和 Global。Global 的箭頭永遠對齊世界，Local 的箭頭跟著物件轉。角色轉過身之後想讓它往自己的前面走，就要切到 Local。

**畫面**
右鍵 > 3D Object > Cube → Transform 特寫 → 直接改 Position 數字 → 點移動按鈕、拖箭頭，Position 跟著跳 → 點旋轉拖一下 → 點縮放，先拖單軸（變扁）、復原、再拖中間方塊（等比例）→ Rotation Y 打 45，切 Global／Local 看箭頭方向差異。

**不講**：Pivot／Center、Rect Tool、Transform Tool（三合一）。Unity 6 的 Local／Global 在 Scene 視窗上方的 overlay，不在主工具列。

---

## BA07 匯入素材

**逐字稿**
匯入很簡單：把圖片、模型、音效直接拖進 Project 視窗就完成了，Unity 會自動轉成它看得懂的格式。點一下匯入的檔案，Inspector 顯示的不是檔案內容，而是它的「匯入設定」，改完記得按下面的 Apply。最常見的一個：圖片要拿來當 2D 精靈用，Texture Type 要改成 Sprite。

**畫面**
拖檔進 Project → 點圖片、Inspector 匯入設定 → Texture Type 改 Sprite → Apply。

---

## BA08 Asset Store 與套件安裝

**錄前準備**
瀏覽器先登入 Unity 帳號（跟 Hub 同一個），挑好一個免費素材。

**逐字稿**
Unity 有自己的素材商店，叫 Asset Store，網址是 assetstore.unity.com，帳號跟 Hub 是同一個。找到想要的素材，免費的按 Add to My Assets，它只是記在你的帳號裡，還沒有進專案。回到 Unity，打開 Window 選 Package Manager，左邊點 My Assets，找到剛剛那個，先按 Download，再按 Import，跳出清單確認後按 Import，東西就出現在 Project 的 Assets 裡了。同一個 Package Manager 裡還有 Unity Registry，裡面是 Unity 官方的功能套件，像 Cinemachine、ProBuilder，這種是按 Install，裝好不會出現在 Assets，而是在 Packages 底下。最後提醒：素材匯入後如果整片變粉紅色，是它的材質跟你專案的渲染管線不合，不是你弄壞了。

**畫面**
瀏覽器開 assetstore.unity.com → 搜尋免費素材 → Add to My Assets → 回 Unity，Window > Package Manager → My Assets → Download → Import → 匯入清單 → Project 出現新資料夾 → 切到 Unity Registry → Install 一個套件 → 指出它在 Packages 底下。

**不講**：付費購買流程、Scoped Registry、從 git URL 安裝。

---

## BA09 Material 材質與顏色

**逐字稿**
新建的方塊是白的，因為它用的是預設材質，而預設材質不能改。要換顏色，在 Project 按右鍵 Create 選 Material，取個名字，選中它，在 Inspector 改 Base Map 旁邊那個色塊。然後把這個 Material 從 Project 拖到場景裡的物件上，顏色就上去了。注意：同一個 Material 拖給十個物件，之後改一次，十個會一起變色。這是特性，不是 bug。

**畫面**
Create > Material → 改顏色 → 拖到 Cube → 再拖給另外兩個 Cube → 改色，三個同時變。

---

## BA10 燈光與天空

**逐字稿**
新場景預設就有一盞 Directional Light，它模擬的是太陽：只看角度，不看位置，你把它拖到天邊也沒差，但轉一下角度整個場景的光影就變了。想要燈泡那種效果，就 Create > Light > Point Light，它才有位置和照射範圍。天空的顏色來自 Skybox，在 Window > Rendering > Lighting 裡換。場景突然全黑，八成是燈被刪了，或是轉到照著背面去了。

**畫面**
轉 Directional Light 角度、陰影跟著轉 → 拖動位置、畫面沒變 → 加 Point Light → 刪掉燈、場景全黑。

---

## BA11 相機與 Game 視窗

**逐字稿**
Game 視窗看到的畫面，就是 Main Camera 拍到的東西，跟你在 Scene 裡怎麼看完全無關。選中 Main Camera，右下角會跳出一個小預覽窗，可以邊調邊看。最好用的一招：先在 Scene 視窗喬好你想要的角度，選中相機，按 Ctrl+Shift+F，相機就直接對齊你現在的視角。如果 Game 視窗是黑的，先檢查場景裡是不是根本沒有相機。

**畫面**
選 Main Camera → 右下角預覽窗 → 在 Scene 喬角度 → Ctrl+Shift+F → Game 視窗跟著變 → 刪掉相機、Game 全黑。

---

## BA12 第一支腳本

**逐字稿**
在 Project 按右鍵，Create 選 MonoBehaviour Script，舊版叫 C# Script。檔名要跟裡面的 class 名稱一樣，之後改名要兩邊一起改，不然掛不上去。雙擊打開，裡面兩個函式：Start 在物件出生時跑一次，Update 每一影格都跑一次。寫完存檔，回到 Unity 等右下角編譯完，最關鍵的一步——把腳本拖到 Hierarchy 的物件上。沒掛在物件上的腳本，永遠不會執行。

**畫面**
Create Script → 命名 → 雙擊開 IDE、指出 class 名稱 → 打一行 Debug.Log → 存檔 → 回 Unity 編譯 → 拖到 Cube 上 → 播放看 Console。

---

## BA13 Prefab 預製物件

**逐字稿**
把 Hierarchy 裡做好的物件，拖回 Project 視窗，它就變成 Prefab，名字會變成藍色。之後從 Project 拖出來幾百次，全都是同一個模子做的。要改的時候雙擊 Prefab 進入編輯模式，改完一存，場景裡所有複本一起更新，這就是 Prefab 存在的意義。那如果只想改其中一個呢？直接在場景上改就好，被你改過的欄位會變成粗體，代表這一個有它自己的設定。

**畫面**
拖物件回 Project、變藍 → 拉出五個 → 雙擊進 Prefab 模式改顏色 → 五個一起變 → 單獨改其中一個、欄位變粗體。

---

## BA14 父子關係

**逐字稿**
在 Hierarchy 裡把 A 拖到 B 上面，A 就變成 B 的子物件。重點是：子物件的 Transform 從此變成「相對於父物件」，父物件移動、旋轉、縮放，子物件全部跟著走。最常見兩種用法：建一個空物件當資料夾，把一堆零件收在一起讓 Hierarchy 乾淨；還有把武器掛在手掌底下，手一動武器就跟著動。要注意父物件的 Scale 不是 1 的時候，子物件會被拉變形。

**畫面**
拖曳建立父子 → 移動父物件、子物件跟著 → 建空物件當群組 → 把方塊掛到旋轉的物件下 → 父物件 Scale 拉歪、子物件變形。

---

## BA15 Animation 關鍵影格動畫

**錄前準備**
場景裡放一個 Cube。

**逐字稿**
不寫程式也能讓東西動。選中物件，打開 Window > Animation > Animation，按 Create 存一個 Animation Clip，Unity 會自動幫物件加上 Animator。按紅色的錄製鍵，把時間軸拖到 1 秒，移動或旋轉物件，就自動記下一個關鍵影格；再拖到 2 秒把它放回原位。按播放就能看到它來回動。錄製中改的任何數值都會被記下來，連顏色、開關都可以。切到 Curves 可以調快慢的曲線。最後提醒兩件事：錄完一定要關掉錄製鍵，不然之後隨手調的數值也會被錄進去；動畫記的是位置數值，把物件搬到別處，播放時會被拉回去，要整組移動就幫它包一層父物件，改移動父物件。

**畫面**
選 Cube → Animation 視窗 Create → 按錄製 → 1 秒移動、2 秒回原位 → 播放 → 再加一個旋轉 → Curves 調曲線 → 關掉錄製 → 搬動物件、播放被拉回 → 包一層父物件解決。

**不講**：Dopesheet 細節、Animation Event、匯入模型附帶的動畫。
---

## BA16 UI Canvas 與按鈕

**錄前準備**
準備一個有 public 函式的腳本，例如讓方塊換顏色。

**逐字稿**
遊戲裡的血條、分數、按鈕都是 UI。Hierarchy 右鍵 UI > Text - TextMeshPro，第一次會跳出要匯入 TMP Essentials，按下去。Unity 會一起建好 Canvas 和 EventSystem：Canvas 是放所有 UI 的畫布，EventSystem 負責接收滑鼠點擊，把它刪掉按鈕就按不了。Scene 視窗裡的 Canvas 大得誇張，這是正常的，切到 2D 模式看比較方便。UI 用的是 Rect Transform，左上角的 Anchor 決定它黏在螢幕的哪個角，選錯的話換個解析度就跑掉了。做按鈕就是 UI > Button，在 Inspector 的 On Click 按加號，把掛了腳本的物件拖進去，再選要執行的函式。最後提醒：Canvas Scaler 改成 Scale With Screen Size，換不同螢幕大小時 UI 才會等比例縮放。

**畫面**
建 Text → 匯入 TMP Essentials → 指出 Canvas、EventSystem → 2D 模式看 Canvas → 調 Anchor、改 Game 視窗解析度看差別 → 建 Button → On Click 綁函式 → 播放、按下去方塊變色 → Canvas Scaler 改 Scale With Screen Size。

**不講**：Layout Group、UI Toolkit、World Space Canvas。
---

## BA17 3D 碰撞

**錄前準備**
一塊 Plane 當地板，一個 Cube 放在半空中。

**逐字稿**
方塊放在半空中按播放，它不會掉，因為它沒有物理。加上 Rigidbody，它就會受重力往下掉，碰到地板停住——因為 Cube 和 Plane 本來就有 Collider，Collider 決定碰撞的形狀。規則是：兩邊都要有 Collider，至少一邊要有 Rigidbody，才會碰撞。想知道撞到了什麼，就在腳本裡寫 OnCollisionEnter，參數裡就有對方是誰。如果要的是「可以穿過去，但知道有東西進來」，像吃金幣、走進某個區域，就把 Collider 的 Is Trigger 勾起來，改用 OnTriggerEnter。最後提醒：有 Rigidbody 的物件要用物理去推它，直接改 Transform 硬搬，碰撞會穿模或抖動。

**畫面**
播放、方塊不掉 → 加 Rigidbody、掉到地板 → 指出 Collider 綠框 → 拿掉地板的 Collider、方塊穿過去 → OnCollisionEnter 印出對方名稱 → 勾 Is Trigger、改 OnTriggerEnter → 吃金幣範例。

**不講**：Physics Material（摩擦、彈性）、Layer 碰撞矩陣、連續碰撞偵測。
---

## BA18 2D 碰撞

**錄前準備**
2D 場景，一個角色 Sprite 和一塊地板 Sprite。

**逐字稿**
2D 的物理跟 3D 是兩套系統，元件名字後面都多一個 2D：Rigidbody 2D、Box Collider 2D、Circle Collider 2D。用法跟 3D 一樣：角色加 Rigidbody 2D 會往下掉，地板加 Box Collider 2D 就能接住它。腳本的函式也要加 2D：OnCollisionEnter2D、OnTriggerEnter2D，參數型別是 Collision2D 和 Collider2D。最常見的錯有兩個：2D 物件加了 3D 的 Collider，或是函式名稱忘了寫 2D，結果完全沒反應，也不會報錯。另外 2D 遊戲通常不希望角色被撞得轉圈圈，在 Rigidbody 2D 的 Constraints 勾 Freeze Rotation Z。

**畫面**
角色加 Rigidbody 2D、掉下去 → 地板加 Box Collider 2D、接住 → OnCollisionEnter2D 印出 → 故意寫成 OnCollisionEnter、沒反應 → 2D 物件加 3D Collider、沒反應 → 角色被撞得轉圈 → Freeze Rotation Z。

**不講**：Composite Collider 2D（Tilemap 那集會用到）、Physics Material 2D、Effector。
---

## BA19 Tilemap 2D 地圖

**錄前準備**
用 2D 場景，準備一張已經切好格子的地形圖（Sprite Mode 設 Multiple，用 Sprite Editor 切格）。Unity 6 的 2D 範本已經裝好 Tilemap 套件。

**逐字稿**
做 2D 關卡一格一格擺物件太慢，要用 Tilemap。Hierarchy 右鍵 2D Object > Tilemap > Rectangular，會產生一個 Grid 和底下一層 Tilemap。打開 Window > 2D > Tile Palette，新建一個調色盤，把切好的地形圖拖進去，它會自動做成一格一格的 Tile。選筆刷在場景上點、拖，就能像畫畫一樣鋪地圖，旁邊還有橡皮擦、填滿、框選。背景和地面可以分成兩層 Tilemap，用 Order in Layer 決定誰在前面。要讓角色站得上去，在地面那層加 Tilemap Collider 2D，再加 Composite Collider 2D，把 Tilemap Collider 的 Composite Operation 設成 Merge，一堆小碰撞就會合成一大塊。最後提醒：圖片的 Pixels Per Unit 要跟格子大小一樣，不然 Tile 會有縫或疊在一起。

**畫面**
建 Tilemap → 開 Tile Palette → 拖入地形圖產生 Tile → 筆刷畫地面 → 橡皮擦、填滿 → 新增背景層、調 Order in Layer → 加 Tilemap Collider 2D + Composite Collider 2D → 角色站上去不會掉。

**不講**：Rule Tile、Animated Tile、等角和六角格地圖。
---

## BA20 TMP 中文字型

**錄前準備**
先下載一個可以免費商用的中文字型，例如 Noto Sans TC（思源黑體），場景裡放一個 TextMeshPro 文字物件。

**逐字稿**
用 TextMeshPro 打中文，畫面上出現一堆方框，不是你打錯，是預設字型 LiberationSans 裡根本沒有中文字。解法是做一個中文的 Font Asset。先把中文字型檔拖進 Project，在字型檔上按右鍵，Create > TextMeshPro > Font Asset，會產生一個動態的 Font Asset：用到哪個字，它就即時把那個字加進去，不用事先準備字表。選中文字物件，把 Inspector 的 Font Asset 換成它，方框就變中文了。不想每個物件都換的話，打開預設的 LiberationSans SDF，在 Fallback 清單加上你的中文字型，以後找不到的字都會自動去中文字型找。最後提醒：不要直接拿 Windows 裡的微軟正黑體，它的授權不允許你跟遊戲一起散佈。

**畫面**
打中文出現方框 → 字型檔拖進 Project → 右鍵 Create > TextMeshPro > Font Asset → 文字物件換 Font Asset、方框變中文 → 打開 LiberationSans SDF → Fallback 加上中文字型 → 新的文字物件直接顯示中文。

**不講**：Font Asset Creator 靜態字表、Atlas 解析度、Material Preset。Unity 6 的選單位置依版本不同，可能還要再選一層 SDF。

---

## BA21 Animator 狀態機

**錄前準備**
準備兩段動畫，例如待機和跳躍（可以用 Animation 那集做的），再放一個 UI 按鈕。

**逐字稿**
一個物件有好幾段動畫，要決定什麼時候播哪一段，就靠 Animator Controller。雙擊打開 Animator 視窗，每一段動畫就是一個狀態，橘色那個是一開始播的預設狀態。在狀態上按右鍵 Make Transition 拉一條箭頭，代表可以從這段切到那段。切換的條件用 Parameters：左邊新增一個 Trigger 叫 Jump，點箭頭，在 Conditions 加上 Jump。程式裡拿到 Animator，呼叫 SetTrigger("Jump") 就會切過去。要跳完自己回到待機，就從跳躍再拉一條箭頭回來，勾 Has Exit Time，等動畫播完才回去。最後提醒：箭頭預設就勾了 Has Exit Time，會等目前的動畫播完才切換，覺得反應慢半拍，就把它取消。

**畫面**
打開 Animator → 指出預設狀態 → Make Transition → 新增 Trigger 參數 → 箭頭加 Conditions → 按鈕呼叫 SetTrigger → 播放 → 回程箭頭 Has Exit Time → 取消 Has Exit Time、比較反應速度。

**不講**：Blend Tree、Animator Layer、Avatar 與人形動畫。
---

## BA22 打包成執行檔

**逐字稿**
做完了要給別人玩，File 選 Build Profiles，舊版叫 Build Settings。第一件事最容易忘：把你要玩的場景加進上面那個清單，沒加進去的場景不會被打包，而且排最上面的那個就是開場場景。左邊選平台，出 Windows 就選 Windows，按 Build，指定一個空資料夾。最後提醒：產出的 exe 檔和旁邊那個 _Data 資料夾必須一起帶走，只複製 exe 一定開不起來。

**畫面**
File > Build Profiles → Add Open Scenes → 拖曳調整場景順序 → 選平台 → Build 選空資料夾 → 顯示產出的 exe + _Data → 只複製 exe、開啟失敗。

---

## BA23 新版 Input System

**錄前準備**
Unity 6 新專案預設已裝 Input System，場景裡放一個 Cube。

**逐字稿**
Unity 6 的新專案預設用新版 Input System，舊的 Input.GetKey 寫法一執行就會報錯。新版的想法是先定義「動作」，再決定哪些按鍵觸發它。專案裡已經有一個 InputSystem_Actions，打開可以看到 Player 底下有 Move、Jump 這些動作，Move 綁了 WASD、方向鍵和手把左類比。程式裡用 InputSystem.actions.FindAction("Move") 拿到動作，在 Update 裡用 ReadValue 讀出方向，乘上速度和 Time.deltaTime 讓方塊移動。好處是之後要換按鍵、加手把，只要改 Actions，程式一行都不用動。

**畫面**
舊寫法報錯 → 打開 InputSystem_Actions → 看 Move 的綁定 → 寫腳本 FindAction + ReadValue → 掛到 Cube 播放、WASD 移動 → 在 Actions 多綁一個按鍵，不改程式也能動。

**不講**：PlayerInput 元件、改鍵介面（Rebinding）、多人輸入。

---

## BA24 ScriptableObject 資料容器

**錄前準備**
準備一個把數值寫死在腳本裡的例子，例如三把武器各有名稱、攻擊力。

**逐字稿**
數值寫在 MonoBehaviour 裡，每個物件都各存一份，要改得一個一個找。ScriptableObject 是專門裝資料的檔案：寫一個類別繼承 ScriptableObject，上面加 [CreateAssetMenu]，Project 按右鍵 Create 就能做出一個資料檔，跟材質一樣是一個資產，數值直接在 Inspector 調。腳本裡宣告這個型別的欄位，把資料檔拖進去就能讀。好處是十個敵人可以共用同一份設定，改一次全部生效，企劃也不用碰程式就能調數值。最後提醒兩件事：在編輯器 Play 模式下改它的值，停止後不會復原，跟一般元件相反；打包後的遊戲裡改了也不會存回檔案，所以不能拿來當存檔用。

**畫面**
數值寫死的腳本 → 改成 ScriptableObject 類別 + CreateAssetMenu → Create 出三把武器資料 → 拖進武器腳本 → 改一份資料、用到它的物件一起變 → Play 中改值、停止後數值還在。

**不講**：用 ScriptableObject 做事件頻道、Runtime Set、Addressables 載入。

---

## 拍攝備註

- 24 支建議分 4 次錄完：BA01–BA06（Hub 與介面）、BA07–BA11（素材與場景）、BA12–BA18（腳本、動畫、UI、碰撞）、BA19–BA24（2D 地圖、字型、動畫狀態機、輸出、輸入與資料）。
- 全程用**同一個新專案**錄，剛好從空專案一路長到可以 Build，畫面有連續性。
- BA01–BA03 是錄 Hub，不是錄編輯器，可以最後補錄。
- 錄之前先把編輯器介面調成 Default Layout、字體放大（Preferences > UI Scaling 調到 125%），手機看得清楚。
