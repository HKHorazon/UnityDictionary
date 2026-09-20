"""把標題／說明／標籤／字幕推到已經上傳的 YouTube 影片上，並同步 Google Sheet。

    python videos/upload.py            # tsv 裡有 youtubeId 的條目全做，最後問要不要公開
    python videos/upload.py BA01 BA02  # 只做指定條目
    python videos/upload.py --check    # 只驗證授權，印出連到哪個頻道
    python videos/upload.py --scan     # 從頻道反查影片 ID，自動填進 tsv
    python videos/upload.py --sheet    # 把已上傳的條目寫進 Google Sheet
    python videos/upload.py --publish  # 只做「改成公開」那一步

影片檔本身請自己在 YouTube Studio 拖上去，不要用 API 傳：未通過 Google 審核的
API 專案，用 videos.insert 傳的片會被永久鎖成私人，事後在 Studio 也改不回公開，
只能整支重傳。videos.update 和 captions.insert 沒有這個限制，所以這支程式只做
上傳「之後」的雜事：

  1. videos.update   套上 meta.py 算出來的標題／說明／標籤／分類／語言
  2. captions.insert 上傳 3.output/*.srt（同語言的字幕軌已存在就改用 update）
  3. playlistItems.insert 加進播放清單「Unity短片辭典」（沒有就自動建）
  4. videos.update   把隱私狀態改成公開（會先列清單問過你才動）
  5. spreadsheets.values 把已上傳的條目寫進網站在讀的那張 Google Sheet

影片 ID 從 design/sheet-rows-basics.tsv 的 youtubeId 欄讀。不想自己抄 ID 的話
先跑 --scan，它會照「YouTube 標題 == 成品檔名」把 ID 反查回來填好。

首次執行需要 videos/client_secret.json（Google Cloud 的 OAuth 桌面用戶端），
授權後 token 會快取在 videos/.youtube-token.json，兩個檔都在 .gitignore 裡。
設定步驟見 README.md。
"""
import json
import re
import sys
from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from meta import OUT, SITE, TSV, build_meta, load

ROOT = Path(__file__).parent
SECRET = ROOT / "client_secret.json"
TOKEN = ROOT / ".youtube-token.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/spreadsheets",
]

CATEGORY = "27"        # Education
LANG = "zh-Hant"       # 影片語言與字幕語言
CAPTION_NAME = "繁體中文"
PLAYLIST = "Unity短片辭典"
SHEET_OUT = TSV.parent / "sheet-current.tsv"
CONSTANTS = ROOT.parent / "src" / "data" / "constants.json"
VIDEO_ID_RE = re.compile("^[A-Za-z0-9_-]{11}$")
TAB = chr(9)


# ── 授權 ────────────────────────────────────────────────────────

def credentials():
    """拿到授權憑證；第一次、或 scope 變過，會開瀏覽器要你登入。

    OAuth 同意畫面停在「測試中」的話，refresh token 只有 7 天壽命，過期後
    refresh 會拋 RefreshError——這裡接住它退回重新授權，不要讓程式直接炸掉。
    把發布狀態改成「正式版」就沒有這個限制，做法見 README。
    """
    creds = None
    if TOKEN.exists():
        # 這裡千萬不要把 SCOPES 傳進去：傳了會直接蓋掉檔案裡記錄的 scopes，
        # 底下的檢查就永遠成立，然後又把這份「宣稱的」範圍寫回 token 檔。
        # token 檔看起來有權限、實際 access token 沒有，Google 會回
        # ACCESS_TOKEN_SCOPE_INSUFFICIENT，而且怎麼重跑都不會自己修好。
        creds = Credentials.from_authorized_user_file(TOKEN)
        if not set(SCOPES).issubset(set(creds.scopes or [])):
            print("授權範圍變了，要重新授權一次……")
            creds = None

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            print("token 過期了（測試中的專案每 7 天要重新授權一次），重開瀏覽器……")
            creds = None

    if not creds or not creds.valid:
        if not SECRET.exists():
            sys.exit(f"找不到 {SECRET}，請先照 README 的「設定 YouTube API」做一次。")
        creds = InstalledAppFlow.from_client_secrets_file(SECRET, SCOPES).run_local_server(port=0)

    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return creds


def service(creds=None):
    return build("youtube", "v3", credentials=creds or credentials())


def confirm(prompt: str) -> bool:
    """會改到外面看得到的東西之前問一句。沒有互動終端機就當作不同意。"""
    try:
        return input(f"\n{prompt} (y/N) ").strip().lower() in ("y", "yes")
    except EOFError:
        print("沒有互動終端機，跳過。")
        return False


# ── YouTube ────────────────────────────────────────────────────

def push_meta(yt, video_id: str, meta: dict) -> None:
    """videos.update 會整段覆蓋 part，所以先讀回現況再改欄位，免得洗掉隱私設定。"""
    found = yt.videos().list(part="snippet,status", id=video_id).execute()["items"]
    if not found:
        raise RuntimeError(f"YouTube 上找不到影片 {video_id}（ID 打錯，或不是這個頻道的）")
    video = found[0]

    snippet = video["snippet"] | {
        "title": meta["title"],
        "description": meta["description"],
        "tags": meta["tags"],
        "categoryId": CATEGORY,
        "defaultLanguage": LANG,
        "defaultAudioLanguage": LANG,
    }
    status = video["status"] | {"selfDeclaredMadeForKids": False}
    yt.videos().update(part="snippet,status",
                       body={"id": video_id, "snippet": snippet, "status": status}).execute()


def push_caption(yt, video_id: str, srt: Path) -> str:
    """同一個語言的字幕軌只留一條：有就換掉內容，沒有才新增。"""
    media = MediaFileUpload(str(srt), mimetype="application/octet-stream")
    existing = yt.captions().list(part="snippet", videoId=video_id).execute()["items"]
    for track in existing:
        if track["snippet"]["language"] == LANG:
            yt.captions().update(part="snippet",
                                 body={"id": track["id"], "snippet": {"isDraft": False}},
                                 media_body=media).execute()
            return f"字幕已更新（{srt.name}）"
    yt.captions().insert(
        part="snippet",
        body={"snippet": {"videoId": video_id, "language": LANG,
                          "name": CAPTION_NAME, "isDraft": False}},
        media_body=media,
    ).execute()
    return f"字幕已上傳（{srt.name}）"


def check(yt) -> None:
    """印出授權到哪個頻道——多頻道帳號很容易授權到錯的那個。"""
    ch = yt.channels().list(part="snippet,contentDetails", mine=True).execute()["items"]
    if not ch:
        sys.exit("這個 Google 帳號底下沒有 YouTube 頻道。")
    for c in ch:
        print(f"授權成功 → 頻道「{c['snippet']['title']}」（{c['id']}）")
    print("如果這不是你要傳的頻道，刪掉 videos/.youtube-token.json 再跑一次，換帳號授權。")


def ensure_playlist(yt) -> str:
    """找到叫 PLAYLIST 的播放清單，沒有就建一個，回傳它的 id。"""
    req = yt.playlists().list(part="snippet", mine=True, maxResults=50)
    while req:
        res = req.execute()
        for pl in res["items"]:
            if pl["snippet"]["title"] == PLAYLIST:
                return pl["id"]
        req = yt.playlists().list_next(req, res)

    created = yt.playlists().insert(part="snippet,status", body={
        "snippet": {"title": PLAYLIST,
                    "description": f"Unity短片辭典，每支短片只講一個 Unity 功能。{SITE}",
                    "defaultLanguage": LANG},
        "status": {"privacyStatus": "public"},
    }).execute()
    print(f"  建立播放清單「{PLAYLIST}」（公開；裡面的私人影片別人還是看不到）")
    return created["id"]


def add_to_playlist(yt, playlist_id: str, video_id: str) -> str:
    """已經在清單裡就不要再加一次，不然會多出重複的項目。"""
    req = yt.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=50)
    while req:
        res = req.execute()
        for item in res["items"]:
            if item["snippet"]["resourceId"].get("videoId") == video_id:
                return f"已經在播放清單「{PLAYLIST}」裡"
        req = yt.playlistItems().list_next(req, res)

    yt.playlistItems().insert(part="snippet", body={"snippet": {
        "playlistId": playlist_id,
        "resourceId": {"kind": "youtube#video", "videoId": video_id},
    }}).execute()
    return f"已加進播放清單「{PLAYLIST}」"


def publish(yt, targets: list[tuple[str, str]]) -> None:
    """把影片改成公開。

    這是整支程式裡唯一會讓影片對外曝光的動作，而且沒有「取消發布」這種乾淨的
    回頭路（改回私人，先前的曝光也收不回來），所以一定先把清單攤開再問。
    """
    if not targets:
        return
    found = yt.videos().list(part="status,snippet",
                             id=",".join(v for _, v in targets)).execute()["items"]
    current = {v["id"]: v for v in found}

    pending = []
    for entry_id, video_id in targets:
        video = current.get(video_id)
        if not video:
            print(f"  ! {entry_id} 在頻道上找不到影片 {video_id}")
            continue
        state = video["status"]["privacyStatus"]
        if state == "public":
            print(f"  - {entry_id} 已經是公開")
            continue
        print(f"  · {entry_id} {video['snippet']['title']}（目前 {state}）")
        pending.append((entry_id, video_id, video))

    if not pending:
        return
    if not confirm(f"要把以上 {len(pending)} 支影片改成「公開」嗎？"):
        print("保持原狀，之後可以單獨跑 python videos/upload.py --publish")
        return

    for entry_id, video_id, video in pending:
        status = video["status"] | {"privacyStatus": "public"}
        yt.videos().update(part="status",
                           body={"id": video_id, "status": status}).execute()
        print(f"  {entry_id} → 公開  https://youtu.be/{video_id}")


# ── tsv ────────────────────────────────────────────────────────

def write_ids(found: dict[str, str], force: bool) -> list[str]:
    """把影片 ID 寫回 tsv 的 youtubeId 欄，回傳真的有寫進去的條目。

    逐行處理而不是用 csv 模組：這張表的行尾（CRLF）和「沒有引號」的原樣都要
    保住，csv.writer 會自作主張加引號。
    """
    with TSV.open(encoding="utf-8", newline="") as f:
        lines = f.readlines()
    cols = lines[0].splitlines()[0].split(TAB)
    id_col, yt_col = cols.index("id"), cols.index("youtubeId")

    written = []
    for i, line in enumerate(lines[1:], start=1):
        body = line.splitlines()[0]
        eol = line[len(body):]
        fields = body.split(TAB)
        fields += [""] * (len(cols) - len(fields))   # 尾欄是空的時候整欄會被省掉
        entry_id = fields[id_col]
        if entry_id not in found:
            continue
        if fields[yt_col].strip() and fields[yt_col].strip() != found[entry_id] and not force:
            print(f"  - {entry_id} 已經有 {fields[yt_col]}，不覆蓋（要蓋加 --force）")
            continue
        fields[yt_col] = found[entry_id]
        lines[i] = TAB.join(fields) + eol
        written.append(entry_id)

    if written:
        with TSV.open("w", encoding="utf-8", newline="") as f:
            f.writelines(lines)
    return written


def scan(yt, clips, force: bool) -> None:
    """從頻道的上傳清單反查影片 ID，不用自己去網址列抄。

    對應規則是「YouTube 標題 == 成品檔名的 stem」——把 1.mp4 拖上 Studio，
    標題預設就是「1」。已經改過標題的對不上，那種還是得自己填 tsv。
    """
    ch = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    by_stem = {c["stem"]: entry_id for entry_id, c in clips.items()}

    found: dict[str, str] = {}
    req = yt.playlistItems().list(part="snippet", playlistId=uploads, maxResults=50)
    while req and len(found) < len(by_stem):
        res = req.execute()
        for item in res["items"]:                    # 清單是新到舊，同名標題取最新那支
            entry_id = by_stem.get(item["snippet"]["title"].strip())
            if entry_id and entry_id not in found:
                found[entry_id] = item["snippet"]["resourceId"]["videoId"]
        req = yt.playlistItems().list_next(req, res)

    for entry_id in sorted(by_stem.values()):
        vid = found.get(entry_id)
        print(f"  {entry_id}  {clips[entry_id]['stem']}.mp4  ->  {vid or '(頻道上找不到)'}")

    written = write_ids(found, force) if found else []
    print(f"\n{len(written)} 筆 ID 寫進 {TSV}")
    if written:
        print("下一步：python videos/upload.py")


# ── Google Sheet ───────────────────────────────────────────────

def live_rows() -> list[list[str]]:
    """讀 tsv，挑出「已經有影片」的條目（含表頭），順手存一份到 SHEET_OUT。

    tsv 保留全部 20 列（那是入門篇的規劃），但沒有影片的條目推到網站上只會變成
    點了說「找不到這個條目」的空卡片，所以對外的那份要濾過。
    """
    with TSV.open(encoding="utf-8", newline="") as f:
        lines = f.readlines()
    cols = lines[0].splitlines()[0].split(TAB)
    yt_col = cols.index("youtubeId")

    keep, rows = [lines[0]], [cols]
    for line in lines[1:]:
        fields = line.splitlines()[0].split(TAB)
        fields += [""] * (len(cols) - len(fields))
        if VIDEO_ID_RE.match(fields[yt_col].strip()):
            keep.append(line)
            rows.append(fields)

    with SHEET_OUT.open("w", encoding="utf-8", newline="") as f:
        f.writelines(keep)
    return rows


def sheet_id() -> str:
    """從網站設定挖出試算表 ID，免得兩邊各寫一份會對不上。"""
    url = json.loads(CONSTANTS.read_text(encoding="utf-8"))["sheetsUrl"]
    match = re.search("/spreadsheets/d/([A-Za-z0-9_-]+)", url)
    if not match:
        sys.exit(f"從 constants.json 的 sheetsUrl 解不出試算表 ID：{url}")
    return match.group(1)


def push_sheet(creds, yes: bool) -> None:
    """把 live_rows() 覆蓋進網站在讀的那張 Google Sheet 的第一個分頁。

    先 clear 再 update，不然刪掉條目時舊的列會留在表尾。網站是即時抓 sheet 的，
    寫完重新整理就看得到，不用重 build。
    """
    rows = live_rows()
    print(f"本機已產生 {SHEET_OUT}（{len(rows) - 1} 筆）")

    sheets = build("sheets", "v4", credentials=creds)
    sid = sheet_id()
    try:
        info = sheets.spreadsheets().get(spreadsheetId=sid).execute()
    except HttpError as e:
        if "SERVICE_DISABLED" in str(e) or e.resp.status == 403:
            sys.exit("Google Sheets API 沒啟用，或這個帳號沒有這張表的權限。\n"
                     "到 Cloud Console 的「API 和服務 > 程式庫」搜 Google Sheets API 按啟用。")
        raise

    tab = info["sheets"][0]["properties"]["title"]
    print(f"目標：{info['properties']['title']} / 分頁「{tab}」")
    for row in rows[1:]:
        print(f"  · {row[0]}  {row[1]}")

    if not yes and not confirm(f"要清空分頁「{tab}」並寫入這 {len(rows) - 1} 筆嗎？"):
        print("沒有動 Google Sheet。")
        return

    sheets.spreadsheets().values().clear(spreadsheetId=sid, range=tab).execute()
    sheets.spreadsheets().values().update(
        spreadsheetId=sid, range=f"{tab}!A1",
        valueInputOption="RAW", body={"values": rows},
    ).execute()
    print(f"已寫入 {len(rows) - 1} 筆，重新整理網站就會更新。")


# ── 主流程 ──────────────────────────────────────────────────────

def targets_from_tsv(rows, clips, wanted: list[str]) -> list[tuple[str, str]]:
    out = []
    for entry_id in sorted(clips):
        if wanted and entry_id not in wanted:
            continue
        video_id = (rows[entry_id].get("youtubeId") or "").strip()
        if video_id:
            out.append((entry_id, video_id))
    return out


def main() -> None:
    rows, clips = load()
    args = sys.argv[1:]
    flags = {a for a in args if a.startswith("--")}
    wanted = [a.upper() for a in args if not a.startswith("--")]

    missing = [e for e in wanted if e not in clips]
    if missing:
        sys.exit(f"trim.json 裡沒有這些條目：{', '.join(missing)}")

    if "--check" in flags:
        check(service())
        return
    if "--scan" in flags:
        scan(service(), clips, force="--force" in flags)
        return
    if "--sheet" in flags:
        push_sheet(credentials(), yes="--yes" in flags)
        return
    if "--publish" in flags:
        publish(service(), targets_from_tsv(rows, clips, wanted))
        return

    todo = []
    for entry_id, clip in sorted(clips.items()):
        if wanted and entry_id not in wanted:
            continue
        video_id = (rows[entry_id].get("youtubeId") or "").strip()
        if not video_id:
            print(f"- {entry_id} 還沒有 youtubeId，跳過（先在 Studio 傳 {clip['stem']}.mp4）")
            continue
        todo.append((entry_id, clip, video_id))

    if not todo:
        sys.exit("沒有可以處理的條目——先跑 --scan，或把影片 ID 填進 "
                 f"{TSV} 的 youtubeId 欄。")

    creds = credentials()
    yt = service(creds)
    playlist_id = ensure_playlist(yt)
    failed = []
    for entry_id, clip, video_id in todo:
        print(f"\n【{entry_id}】{rows[entry_id]['title']}  → {video_id}")
        try:
            push_meta(yt, video_id, build_meta(entry_id, rows[entry_id]))
            print("  標題／說明／標籤已套用")
            srt = OUT / f"{clip['stem']}.srt"
            print("  " + (push_caption(yt, video_id, srt) if srt.exists()
                          else f"! 找不到 {srt}，字幕跳過"))
            print("  " + add_to_playlist(yt, playlist_id, video_id))
        except (HttpError, RuntimeError) as e:
            print(f"  ! 失敗：{e}")
            failed.append(entry_id)

    print(f"\n完成 {len(todo) - len(failed)}/{len(todo)}。")
    if failed:
        print(f"失敗：{', '.join(failed)}")

    ok = [(e, v) for e, _, v in todo if e not in failed]
    if ok:
        print("\n── 隱私狀態 ──")
        publish(yt, ok)
        print("\n── Google Sheet ──")
        push_sheet(creds, yes=False)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
