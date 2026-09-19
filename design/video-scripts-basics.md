# Unity字典 — 入門篇 20 支腳本（BA01–BA20）

每支 30–60 秒，一支只講一件事。
格式固定：**一句問題 → 操作 → 結果 → 一句提醒**。
逐字稿直接照唸即可，畫面欄是同步要做的操作。

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

**逐字稿**
Unity 主畫面就五個區塊。Scene 是你編輯的世界，Game 是玩家實際會看到的畫面，這兩個最容易搞混。Hierarchy 列出這個場景裡所有物件，Project 是硬碟裡的檔案，Inspector 顯示你現在選中那個東西的所有設定。所以流程永遠是：在 Hierarchy 或 Project 點一下，然後在 Inspector 改。版面被弄亂了，右上角 Layout 選 Default 就回復。

**畫面**
五個區塊依序打亮並標名稱 → 點 Hierarchy 物件、Inspector 跟著變 → Layout > Default 還原。

---

## BA05 場景視角操作

**逐字稿**
Scene 視窗的視角全靠滑鼠。滾輪縮放，按住中鍵平移——沒有中鍵的話，點左上工具列的手掌按鈕，用左鍵拖也一樣。按住右鍵轉視角，按著右鍵還能用 WASD 在場景裡飛。右上角這個座標小方塊可以直接點，一點就切成俯視、正視這些標準角度。最重要的一招：物件不見了、找不到了，就在 Hierarchy 雙擊它，鏡頭馬上飛到它面前。記住，這些都只是在移動你的眼睛，物件本身一動也沒動。

**畫面**
依序示範滾輪、中鍵、點手掌按鈕拖曳、右鍵轉視角 → 點右上角座標小方塊切換俯視／正視 → 故意把視角拉到很遠 → 在 Hierarchy 雙擊物件飛回去。

---

## BA06 移動、旋轉、縮放工具

**逐字稿**
上一支是移動你的眼睛，這一支是移動物件本身。Scene 視窗左上的工具列，手掌下面依序是移動、旋轉、縮放。選移動，拖箭頭，你會看到 Inspector 的 Position 數字跟著變——這就是跟移動視角最大的差別。旋轉、縮放也一樣，縮放時拖中間的方塊是等比例放大。上方還有兩個按鈕很多人沒注意：Pivot 和 Center，決定一次選多個物件時，是各自原地轉、還是繞著大家的中間轉；Local 和 Global，決定箭頭跟著物件轉、還是永遠對齊世界座標。角色轉過身之後想讓它往自己的前面走，就要切到 Local。

**畫面**
點移動按鈕 → 拖箭頭、特寫 Inspector 的 Position 數字在跳 → 點旋轉、縮放各拖一下 → 選兩個 Cube，Center 模式旋轉（繞中間公轉）→ 切 Pivot（各自原地轉）→ 把 Cube 轉 45 度，切 Local / Global 看箭頭方向差異。

---

## BA07 建立第一個物件與 Transform

**逐字稿**
在 Hierarchy 空白處按右鍵，3D Object 選 Cube，場景中間就出現一個方塊。選中它，看 Inspector 最上面的 Transform：Position 是位置，Rotation 是角度，Scale 是大小。場景裡任何物件都一定有這三個，這是 Unity 的共同語言。數字可以直接打，也可以按住欄位名稱左右拖曳來微調。要一塊地板，就再建一個 Plane，把 Scale 放大。

**畫面**
右鍵 > 3D Object > Cube → Transform 特寫 → 拖曳 X 欄位名稱、方塊跟著滑動 → 建 Plane 放大成地板。

---

## BA08 存檔的兩層意思

**逐字稿**
Unity 的存檔有兩層。Ctrl+S 存的是「場景」，也就是 Hierarchy 裡的所有東西；標題列有星號就代表還沒存。新專案第一次存會叫你命名，存到 Assets 底下的 Scenes 資料夾。至於專案設定和匯入的素材，是自動存的，不用管。最重要的一句：Play 模式下改的東西，一停止播放就全部消失，Ctrl+S 也救不回來。

**畫面**
標題列星號特寫 → Ctrl+S、星號消失 → 進 Play 模式改一個數值 → 停止、數值復原。

---

## BA09 Project 視窗與資料夾

**逐字稿**
Project 視窗就是你專案裡的 Assets 資料夾，你在這裡建的資料夾，硬碟上是真的存在的。建議一開始就分好 Scenes、Scripts、Materials、Prefabs、Art，之後找東西才不會崩潰。但有一個鐵則：搬檔案、改檔名，一定要在 Unity 裡面做，不要去檔案總管拖。每個檔案旁邊都有一個 .meta 檔記錄它的身分，在外面搬會讓關聯斷掉，物件上的東西就全部變成 Missing。

**畫面**
建立資料夾結構 → 在 Unity 內拖曳搬檔（正常）→ 切到檔案總管示意（打叉）→ 顯示 .meta 檔 → Missing 的 Inspector 畫面。

---

## BA10 匯入素材

**逐字稿**
匯入很簡單：把圖片、模型、音效直接拖進 Project 視窗就完成了，Unity 會自動轉成它看得懂的格式。點一下匯入的檔案，Inspector 顯示的不是檔案內容，而是它的「匯入設定」，改完記得按下面的 Apply。最常見的一個：圖片要拿來當 2D 精靈用，Texture Type 要改成 Sprite。從 Asset Store 買的東西，會出現在 Package Manager 的 My Assets 裡，按 Import 才會進專案。

**畫面**
拖檔進 Project → 點圖片、Inspector 匯入設定 → Texture Type 改 Sprite → Apply → Package Manager > My Assets。

---

## BA11 Material 材質與顏色

**逐字稿**
新建的方塊是白的，因為它用的是預設材質，而預設材質不能改。要換顏色，在 Project 按右鍵 Create 選 Material，取個名字，選中它，在 Inspector 改 Base Map 旁邊那個色塊。然後把這個 Material 從 Project 拖到場景裡的物件上，顏色就上去了。注意：同一個 Material 拖給十個物件，之後改一次，十個會一起變色。這是特性，不是 bug。

**畫面**
Create > Material → 改顏色 → 拖到 Cube → 再拖給另外兩個 Cube → 改色，三個同時變。

---

## BA12 燈光與天空

**逐字稿**
新場景預設就有一盞 Directional Light，它模擬的是太陽：只看角度，不看位置，你把它拖到天邊也沒差，但轉一下角度整個場景的光影就變了。想要燈泡那種效果，就 Create > Light > Point Light，它才有位置和照射範圍。天空的顏色來自 Skybox，在 Window > Rendering > Lighting 裡換。場景突然全黑，八成是燈被刪了，或是轉到照著背面去了。

**畫面**
轉 Directional Light 角度、陰影跟著轉 → 拖動位置、畫面沒變 → 加 Point Light → 刪掉燈、場景全黑。

---

## BA13 相機與 Game 視窗

**逐字稿**
Game 視窗看到的畫面，就是 Main Camera 拍到的東西，跟你在 Scene 裡怎麼看完全無關。選中 Main Camera，右下角會跳出一個小預覽窗，可以邊調邊看。最好用的一招：先在 Scene 視窗喬好你想要的角度，選中相機，按 Ctrl+Shift+F，相機就直接對齊你現在的視角。如果 Game 視窗是黑的，先檢查場景裡是不是根本沒有相機。

**畫面**
選 Main Camera → 右下角預覽窗 → 在 Scene 喬角度 → Ctrl+Shift+F → Game 視窗跟著變 → 刪掉相機、Game 全黑。

---

## BA14 Play 模式

**逐字稿**
上方三角形按鈕開始播放，再按一次停止。這裡有個新手一定會踩的坑：在播放中調好的一堆數值，一停止就全部復原，白調了。真的要留住的話，播放中在那個元件右上角的三個點選 Copy Component，停止後再 Paste Component Values。建議先去 Edit > Preferences > Colors，把 Playmode tint 調成明顯的顏色，這樣一眼就知道自己現在在播放中。

**畫面**
播放中改數值 → 停止、復原 → Copy Component / Paste Component Values → 設定 Playmode tint、整個編輯器變色。

---

## BA15 第一支腳本

**逐字稿**
在 Project 按右鍵，Create 選 MonoBehaviour Script，舊版叫 C# Script。檔名要跟裡面的 class 名稱一樣，之後改名要兩邊一起改，不然掛不上去。雙擊打開，裡面兩個函式：Start 在物件出生時跑一次，Update 每一影格都跑一次。寫完存檔，回到 Unity 等右下角編譯完，最關鍵的一步——把腳本拖到 Hierarchy 的物件上。沒掛在物件上的腳本，永遠不會執行。

**畫面**
Create Script → 命名 → 雙擊開 IDE、指出 class 名稱 → 打一行 Debug.Log → 存檔 → 回 Unity 編譯 → 拖到 Cube 上 → 播放看 Console。

---

## BA16 Console 與錯誤訊息

**逐字稿**
Console 在 Window > General > Console，或按 Ctrl+Shift+C。紅色是錯誤，只要有紅色，遊戲根本按不下去；黃色是警告，通常可以先放著。錯誤訊息雙擊下去，會直接跳到程式碼出錯的那一行，不用自己找。想看變數現在是多少，就寫 Debug.Log，括號裡放你要看的東西。訊息太多按 Clear，把 Clear on Play 勾起來，每次播放會自動清空。

**畫面**
故意寫錯語法 → 紅字出現、播放鍵按不動 → 雙擊跳到程式碼 → 修好 → Debug.Log 輸出 → 勾 Clear on Play。

---

## BA17 讓變數出現在 Inspector

**逐字稿**
腳本裡宣告成 public 的變數，會自動出現在 Inspector，不用改程式就能調數值，這是 Unity 最方便的地方。但 public 的意思是「誰都能改」，別的腳本也能亂動它。比較好的寫法是宣告成 private，前面加上中括號 SerializeField，一樣看得到、一樣能調，但只有自己人能改。還有一件事要記住：Inspector 上的數值會蓋過程式碼裡寫的初始值。改了程式卻沒反應，通常就是這個原因。

**畫面**
public float speed → Inspector 出現欄位 → 改成 [SerializeField] private → 一樣出現 → 改程式初始值、Inspector 沒跟著變。

---

## BA18 Prefab 預製物件

**逐字稿**
把 Hierarchy 裡做好的物件，拖回 Project 視窗，它就變成 Prefab，名字會變成藍色。之後從 Project 拖出來幾百次，全都是同一個模子做的。要改的時候雙擊 Prefab 進入編輯模式，改完一存，場景裡所有複本一起更新，這就是 Prefab 存在的意義。那如果只想改其中一個呢？直接在場景上改就好，被你改過的欄位會變成粗體，代表這一個有它自己的設定。

**畫面**
拖物件回 Project、變藍 → 拉出五個 → 雙擊進 Prefab 模式改顏色 → 五個一起變 → 單獨改其中一個、欄位變粗體。

---

## BA19 父子關係

**逐字稿**
在 Hierarchy 裡把 A 拖到 B 上面，A 就變成 B 的子物件。重點是：子物件的 Transform 從此變成「相對於父物件」，父物件移動、旋轉、縮放，子物件全部跟著走。最常見兩種用法：建一個空物件當資料夾，把一堆零件收在一起讓 Hierarchy 乾淨；還有把武器掛在手掌底下，手一動武器就跟著動。要注意父物件的 Scale 不是 1 的時候，子物件會被拉變形。

**畫面**
拖曳建立父子 → 移動父物件、子物件跟著 → 建空物件當群組 → 把方塊掛到旋轉的物件下 → 父物件 Scale 拉歪、子物件變形。

---

## BA20 打包成執行檔

**逐字稿**
做完了要給別人玩，File 選 Build Profiles，舊版叫 Build Settings。第一件事最容易忘：把你要玩的場景加進上面那個清單，沒加進去的場景不會被打包，而且排最上面的那個就是開場場景。左邊選平台，出 Windows 就選 Windows，按 Build，指定一個空資料夾。最後提醒：產出的 exe 檔和旁邊那個 _Data 資料夾必須一起帶走，只複製 exe 一定開不起來。

**畫面**
File > Build Profiles → Add Open Scenes → 拖曳調整場景順序 → 選平台 → Build 選空資料夾 → 顯示產出的 exe + _Data → 只複製 exe、開啟失敗。

---

## 拍攝備註

- 20 支建議分 3 次錄完：BA01–BA06（Hub 與介面）、BA07–BA14（場景操作）、BA15–BA20（腳本與輸出）。
- 全程用**同一個新專案**錄，剛好從空專案一路長到可以 Build，畫面有連續性。
- BA01–BA03 是錄 Hub，不是錄編輯器，可以最後補錄。
- 錄之前先把編輯器介面調成 Default Layout、字體放大（Preferences > UI Scaling 調到 125%），手機看得清楚。
