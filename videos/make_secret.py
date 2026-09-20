"""手動產生 client_secret.json。

    python videos/make_secret.py

Google 從 2025 年起，OAuth 用戶端密鑰只在建立當下顯示一次，之後在 Console
看到的是遮蔽過的 ****，也沒有下載 JSON 的按鈕。如果當初沒存到，就到用戶端
詳細頁按「Add secret」新增一組，再用這支程式把檔案組回來。

密鑰用隱藏輸入讀，不會留在終端機歷史或畫面上。
"""
import json
from getpass import getpass
from pathlib import Path

DST = Path(__file__).parent / "client_secret.json"


def main() -> None:
    client_id = input("用戶端 ID（...apps.googleusercontent.com）：").strip()
    client_secret = getpass("用戶端密鑰（GOCSPX-...，輸入時不會顯示）：").strip()
    if not client_id.endswith(".apps.googleusercontent.com"):
        raise SystemExit("用戶端 ID 格式不對，應該以 .apps.googleusercontent.com 結尾。")
    if not client_secret:
        raise SystemExit("沒有輸入密鑰。")

    DST.write_text(json.dumps({"installed": {
        "client_id": client_id,
        "client_secret": client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": ["http://localhost"],
    }}, indent=2), encoding="utf-8")
    print(f"→ {DST}")


if __name__ == "__main__":
    main()
