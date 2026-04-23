<template>
  <div data-theme="k" class="app-root">
    <header class="app-header px-5 py-3 flex items-center gap-3 flex-wrap relative">

      <!-- Title -->
      <h1 class="site-title text-2xl font-bold flex items-center gap-2">
        <img :src="unityIcon" class="w-5 h-5 opacity-90" alt="Unity" />
        Unity 影片圖鑑
      </h1>

      <!-- Mobile filter toggle + clear -->
      <div class="sm:hidden ml-auto flex flex-col items-end gap-1">
        <button class="filter-toggle-btn" @click="filterOpen = true">
          <svg width="22" height="22" viewBox="0 0 15 15" fill="none">
            <path d="M1 3h13M3 7.5h9M5.5 12h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>
        <div v-if="query || activeTopic !== null || activeDifficulty !== null || sortBy !== null"
          class="w-full border-t border-white/10 pt-1 flex justify-end">
          <button class="header-clear-btn" @click="query = ''; activeTopic = null; activeDifficulty = null; sortBy = null">✕ 清除篩選</button>
        </div>
      </div>
    </header>

    <main class="relative z-10 max-w-screen-2xl mx-auto px-6 py-8">
      <!-- Filters -->
      <div class="filter-block hidden sm:flex sm:flex-col">
        <div class="filter-row">
          <span class="filter-label">搜尋</span>
          <div class="search-wrap">
            <svg class="search-icon" width="14" height="14" viewBox="0 0 15 15" fill="none">
              <path d="M10 6.5a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Zm-.72 3.72a4.5 4.5 0 1 1 .71-.71l2.76 2.75a.5.5 0 1 1-.71.71l-2.76-2.75Z" fill="currentColor"/>
            </svg>
            <input v-model="query" type="text" class="search-input" placeholder="搜尋標題、說明、關鍵字…" />
          </div>
        </div>
        <div class="filter-row">
          <span class="filter-label">難度</span>
          <button
            v-for="d in difficultyOptions" :key="d ?? 'all'"
            @click="activeDifficulty = d"
            :class="['chapter-btn', { active: activeDifficulty === d }]"
          >{{ d === null ? '全部' : d }}<span class="chip-count">{{difficultyCounts[d ?? 'all'] }}</span></button>
        </div>
        <div class="filter-row">
          <span class="filter-label">主題</span>
          <button
            :class="['chapter-btn', { active: activeTopic === null }]"
            @click="activeTopic = null"
          >全部<span class="chip-count">{{difficultyCounts.all }}</span></button>
          <button
            v-for="t in topicOptions" :key="t"
            @click="activeTopic = t"
            :class="['chapter-btn', { active: activeTopic === t }]"
          >{{ kwLabel(t) }}<span class="chip-count">{{topicCounts[t] ?? 0 }}</span></button>
        </div>
        <div class="filter-row">
          <span class="filter-label">排序</span>
          <button :class="['chapter-btn', { active: sortBy === null }]" @click="sortBy = null">預設</button>
          <button :class="['chapter-btn', { active: sortBy === 'diff-asc' }]" @click="sortBy = 'diff-asc'">難度 ↑</button>
          <button :class="['chapter-btn', { active: sortBy === 'diff-desc' }]" @click="sortBy = 'diff-desc'">難度 ↓</button>
        </div>
        <div v-if="query || activeTopic !== null || activeDifficulty !== null || sortBy !== null" class="filter-row">
          <span class="filter-label" style="visibility:hidden">x</span>
          <button class="chapter-btn clear-btn" @click="query = ''; activeTopic = null; activeDifficulty = null; sortBy = null">✕ 清除篩選</button>
        </div>
      </div>

      <p v-if="query" class="results-hint">找到 {{ filtered.length }} 筆結果</p>

      <div v-if="filtered.length === 0" class="empty-state">
        <p>找不到符合的條目</p>
        <p class="empty-sub">試試其他關鍵字或清除篩選</p>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        <div v-for="entry in filtered" :key="entry.id" class="t-card">
          <!-- 手機：全寬標題 -->
          <h2 class="sm:hidden t-card-title font-semibold text-lg px-3 pt-3 line-clamp-2 cursor-pointer hover:opacity-80 transition-opacity" @click="openModal(entry)">{{ entry.title }}</h2>

          <!-- 縮圖 + 內容 row -->
          <div class="t-card-body-row">
            <!-- Thumb -->
            <div class="t-thumb" @click="openModal(entry)">
              <img v-if="isThumb(entry.thumb)" :src="getThumbSrc(entry.thumb)" :alt="entry.title" class="w-full h-full object-cover" />
              <span v-else class="text-3xl sm:text-5xl select-none">{{ entry.thumb || '🎮' }}</span>
              <div class="t-thumb-overlay"><span>[ OPEN ]</span></div>
            </div>

            <!-- Body -->
            <div class="flex flex-col flex-1 px-3 py-2 sm:p-4 gap-1 sm:gap-3 min-w-0">
              <!-- 桌機標題 -->
              <h2 class="hidden sm:block t-card-title font-semibold text-xl line-clamp-none cursor-pointer hover:opacity-80 transition-opacity" @click="openModal(entry)">{{ entry.title }}</h2>
              <!-- 關鍵字 -->
              <div class="flex flex-nowrap gap-1 sm:gap-1.5 overflow-hidden">
                <button class="t-tag shrink-0" @click="query = entry.topic">{{ kwLabel(entry.topic) }}</button>
                <template v-for="(kw, i) in entry.keywords.slice(0, 2)" :key="kw">
                  <button class="t-tag t-tag-dim shrink-0" @click="query = kw">{{ kwLabel(kw) }}</button>
                </template>
                <button v-if="entry.keywords.length > 2" class="t-tag t-tag-dim shrink-0" @click="openModal(entry)">+{{ entry.keywords.length - 2 }}</button>
              </div>
              <!-- 描述 -->
              <p class="t-card-desc text-xs sm:text-sm line-clamp-2 leading-snug">{{ entry.description }}</p>
              <!-- 難度 + YouTube -->
              <div class="mt-auto flex gap-2">
                <span v-if="entry.difficulty" :class="['flex items-center justify-center shrink-0 whitespace-nowrap px-2 text-xs rounded-lg font-semibold', difficultyColor[entry.difficulty]]">Lv. {{ entry.difficulty }}</span>
                <a :href="`https://www.youtube.com/watch?v=${entry.youtubeId}`" target="_blank" rel="noopener noreferrer"
                  class="flex-1 flex items-center justify-center gap-1.5 py-1 sm:py-2 rounded-lg bg-red-900/70 hover:bg-red-800/80 text-white/80 text-xs sm:text-sm font-medium transition-colors duration-200">
                  <svg class="w-3 h-3 sm:w-4 sm:h-4 shrink-0" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                  </svg>
                  前往 YouTube
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Mobile Filter Drawer -->
    <Teleport to="body">
      <template v-if="filterOpen">
        <div class="filter-drawer-backdrop" @click="filterOpen = false"></div>
        <div data-theme="k" class="filter-drawer" @click.stop>
          <div class="filter-drawer-header">
            <span class="filter-drawer-title">篩選</span>
            <button class="filter-drawer-close" @click="filterOpen = false">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div class="filter-drawer-section">
            <span class="filter-label">搜尋</span>
            <div class="search-wrap filter-drawer-search">
              <svg class="search-icon" width="14" height="14" viewBox="0 0 15 15" fill="none">
                <path d="M10 6.5a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Zm-.72 3.72a4.5 4.5 0 1 1 .71-.71l2.76 2.75a.5.5 0 1 1-.71.71l-2.76-2.75Z" fill="currentColor"/>
              </svg>
              <input v-model="query" type="text" class="search-input" placeholder="搜尋標題、說明、關鍵字…" />
            </div>
          </div>
          <div class="filter-drawer-section">
            <span class="filter-label">難度</span>
            <div class="filter-drawer-chips">
              <button
                v-for="d in difficultyOptions" :key="d ?? 'all'"
                @click="activeDifficulty = d"
                :class="['chapter-btn', { active: activeDifficulty === d }]"
              >{{ d === null ? '全部' : d }}<span class="chip-count">{{difficultyCounts[d ?? 'all'] }}</span></button>
            </div>
          </div>
          <div class="filter-drawer-section">
            <span class="filter-label">主題</span>
            <div class="filter-drawer-chips">
              <button
                :class="['chapter-btn', { active: activeTopic === null }]"
                @click="activeTopic = null"
              >全部<span class="chip-count">{{difficultyCounts.all }}</span></button>
              <button
                v-for="t in topicOptions" :key="t"
                @click="activeTopic = t"
                :class="['chapter-btn', { active: activeTopic === t }]"
              >{{ kwLabel(t) }}<span class="chip-count">{{topicCounts[t] ?? 0 }}</span></button>
            </div>
          </div>
          <div class="filter-drawer-section">
            <span class="filter-label">排序</span>
            <div class="filter-drawer-chips">
              <button :class="['chapter-btn', { active: sortBy === null }]" @click="sortBy = null">預設</button>
              <button :class="['chapter-btn', { active: sortBy === 'diff-asc' }]" @click="sortBy = 'diff-asc'">難度 ↑</button>
              <button :class="['chapter-btn', { active: sortBy === 'diff-desc' }]" @click="sortBy = 'diff-desc'">難度 ↓</button>
            </div>
          </div>
        </div>
      </template>
    </Teleport>

    <!-- Modal -->
    <Teleport to="body">
      <div v-if="modal" data-theme="k"
        class="fixed inset-0 z-50 overflow-y-auto sm:overflow-hidden sm:flex sm:items-center sm:justify-center"
        @click.self="closeModal">
        <div class="absolute inset-0 bg-black/85 backdrop-blur-sm" @click="closeModal"></div>

        <div class="t-modal-panel relative z-10 w-full sm:w-[90vw] sm:rounded-2xl overflow-hidden shadow-2xl flex flex-col sm:max-h-[96vh]">
          <!-- Video -->
          <div class="aspect-video sm:aspect-auto sm:h-[68vh] bg-black relative shrink-0">
            <iframe :src="`https://www.youtube.com/embed/${modal.youtubeId}`" class="w-full h-full"
              frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
          </div>

          <!-- Info -->
          <div class="p-5 sm:p-4 sm:overflow-y-auto">
            <div class="flex items-start justify-between gap-4">
              <div class="flex items-start gap-2 min-w-0">
                <span v-if="modal.difficulty" :class="['shrink-0 text-xs px-2 py-0.5 rounded-full font-semibold mt-1', difficultyColor[modal.difficulty]]">Lv. {{ modal.difficulty }}</span>
                <h2 class="t-modal-title text-xl font-bold">{{ modal.title }}</h2>
              </div>
              <!-- 桌機：YouTube + 關閉 並排於右上 -->
              <div class="hidden sm:flex shrink-0 items-center gap-2">
                <a :href="`https://www.youtube.com/watch?v=${modal.youtubeId}`" target="_blank" rel="noopener noreferrer"
                  class="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-red-900/70 hover:bg-red-800/80 text-white/80 text-sm font-semibold transition-colors duration-200">
                  <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                  </svg>
                  前往 YouTube
                </a>
                <button @click="closeModal"
                  class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border-2 border-current t-modal-title text-sm font-semibold hover:opacity-70 transition-opacity cursor-pointer">
                  <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                  關閉
                </button>
              </div>
            </div>
            <div class="mt-2 flex flex-wrap gap-1.5">
              <button class="t-tag" @click="query = modal.topic; closeModal()">{{ kwLabel(modal.topic) }}</button>
              <button v-for="kw in modal.keywords" :key="kw" class="t-tag t-tag-dim"
                @click="query = kw; closeModal()">{{ kwLabel(kw) }}</button>
            </div>
            <p class="t-card-desc mt-3 text-sm sm:text-base leading-relaxed sm:line-clamp-2">{{ modal.description }}</p>
            <div class="mt-5 flex gap-3">
              <a :href="`https://www.youtube.com/watch?v=${modal.youtubeId}`" target="_blank" rel="noopener noreferrer"
                class="sm:hidden flex-[7] flex items-center justify-center gap-2 py-2.5 rounded-xl bg-red-900/70 hover:bg-red-800/80 text-white/80 text-sm font-semibold transition-colors duration-200">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
                前往 YouTube
              </a>
              <button @click="closeModal"
                class="sm:hidden flex-[3] flex items-center justify-center gap-1.5 py-2.5 rounded-xl border-2 border-current t-modal-title text-sm font-semibold hover:opacity-70 transition-opacity cursor-pointer">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                </svg>
                關閉
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
    <footer class="relative z-10 mt-8 border-t border-white/10 px-6 py-6 text-center text-xs leading-relaxed t-card-desc">
      <p class="font-medium">弘光科大多遊系 Horazon(張仕明)製作</p>
      <p class="mt-2 opacity-70">最後更新時間：2026/4/22</p>
      <p class="mt-3 opacity-50">Unity 可能因版本差異或省略資訊而有錯誤，請見諒。<br>如有問題，可寄信至
        <a href="mailto:horazon@hk.edu.tw" class="underline hover:opacity-100 transition-opacity">horazon@hk.edu.tw</a>
      </p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import entries from './data/entries.json'
import kwMap from './data/keywords.json'

function kwLabel(kw) {
  const entry = kwMap[kw] ?? kwMap[kw.toLowerCase()]
  return entry?.label ?? kw
}

const unityIcon = '/UnityDictionary/unity.svg'

const modal = ref(null)
const filterOpen = ref(false)
watch(filterOpen, v => { document.body.style.overflow = v ? 'hidden' : '' })
const query = ref('')
const activeDifficulty = ref(null)
const activeTopic = ref(null)
const sortBy = ref(null)

const difficultyOptions = [null, 1, 2, 3, 4, 5]

const topicOptions = computed(() => {
  const seen = new Set()
  const list = []
  for (const e of entries) {
    if (e.topic && !seen.has(e.topic)) { seen.add(e.topic); list.push(e.topic) }
  }
  return list
})

function applyQuery(list) {
  if (!query.value.trim()) return list
  const q = query.value.toLowerCase()
  return list.filter(e =>
    e.title.toLowerCase().includes(q) ||
    e.description.toLowerCase().includes(q) ||
    kwLabel(e.topic).toLowerCase().includes(q) ||
    e.keywords.some(k => k.toLowerCase().includes(q) || kwLabel(k).toLowerCase().includes(q))
  )
}

const difficultyCounts = computed(() => {
  const base = applyQuery(activeTopic.value ? entries.filter(e => e.topic === activeTopic.value) : entries)
  const counts = { all: base.length }
  for (const d of [1,2,3,4,5]) counts[d] = base.filter(e => e.difficulty === d).length
  return counts
})

const topicCounts = computed(() => {
  const base = applyQuery(activeDifficulty.value ? entries.filter(e => e.difficulty === activeDifficulty.value) : entries)
  const counts = {}
  for (const e of base) counts[e.topic] = (counts[e.topic] ?? 0) + 1
  return counts
})

const filtered = computed(() => {
  let list = entries
  if (activeDifficulty.value !== null) list = list.filter(e => e.difficulty === activeDifficulty.value)
  if (activeTopic.value !== null) list = list.filter(e => e.topic === activeTopic.value)
  list = applyQuery(list)
  if (sortBy.value === 'diff-asc') list = [...list].sort((a, b) => (a.difficulty ?? 99) - (b.difficulty ?? 99))
  if (sortBy.value === 'diff-desc') list = [...list].sort((a, b) => (b.difficulty ?? 0) - (a.difficulty ?? 0))
  return list
})

function openModal(entry) { modal.value = entry }
function closeModal() { modal.value = null }
function isUrl(val) { return typeof val === 'string' && (val.startsWith('http') || val.startsWith('/')) }
function getThumbSrc(val) {
  if (!val || typeof val !== 'string') return null
  if (val.startsWith('http') || val.startsWith('/')) return val
  // 本地檔名 → public/thumbs/
  if (val.includes('.')) return `${import.meta.env.BASE_URL}thumbs/${val}`
  return null
}
function isThumb(val) { return !!getThumbSrc(val) }

const difficultyColor = {
  1: 'bg-green-500/20 text-green-400 border border-green-500/40',
  2: 'bg-sky-500/20 text-sky-400 border border-sky-500/40',
  3: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/40',
  4: 'bg-orange-500/20 text-orange-400 border border-orange-500/40',
  5: 'bg-red-500/20 text-red-400 border border-red-500/40',
}


</script>
