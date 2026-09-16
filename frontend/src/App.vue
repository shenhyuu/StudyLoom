<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import PixelIcon from './components/PixelIcon.vue'
import RoomRadio from './components/RoomRadio.vue'
import MinecraftWorld from './components/MinecraftWorld.vue'
import MinecraftItem from './components/MinecraftItem.vue'
import MinecraftCrafting from './components/MinecraftCrafting.vue'
import MinecraftProgress from './components/MinecraftProgress.vue'
import './assets/minecraft.css'
import TerrariaWorld from './components/TerrariaWorld.vue'
import TerrariaSprite from './components/TerrariaSprite.vue'
import './assets/terraria.css'
import { studyLoomApi, identity, leaveRoom, type ApiMember, type ApiStitch } from './services/api'

type Theme = 'minecraft' | 'terraria'

let heartbeat: number | undefined
let focusStartedAt = 0
let loadingRoom = false
const roomName = ref('晚风自习室')
const memberCount = ref(0)
const collectiveMinutes = ref(0)
const milestoneTargetMinutes = ref(2100)
const members = ref<ApiMember[]>([])
const stitches = ref<ApiStitch[]>([])
const isFocusing = ref(false)
const isSaving = ref(false)
const elapsedSeconds = ref(0)
const activeSessionId = ref<string | null>(null)
const message = ref('')
const connectionNote = ref('')
const theme = ref<Theme>(localStorage.getItem('studyloom-theme') === 'terraria' ? 'terraria' : 'minecraft')
const journalOpen = ref(true)
const recipeStorageKey = `studyloom-recipes-${identity.id}`
function nextRecipeIndex() {
  const stored = Number(localStorage.getItem(recipeStorageKey) ?? 0)
  return Number.isSafeInteger(stored) && stored >= 0 ? stored : 0
}
const recipeIndex = ref(nextRecipeIndex())
function syncRecipe(sessionId: string | null) {
  if (!sessionId) { recipeIndex.value = nextRecipeIndex(); return }
  const key = `${recipeStorageKey}-${sessionId}`
  const stored = localStorage.getItem(key)
  const value = stored === null ? NaN : Number(stored)
  if (Number.isSafeInteger(value) && value >= 0) { recipeIndex.value = value; return }
  recipeIndex.value = nextRecipeIndex()
  localStorage.setItem(key, String(recipeIndex.value))
  localStorage.setItem(recipeStorageKey, String(recipeIndex.value + 1))
}
// Boss 顺序与分组参考 Terraria Wiki（https://wiki.biligame.com/tr/Boss），完整收录：
// 困难模式之前：史莱姆王 → 克苏鲁之眼 → 世界吞噬怪 → 克苏鲁之脑 → 蜂王 → 独眼巨鹿 → 骷髅王 → 血肉墙；
// 困难模式：史莱姆皇后 → 双子魔眼 → 毁灭者 → 机械骷髅王 → 世纪之花 → 石巨人 → 猪龙鱼公爵 → 光之女皇 → 拜月教邪教徒 → 月亮领主。
const bossMilestones = [
  { minutes: 120, name: '史莱姆王', sprite: 'King_Slime.gif' },
  { minutes: 300, name: '克苏鲁之眼', sprite: 'Eye_of_Cthulhu.gif' },
  { minutes: 480, name: '世界吞噬怪', sprite: '340px-Eater_of_Worlds.png' },
  { minutes: 660, name: '克苏鲁之脑', sprite: 'Brain_of_Cthulhu.gif' },
  { minutes: 840, name: '蜂王', sprite: 'Queen_Bee.gif' },
  { minutes: 1020, name: '独眼巨鹿', sprite: 'Deerclops.gif' },
  { minutes: 1200, name: '骷髅王', sprite: 'Skeletron.png' },
  { minutes: 1440, name: '血肉墙', sprite: '200px-Wall_of_Flesh.gif' },
  { minutes: 1620, name: '史莱姆皇后', sprite: 'Queen_Slime.png' },
  { minutes: 1800, name: '双子魔眼', sprite: 'The_Twins.gif' },
  { minutes: 1980, name: '毁灭者', sprite: 'The_Destroyer.png' },
  { minutes: 2100, name: '机械骷髅王', sprite: '246px-Skeletron_Prime.gif' },
  { minutes: 2340, name: '世纪之花', sprite: 'Plantera.gif' },
  { minutes: 2580, name: '石巨人', sprite: 'Golem.gif' },
  { minutes: 2820, name: '猪龙鱼公爵', sprite: 'Duke_Fishron.gif' },
  { minutes: 3060, name: '光之女皇', sprite: '340px-Empress_of_Light.gif' },
  { minutes: 3300, name: '拜月教邪教徒', sprite: 'Lunatic_Cultist.gif' },
  { minutes: 3600, name: '月亮领主', sprite: '340px-Moon_Lord.gif' },
] as const
const nextBossIndex = computed(() => bossMilestones.findIndex(boss => collectiveMinutes.value < boss.minutes))
const nextBoss = computed(() => nextBossIndex.value === -1 ? null : bossMilestones[nextBossIndex.value])
const bossTrackProgress = computed(() => {
  const index = nextBossIndex.value
  if (index === -1) return 100
  const target = bossMilestones[index]
  if (!target) return 100
  const from = index === 0 ? 0 : bossMilestones[index - 1]?.minutes ?? 0
  return Math.min(100, (collectiveMinutes.value - from) / (target.minutes - from) * 100)
})
const milestoneProgress = computed(() => theme.value === 'terraria'
  ? bossTrackProgress.value
  : Math.min(100, collectiveMinutes.value / Math.max(1, milestoneTargetMinutes.value) * 100))
const latestDefeatedIndex = computed(() => nextBossIndex.value === -1 ? bossMilestones.length - 1 : nextBossIndex.value - 1)
function bossCardClass(index: number) {
  const boss = bossMilestones[index]
  if (!boss) return {}
  return {
    unlocked: collectiveMinutes.value >= boss.minutes,
    fighting: index === nextBossIndex.value,
    latest: index === latestDefeatedIndex.value,
  }
}
function bossProgressStyle(index: number) {
  return index === nextBossIndex.value ? { '--boss-progress': `${Math.round(bossTrackProgress.value)}%` } : undefined
}
const bossTrackEl = ref<HTMLElement | null>(null)
// 默认滚动到正在挑战的 Boss，让最新击败的 Boss 一并可见
watch([theme, nextBossIndex], async () => {
  if (theme.value !== 'terraria') return
  await nextTick()
  const track = bossTrackEl.value
  const target = track?.querySelector('.boss-card.fighting, .boss-card.latest')
  if (track && target instanceof HTMLElement) {
    track.scrollTo({ left: target.offsetLeft - (track.clientWidth - target.offsetWidth) / 2, behavior: 'smooth' })
  }
}, { immediate: true, flush: 'post' })
const focusMembers = computed(() => members.value.map(member => member.id === identity.id && isFocusing.value ? { ...member, active: true, active_minutes: Math.floor(elapsedSeconds.value / 60) } : member))
let timer: number | undefined

const collectiveHours = computed(() => Math.floor(collectiveMinutes.value / 60))
const collectiveRemainder = computed(() => collectiveMinutes.value % 60)
const activeCount = computed(() => focusMembers.value.filter((member) => member.active).length)
const nextMilestoneMinutes = computed(() => theme.value === 'terraria'
  ? (nextBoss.value ? nextBoss.value.minutes - collectiveMinutes.value : 0)
  : Math.max(0, milestoneTargetMinutes.value - collectiveMinutes.value))
const nextMilestoneLabel = computed(() => `${Math.floor(nextMilestoneMinutes.value / 60)} 小时 ${nextMilestoneMinutes.value % 60} 分`)
const timerLabel = computed(() => {
  const minutes = Math.floor(elapsedSeconds.value / 60).toString().padStart(2, '0')
  const seconds = (elapsedSeconds.value % 60).toString().padStart(2, '0')
  return `${minutes}:${seconds}`
})

function memberStatus(member: ApiMember) {
  if (member.id === identity.id && !member.active) return '准备开始'
  if (!member.active) return '在线 · 休息中'
  if (member.active_minutes >= 60) return `专注中 · ${Math.floor(member.active_minutes / 60)} 小时`
  return `专注中 · ${member.active_minutes} 分钟`
}

function stitchTime(createdAt: string) {
  return new Intl.DateTimeFormat('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date(createdAt))
}

function setTheme(nextTheme: Theme) {
  theme.value = nextTheme
  localStorage.setItem('studyloom-theme', nextTheme)
}

async function loadRoom() {
  if (loadingRoom) return
  loadingRoom = true
  try {
    const room = await studyLoomApi.room()
    roomName.value = room.name
    memberCount.value = room.member_count
    collectiveMinutes.value = room.collective_minutes
    milestoneTargetMinutes.value = room.milestone_target_minutes
    members.value = room.members
    activeSessionId.value = room.active_session?.id ?? null
    syncRecipe(activeSessionId.value)
    isFocusing.value = !!room.active_session
    focusStartedAt = room.active_session ? Date.parse(room.active_session.started_at) : 0
    elapsedSeconds.value = focusStartedAt ? Math.max(0, Math.floor((Date.now() - focusStartedAt) / 1000)) : 0
    stitches.value = room.stitches
    connectionNote.value = ''
  } catch (error) {
    members.value = []
    memberCount.value = 0
    connectionNote.value = error instanceof Error ? error.message : '连接已断开，正在重试'
  } finally { loadingRoom = false }

}

async function toggleFocus() {
  if (isSaving.value) return
  isSaving.value = true
  connectionNote.value = ''
  try {
    if (!isFocusing.value) {
      const session = await studyLoomApi.startFocus()
      activeSessionId.value = session.id
      syncRecipe(session.id)
      isFocusing.value = true
      focusStartedAt = Date.parse(session.started_at)
      await loadRoom()
    } else if (activeSessionId.value) {
      const session = await studyLoomApi.stopFocus(activeSessionId.value)
      collectiveMinutes.value += session.duration_minutes ?? 0
      isFocusing.value = false
      activeSessionId.value = null
      syncRecipe(null)
      focusStartedAt = 0
      elapsedSeconds.value = 0
      await loadRoom()
    }
  } catch (error) {
    connectionNote.value = error instanceof Error ? error.message : '房间连接中断，请稍后再试'
  } finally {
    isSaving.value = false
  }
}

async function sendStitch() {
  const content = message.value.trim()
  if (!content || isSaving.value) return
  isSaving.value = true
  connectionNote.value = ''
  try {
    const stitch = await studyLoomApi.createStitch(content)
    stitches.value.unshift(stitch)
    message.value = ''
    await loadRoom()
  } catch (error) {
    connectionNote.value = error instanceof Error ? error.message : '留言暂未保存，请重试'
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  void loadRoom()
  heartbeat = window.setInterval(() => void loadRoom(), 5000)
  timer = window.setInterval(() => { if (focusStartedAt) elapsedSeconds.value = Math.max(0, Math.floor((Date.now() - focusStartedAt) / 1000)) }, 1000)
  window.addEventListener('pagehide', leaveRoom)
})
onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
  if (heartbeat) window.clearInterval(heartbeat)
  window.removeEventListener('pagehide', leaveRoom)
  leaveRoom()
})
</script>

<template>
  <div class="app-shell" :class="[theme, { 'focus-mode': isFocusing }]">
    <header class="topbar">
      <a class="brand" href="#home"><PixelIcon :kind="theme === 'minecraft' ? 'grass' : 'tree'"/><span>StudyLoom<small>一起专注，让世界生长</small></span></a>
      <nav class="top-links" aria-label="房间导航"><a href="#home" class="selected">自习世界</a><a href="#companions">同行伙伴</a><a href="#journal">留言小站</a></nav>
      <div class="theme-switcher" role="group" aria-label="选择世界风格">
        <button :class="{ active: theme === 'minecraft' }" :aria-pressed="theme === 'minecraft'" @click="setTheme('minecraft')"><PixelIcon kind="grass"/>Minecraft</button>
        <button :class="{ active: theme === 'terraria' }" :aria-pressed="theme === 'terraria'" @click="setTheme('terraria')"><PixelIcon kind="tree"/>Terraria</button>
      </div>
    </header>
    <main id="home" class="workspace">
      <div class="world-heading"><div class="world-path"><span>{{ theme === 'minecraft' ? '我的世界' : '泰拉大陆' }}</span><span>/</span>{{ roomName }}</div><span class="world-edition">{{ theme === 'minecraft' ? 'OVERWORLD' : 'TERRARIA WORLD' }} <i></i> 共享房间</span></div>
      <TerrariaWorld v-if="theme === 'terraria'" :room-name="roomName" :focusing="isFocusing" :active-count="activeCount"/>
      <MinecraftWorld v-else :room-name="roomName" :focusing="isFocusing" :active-count="activeCount" :minutes="collectiveMinutes"/>
      <p v-if="connectionNote" class="connection-note" role="status">{{ connectionNote }} <button @click="loadRoom">重新连接 ↻</button></p>
      <div class="dashboard">
        <section class="progress-panel panel" aria-labelledby="progress-title">
          <div class="panel-heading"><div><TerrariaSprite v-if="theme === 'terraria'" name="Work_Bench"/><MinecraftItem v-else name="diamond"/><h2 id="progress-title">{{ theme === 'terraria' ? '世界建造进度' : '进度 · 我们的主世界' }}</h2></div><span>集体专注</span></div>
          <div class="progress-content"><p class="muted">{{ theme === 'terraria' ? '从史莱姆王，一路挑战到月亮领主' : '从第一张工作台，到属于我们的图书馆' }}</p><div class="time-total"><strong>{{ collectiveHours }}</strong><span>小时</span><strong>{{ collectiveRemainder }}</strong><span>分钟</span></div>
            <MinecraftProgress v-if="theme === 'minecraft'" :minutes="collectiveMinutes"/>
            <div v-if="theme === 'terraria'" class="milestone-label"><span><PixelIcon kind="star"/>下一座里程碑</span><b>{{ Math.round(milestoneProgress) }}%</b></div>
            <div v-if="theme === 'terraria'" class="xp-bar" role="progressbar" aria-label="集体专注里程碑进度" :aria-valuenow="Math.round(milestoneProgress)" :aria-valuemin="0" :aria-valuemax="100"><span :style="{ width: milestoneProgress + '%' }"></span></div>
            <p v-if="theme === 'terraria'" class="milestone-note"><template v-if="theme === 'terraria' && nextBoss">再一起专注 <b>{{ nextMilestoneLabel }}</b>，唤醒 <b>{{ nextBoss.name }}</b>！</template><template v-else-if="theme === 'terraria'">月亮领主已被战胜，这片泰拉大陆由你们守护。</template></p>
            <div v-if="theme === 'terraria'" ref="bossTrackEl" class="achievement-shelf boss-track"><div v-for="(boss, index) in bossMilestones" :key="boss.sprite" class="boss-card" :class="bossCardClass(index)" :style="bossProgressStyle(index)"><span class="boss-icon"><span class="boss-icon-inner"><TerrariaSprite :name="boss.sprite" :label="boss.name"/></span></span><span>{{ boss.name }}</span><small>{{ boss.minutes / 60 }} 小时</small></div></div>
          </div>
        </section>
        <section class="focus-panel panel" aria-labelledby="focus-title"><div class="panel-heading"><div><TerrariaSprite v-if="theme === 'terraria'" name="Campfire"/><MinecraftItem v-else name="crafting_table"/><h2 id="focus-title">{{ theme === 'minecraft' ? '你的工作台' : '篝火旁的时光' }}</h2></div><span>{{ isFocusing ? '专注进行中' : '准备就绪' }}</span></div>
          <div class="focus-content"><MinecraftCrafting v-if="theme === 'minecraft'" :recipe-index="recipeIndex" :focusing="isFocusing"/><div v-if="theme === 'terraria'" class="tr-focus-buff"><TerrariaSprite name="Campfire"/><span>温暖篝火<small>{{ isFocusing ? '专注进行中' : '在这里，安心做自己的事' }}</small></span></div><p class="eyebrow">{{ isFocusing ? 'ONE MINUTE AT A TIME' : 'MAKE ROOM FOR A LITTLE FOCUS' }}</p><div class="timer" role="timer" aria-label="本次专注时长">{{ timerLabel }}</div><p>{{ isFocusing ? '安静地做自己的事，我们都在这里。' : '不必急着抵达，先从这一分钟开始。' }}</p><button class="focus-button" :disabled="isSaving" @click="toggleFocus"><TerrariaSprite v-if="theme === 'terraria'" :name="isFocusing ? 'Gold_Chest' : 'Copper_Pickaxe'"/><MinecraftItem v-else :name="isFocusing ? 'emerald' : 'diamond_pickaxe'"/>{{ isSaving ? '正在保存…' : isFocusing ? '结束专注 · 保存时光' : '开始专注' }}<span>{{ isFocusing ? '■' : '▶' }}</span></button><small>专注时，留言会暂时收起</small></div>
        </section>
        <RoomRadio :theme="theme"/>
      </div>
      <section id="companions" class="companions panel" aria-labelledby="companions-title"><div class="panel-heading"><div><PixelIcon :kind="theme === 'minecraft' ? 'heart' : 'life'"/><h2 id="companions-title">{{ theme === 'terraria' ? '城镇居民 · 同行的冒险者' : '同一片世界里的伙伴' }}</h2></div><span>{{ memberCount }} 人在线</span></div><div class="member-list"><p v-if="!members.length" class="muted">正在连接同行的伙伴…</p><article v-for="member in focusMembers" :key="member.id" class="member" :class="{ 'is-active': member.active }"><div class="portrait" :style="{ '--avatar-color': member.color }"><svg v-if="theme === 'terraria'" class="tr-player" viewBox="0 0 16 24" aria-hidden="true" shape-rendering="crispEdges"><path fill="#18213b" d="M4 1h8v3h2v7h-2v2h2v7h-2v4H8v-3H7v3H3v-5H1v-6h3z"/><path fill="#a07651" d="M4 2h7v2h2v3H3V4h1z"/><path fill="#edbf90" d="M4 6h8v5H4zM2 14h2v5H2zm10 0h2v5h-2z"/><path fill="#f8dab0" d="M6 6h6v3H6z"/><path fill="#263145" d="M10 7h2v2h-2z"/><path fill="var(--avatar-color)" d="M4 12h8v7H4z"/><path fill="#6782a5" d="M4 19h3v3H4zm5 0h3v3H9z"/><path fill="#b5d1de" opacity=".5" d="M4 13h2v5H4z"/></svg><span v-else class="pixel-face"><i></i></span><span class="member-presence"></span></div><div><strong>{{ member.name }} <small v-if="member.id === identity.id">YOU</small></strong><p>{{ memberStatus(member) }}</p></div><PixelIcon v-if="member.active" :kind="theme === 'minecraft' ? 'pickaxe' : 'star'"/></article></div></section>
      <section id="journal" class="journal panel" aria-labelledby="journal-title"><div class="panel-heading"><div><PixelIcon kind="book"/><h2 id="journal-title">营地留言簿</h2><span class="journal-subtitle">休息一下，再继续出发</span></div><button :aria-expanded="journalOpen" aria-controls="journal-content" @click="journalOpen = !journalOpen">{{ journalOpen ? '收起 −' : '展开 +' }}</button></div><div v-if="journalOpen" id="journal-content"><div v-if="isFocusing" class="folded-stitches"><PixelIcon kind="book"/>{{ stitches.length }} 条留言在这里等你，休息时再来看。</div><div v-else class="journal-body"><div class="stitch-list" aria-live="polite"><article v-for="stitch in stitches" :key="stitch.id" class="stitch"><span class="initial-avatar" :style="{ '--avatar-color': stitch.color }">{{ stitch.initials }}</span><div><div class="stitch-meta"><strong>{{ stitch.author }}</strong><time>{{ stitchTime(stitch.created_at) }}</time></div><p>{{ stitch.content }}</p></div></article><p v-if="!stitches.length" class="muted">这里还很安静，留下第一条留言吧。</p></div><form class="message-form" @submit.prevent="sendStitch"><label for="stitch-message">留句话，给同行的伙伴</label><textarea id="stitch-message" v-model="message" maxlength="180" placeholder="今天也有好好努力。" rows="3"></textarea><div><span>{{ message.length }} / 180</span><button :disabled="!message.trim() || isSaving">留下留言 ↗</button></div></form></div></div></section>
      <details v-if="theme === 'terraria'" class="tr-credits"><summary>关于这片泰拉世界 · 灵感与素材</summary><p>致敬 Terraria / Re-Logic。NPC、物品与 Boss 精灵取自 Terraria Wiki 并保存在本地；场景为原创 SVG，学习对话为原创改写。星星收藏在离开主题或刷新后重置，晶塔用于切换主题风景。</p><a href="https://terraria.wiki.gg/wiki/Guide" target="_blank" rel="noreferrer">NPC · 向导 ↗</a><a href="https://terraria.wiki.gg/wiki/Inventory" target="_blank" rel="noreferrer">物品栏 ↗</a><a href="https://terraria.wiki.gg/wiki/Biomes" target="_blank" rel="noreferrer">生态环境 ↗</a><a href="https://terraria.huijiwiki.com/wiki/首页" target="_blank" rel="noreferrer">灰机 Wiki ↗</a><a href="https://terraria.fandom.com/wiki/Terraria_Wiki" target="_blank" rel="noreferrer">Fandom Wiki ↗</a></details>
      <footer><span><PixelIcon :kind="theme === 'minecraft' ? 'grass' : 'tree'"/>StudyLoom · 小小世界，慢慢生长</span><span>不比较进度，只分享陪伴。</span></footer>
    </main>
  </div>
</template>

