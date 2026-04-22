# entries.json 資料格式

每個條目代表一個 Unity 功能說明，存放於 `src/data/entries.json`。

## 欄位定義

| 欄位 | 類型 | 說明 |
|------|------|------|
| `id` | string | 唯一識別碼，使用 kebab-case（例：`rigidbody-basics`） |
| `title` | string | 條目標題 |
| `chapter` | number | 所屬章節編號（例：`1`、`2`） |
| `keywords` | string[] | 關鍵字，用於搜尋與標記 |
| `description` | string | 文字說明 |
| `youtubeId` | string | YouTube 影片 ID（網址 `?v=` 後面的部分） |

## 範例

```json
{
  "id": "rigidbody-basics",
  "title": "Rigidbody 基礎",
  "chapter": 1,
  "keywords": ["rigidbody", "physics", "force"],
  "description": "介紹 Rigidbody 元件的基本用法，包含 AddForce 與重力設定。",
  "youtubeId": "YOUTUBE_ID"
}
```

## 注意事項

- `id` 必須唯一，不可重複
- `youtubeId` 只填 ID，不填完整網址
- `chapter` 為整數，從 1 開始
