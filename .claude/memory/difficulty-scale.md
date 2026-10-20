---
name: difficulty-scale
description: Unity短片辭典的難度等級規劃到 Lv10，目前網站選項與條目只用到 Lv5
metadata:
  type: project
---

難度等級（difficulty）長期規劃會到 Lv10，Lv5 不是最高級；但目前網站的難度選項、tsv 條目都只用到 Lv5 為止。（2026-10-21 使用者說明）

**Why:** 使用者說「Lv5 不是最高，未來會做到 Lv10，但目前選項最高到 5 就好」。

**How to apply:** 提新章節或調難度時不要把 Lv5 當成「最難、最進階」來描述；現階段新增條目難度上限是 5。之後要開放 Lv6 以上時，`src/App.vue` 的 `difficultyOptions`、`difficultyCounts` 和 `difficultyColor` 都要一起擴充。
