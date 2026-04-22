# chapters.json 資料格式

章節資料，存放於 `src/data/chapters.json`。
與 entries.json 的 `chapter` 欄位對應。

## 欄位定義

| 欄位 | 類型 | 說明 |
|------|------|------|
| `number` | number | 章節編號，用於排序與對應 entries 的 `chapter` |
| `name` | string | 章節名稱 |

## 範例

```json
{
  "number": 1,
  "name": "Physics 基礎"
}
```
