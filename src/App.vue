<template>
  <div :data-theme="theme" class="app-root">
    <header class="app-header px-5 py-3 flex items-center gap-3 flex-wrap">

      <!-- Theme Dropdown -->
      <div class="theme-picker" ref="pickerRef">
        <button class="theme-picker-btn" @click="dropdownOpen = !dropdownOpen">
          <span class="theme-dot" :class="`dot-${theme}`"></span>
          {{ currentTheme.label }}
          <svg class="theme-picker-chevron w-3.5 h-3.5 ml-1" :class="{ open: dropdownOpen }"
            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
          </svg>
        </button>
        <div v-show="dropdownOpen" class="theme-picker-menu">
          <button
            v-for="t in themes" :key="t.id"
            @click="selectTheme(t.id)"
            :class="['theme-picker-item', { active: theme === t.id }]"
          >
            <span class="theme-dot" :class="`dot-${t.id}`"></span>
            {{ t.label }}
            <span class="theme-picker-item-desc">{{ t.desc }}</span>
          </button>
        </div>
      </div>

      <!-- Title -->
      <h1 class="site-title text-lg font-bold">Unity 字典</h1>

      <!-- Search -->
      <div class="search-wrap ml-auto">
        <svg class="search-icon" width="14" height="14" viewBox="0 0 15 15" fill="none">
          <path d="M10 6.5a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Zm-.72 3.72a4.5 4.5 0 1 1 .71-.71l2.76 2.75a.5.5 0 1 1-.71.71l-2.76-2.75Z" fill="currentColor"/>
        </svg>
        <input v-model="query" type="text" class="search-input" placeholder="搜尋標題、說明、關鍵字…" />
      </div>
    </header>

    <main class="relative z-10 max-w-6xl mx-auto px-6 py-8">
      <!-- Filters -->
      <div class="filter-block">
        <div class="filter-row">
          <span class="filter-label">難度</span>
          <button
            v-for="d in difficultyOptions" :key="d ?? 'all'"
            @click="activeDifficulty = d"
            :class="['chapter-btn', { active: activeDifficulty === d }]"
          >{{ d === null ? '全部' : d }}</button>
        </div>
        <div class="filter-row">
          <span class="filter-label">主題</span>
          <button
            :class="['chapter-btn', { active: activeTopic === null }]"
            @click="activeTopic = null"
          >全部</button>
          <button
            v-for="t in topicOptions" :key="t"
            @click="activeTopic = t"
            :class="['chapter-btn', { active: activeTopic === t }]"
          >{{ t }}</button>
        </div>
      </div>

      <p v-if="query" class="results-hint">找到 {{ filtered.length }} 筆結果</p>

      <div v-if="filtered.length === 0" class="empty-state">
        <p>找不到符合的條目</p>
        <p class="empty-sub">試試其他關鍵字或清除篩選</p>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <div v-for="entry in filtered" :key="entry.id" class="t-card">
          <!-- Thumb -->
          <div class="t-thumb" @click="openModal(entry)">
            <img v-if="isUrl(entry.thumb)" :src="entry.thumb" :alt="entry.title" class="w-full h-full object-cover" />
            <span v-else class="text-5xl select-none">{{ entry.thumb || '🎮' }}</span>
            <div class="t-thumb-overlay"><span>詳細資訊</span></div>
          </div>

          <!-- Body -->
          <div class="flex flex-col flex-1 p-4 gap-3">
            <div>
              <h2 class="t-card-title font-semibold">{{ entry.title }}</h2>
              <p class="t-card-desc mt-2 line-clamp-2">{{ entry.description }}</p>
            </div>
            <div class="flex flex-wrap gap-1.5">
              <button v-for="kw in entry.keywords" :key="kw" class="t-tag" @click="query = kw">{{ kw }}</button>
            </div>
            <div class="mt-auto pt-1">
              <a :href="`https://www.youtube.com/watch?v=${entry.youtubeId}`" target="_blank" rel="noopener noreferrer"
                class="flex items-center justify-center gap-2 w-full py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white text-sm font-medium transition-colors duration-200">
                <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
                前往 YouTube
              </a>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Modal -->
    <Teleport to="body">
      <div v-if="modal" :data-theme="theme" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="closeModal">
        <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="closeModal"></div>
        <div class="t-modal-panel relative z-10 w-full max-w-2xl overflow-hidden shadow-2xl">
          <div class="aspect-video bg-black">
            <iframe :src="`https://www.youtube.com/embed/${modal.youtubeId}`" class="w-full h-full"
              frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
          </div>
          <div class="p-6">
            <div class="flex items-start justify-between gap-4">
              <h2 class="t-modal-title text-xl font-bold">{{ modal.title }}</h2>
              <button @click="closeModal" class="shrink-0 p-1.5 rounded-lg text-gray-500 hover:text-gray-200 hover:bg-white/10 transition-colors cursor-pointer">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
            <p class="t-card-desc mt-3 text-sm leading-relaxed">{{ modal.description }}</p>
            <div class="mt-4 flex flex-wrap gap-2">
              <button v-for="kw in modal.keywords" :key="kw" class="t-tag" @click="query = kw; closeModal()">{{ kw }}</button>
            </div>
            <div class="mt-5">
              <a :href="`https://www.youtube.com/watch?v=${modal.youtubeId}`" target="_blank" rel="noopener noreferrer"
                class="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-red-600 hover:bg-red-500 text-white text-sm font-semibold transition-colors duration-200">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
                前往 YouTube
              </a>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import entries from './data/entries.json'

const themes = [
  { id: 'c', label: 'Cyberpunk',        desc: '霓虹紫 × 賽博龐克' },
  { id: 'd', label: 'Code Dark',        desc: '綠碼 × 程式編輯器' },
  { id: 'e', label: 'Retro Pixel',      desc: '像素電玩 × Synthwave' },
  { id: 'f', label: 'RPG Gold',         desc: '暗金 × 奇幻' },
  { id: 'g', label: 'Anime Pop',        desc: '亮色 × 日系動漫' },
  { id: 'h', label: 'JRPG Menu',        desc: '暗紫金 × 日式RPG' },
  { id: 'i', label: 'Glass HUD',        desc: '毛玻璃 × 青白 Sci-Fi' },
  { id: 'j', label: 'Vaporwave',        desc: '深紫粉 × 90年代美學' },
  { id: 'k', label: 'Tactical HUD',     desc: '極深藍 × 綠色軍事介面' },
]

const theme = ref('c')
const dropdownOpen = ref(false)
const pickerRef = ref(null)
const modal = ref(null)
const query = ref('')
const activeDifficulty = ref(null)
const activeTopic = ref(null)

const currentTheme = computed(() => themes.find(t => t.id === theme.value) ?? themes[0])

const difficultyOptions = [null, 1, 2, 3, 4, 5]

const topicOptions = computed(() => {
  const seen = new Set()
  const list = []
  for (const e of entries) {
    if (e.topic && !seen.has(e.topic)) { seen.add(e.topic); list.push(e.topic) }
  }
  return list
})

const filtered = computed(() => {
  let list = entries
  if (activeDifficulty.value !== null)
    list = list.filter(e => e.difficulty === activeDifficulty.value)
  if (activeTopic.value !== null)
    list = list.filter(e => e.topic === activeTopic.value)
  if (query.value.trim()) {
    const q = query.value.toLowerCase()
    list = list.filter(e =>
      e.title.toLowerCase().includes(q) ||
      e.description.toLowerCase().includes(q) ||
      e.keywords.some(k => k.toLowerCase().includes(q))
    )
  }
  return list
})

function selectTheme(id) { theme.value = id; dropdownOpen.value = false }
function openModal(entry) { modal.value = entry }
function closeModal() { modal.value = null }
function isUrl(val) { return typeof val === 'string' && (val.startsWith('http') || val.startsWith('/')) }

function onClickOutside(e) {
  if (pickerRef.value && !pickerRef.value.contains(e.target)) dropdownOpen.value = false
}
onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>
