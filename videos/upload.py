"""把標題／說明／標籤／字幕推到已經上傳的 YouTube 影片上。

    python videos/upload.py            # tsv 裡有 youtubeId 的條目全做
    python videos/upload.py BA01 BA02  # 只做指定條目
    python videos/upload.py --check    # 只驗證授權，印出連到哪個頻道
    python videos/upload.py --scan     # 從頻道反查影片 ID，自動填進 tsv
    python videos/upload.py --sheet    # 產出只含已上傳條目的 tsv，貼回 Google Sheet

影片檔本身請自己在 YouTube Studio 拖上去，不要用 API 傳：未通過 Google 審核的
API 專案，用 videos.insert 傳的片會被永久鎖成私人，事後在 Studio 也改不回公開，
只能整支重傳。videos.update 和 captions.insert 沒有這個限制，所以這支程式只做
上傳「之後」的雜事：

  1. videos.update   套上 meta.py 算出來的標題／說明／標籤／分類／語言
  2. captions.insert 上傳 3.output/*.srt（同語言的字幕軌已存在就改用 update）
  3. playlistItems.insert 加進播放清單「Unity短片辭典」（沒有就自動建）

影片 ID 從 design/sheet-rows-basics.tsv 的 youtubeId 欄讀。不想自己抄 ID 的話
先跑 --scan，它會照「YouTube 標題 == 成品檔名」把 ID 反查回來填好。

首次執行需要 videos/client_secret.json（Google Cloud 的 OAuth 桌面用戶端），
授權後 token 會快取在 videos/.youtube-token.json，兩個檔都在 .gitignore 裡。
設定步驟見 README.md。
"""
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
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

CATEGORY = "27"        # Education
LANG = "zh-Hant"       # 影片語言與字幕語言
CAPTION_NAME = "繁體中文"
PLAYLIST = "Unity短片辭典"
SHEET_OUT = TSV.parent / "sheet-current.tsv"
VIDEO_ID_RE = re.compile("^[A-Za-z0-9_-]{11}$")


def service():
    """拿到已授權的 youtube client；第一次會開瀏覽器要你登入。

    OAuth 同意畫面停在「測試中」的話，refresh token 只有 7 天壽命，過期後
    refresh 會拋 RefreshError——這裡接住它退回重新授權，不要讓程式直接炸掉。
    """
    creds = Credentials.from_authorized_user_file(TOKEN, SCOPES) if TOKEN.exists() else None
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
    return build("youtube", "v3", credentials=creds)


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


def write_ids(found: dict[str, str], force: bool) -> list[str]:
    """把影片 ID 寫回 tsv 的 youtubeId 欄，回傳真的有寫進去的條目。

    逐行處理而不是用 csv 模組：這張表是要整份貼回 Google Sheet 的，行尾（CRLF）
    和「沒有引號」的原樣都要保住，csv.writer 會自作主張加引號。
    """
    with TSV.open(encoding="utf-8", newline="") as f:
        lines = f.readlines()
    cols = lines[0].splitlines()[0].split("	")
    id_col, yt_col = cols.index("id"), cols.index("youtubeId")

    written = []
    for i, line in enumerate(lines[1:], start=1):
        body = line.splitlines()[0]
        eol = line[len(body):]
        fields = body.split("	")
        fields += [""] * (len(cols) - len(fields))   # 尾欄是空的時候整欄會被省掉
        entry_id = fields[id_col]
        if entry_id not in found:
            continue
        if fields[yt_col].strip() and fields[yt_col].strip() != found[entry_id] and not force:
            print(f"  - {entry_id} already has {fields[yt_col]}, left alone (use --force to overwrite)")
            continue
        fields[yt_col] = found[entry_id]
        lines[i] = "	".join(fields) + eol
        written.append(entry_id)

    if written:
        with TSV.open("w", encoding="utf-8", newline="") as f:
            f.writelines(lines)
    return written


def scan(yt, rows, clips, force: bool) -> None:
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
        print(f"  {entry_id}  {clips[entry_id]['stem']}.mp4  ->  {vid or '(not found on the channel)'}")

    written = write_ids(found, force) if found else []
    print(f"\n{len(written)} id(s) written to {TSV}")
    if written:
        print("Next: python videos/upload.py")


def sheet_rows() -> None:
    """輸出「只有已經上傳的條目」那幾列到 SHEET_OUT，整份貼回 Google Sheet 用。

    tsv 本身保留全部 20 列（那是入門篇的規劃），沒有影片的條目貼上去只會變成
    點了說「找不到這個條目」的空卡片，所以對外的那份要濾過。
    """
    TAB = chr(9)
    with TSV.open(encoding="utf-8", newline="") as f:
        lines = f.readlines()
    cols = lines[0].splitlines()[0].split(TAB)
    yt_col = cols.index("youtubeId")

    keep = [lines[0]]
    for line in lines[1:]:
        fields = line.splitlines()[0].split(TAB)
        fields += [""] * (len(cols) - len(fields))
        if VIDEO_ID_RE.match(fields[yt_col].strip()):
            keep.append(line)

    with SHEET_OUT.open("w", encoding="utf-8", newline="") as f:
        f.writelines(keep)
    print(f"{len(keep) - 1} row(s) -> {SHEET_OUT}")


def main() -> None:
    rows, clips = load()
    args = sys.argv[1:]
    if args and args[0] == "--check":
        check(service())
        return
    if args and args[0] == "--scan":
        scan(service(), rows, clips, force="--force" in args)
        return
    if args and args[0] == "--sheet":
        sheet_rows()
        return
    wanted = [a.upper() for a in args]

    todo = []
    for entry_id, clip in clips.items():
        if wanted and entry_id not in wanted:
            continue
        video_id = (rows[entry_id].get("youtubeId") or "").strip()
        if not video_id:
            print(f"- {entry_id} 還沒有 youtubeId，跳過（先在 Studio 傳 {clip['stem']}.mp4）")
            continue
        todo.append((entry_id, clip, video_id))
    todo.sort()

    missing = [e for e in wanted if e not in clips]
    if missing:
        sys.exit(f"trim.json 裡沒有這些條目：{', '.join(missing)}")
    if not todo:
        sys.exit("沒有可以處理的條目——先把 Studio 拿到的影片 ID 填進 "
                 f"{TSV} 的 youtubeId 欄。")

    yt = service()
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

    done = len(todo) - len(failed)
    print(f"\n完成 {done}/{len(todo)}。到 Studio 確認後再按發布。")
    if failed:
        sys.exit(f"失敗：{', '.join(failed)}")


if __name__ == "__main__":
    main()
