<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import PixelIcon from './components/PixelIcon.vue'
import MinecraftWorld from './components/MinecraftWorld.vue'
import MinecraftItem from './components/MinecraftItem.vue'
import './assets/minecraft.css'
import TerrariaWorld from './components/TerrariaWorld.vue'
import TerrariaSprite from './components/TerrariaSprite.vue'
import './assets/terraria.css'
import { studyLoomApi, type ApiMember, type ApiStitch, type ApiTrack } from './services/api'

type Theme = 'minecraft' | 'terraria'

const fallbackMembers: ApiMember[] = [
  { id: 'member-rain', name: '小雨', initials: '雨', color: '#ef7f5a', active: true, active_minutes: 42 },
  { id: 'member-he', name: '阿禾', initials: '禾', color: '#5f8e7d', active: true, active_minutes: 18 },
  { id: 'member-lin', name: 'Lin', initials: 'L', color: '#7789b5', active: true, active_minutes: 60 },
  { id: 'member-you', name: '你', initials: '你', color: '#b07d9f', active: false, active_minutes: 0 },
]
const fallbackTrack: ApiTrack = {
  title: '夜空中最亮的星', artist: '逃跑计划', album: '世界', duration_seconds: 284,
  position_seconds: 136, playing: true, white_noise: '雨声', white_noise_volume: 30,
  next_dj: 'Lin', skip_votes: 2, votes_needed: 5,
}
const fallbackStitches: ApiStitch[] = [
  { id: 'stitch-1', author_id: 'member-he', author: '阿禾', initials: '禾', color: '#5f8e7d', created_at: '2026-09-14T21:06:00+08:00', content: '图书馆今晚很安静，适合把最后两章收尾。' },
  { id: 'stitch-2', author_id: 'member-rain', author: '小雨', initials: '雨', color: '#ef7f5a', created_at: '2026-09-14T20:42:00+08:00', content: '刚做完一套题，先休息十分钟。你们也加油 🧵' },
]

const roomName = ref('晚风自习室')
const memberCount = ref(4)
const collectiveMinutes = ref(1968)
const milestoneTargetMinutes = ref(2100)
const members = ref(fallbackMembers)
const track = ref(fallbackTrack)
const stitches = ref(fallbackStitches)
const isFocusing = ref(false)
const isSaving = ref(false)
const elapsedSeconds = ref(0)
const activeSessionId = ref<string | null>(null)
const message = ref('')
const connectionNote = ref('')
const hasLoadedRoom = ref(false)
const theme = ref<Theme>(localStorage.getItem('studyloom-theme') === 'terraria' ? 'terraria' : 'minecraft')
const journalOpen = ref(true)
const milestoneProgress = computed(() => Math.min(100, collectiveMinutes.value / Math.max(1, milestoneTargetMinutes.value) * 100))
const focusMembers = computed(() => members.value.map(member => member.id === 'member-you' && isFocusing.value ? { ...member, active: true, active_minutes: Math.floor(elapsedSeconds.value / 60) } : member))
function formatSeconds(value: number) { return Math.floor(value / 60).toString().padStart(2, '0') + ':' + Math.floor(value % 60).toString().padStart(2, '0') }
let timer: number | undefined

const collectiveHours = computed(() => Math.floor(collectiveMinutes.value / 60))
const collectiveRemainder = computed(() => collectiveMinutes.value % 60)
const activeCount = computed(() => focusMembers.value.filter((member) => member.active).length)
const nextMilestoneMinutes = computed(() => Math.max(0, milestoneTargetMinutes.value - collectiveMinutes.value))
const nextMilestoneLabel = computed(() => `${Math.floor(nextMilestoneMinutes.value / 60)} 小时 ${nextMilestoneMinutes.value % 60} 分`)
const trackProgress = computed(() => `${Math.min(100, (track.value.position_seconds / track.value.duration_seconds) * 100)}%`)
const timerLabel = computed(() => {
  const minutes = Math.floor(elapsedSeconds.value / 60).toString().padStart(2, '0')
  const seconds = (elapsedSeconds.value % 60).toString().padStart(2, '0')
  return `${minutes}:${seconds}`
})

function memberStatus(member: ApiMember) {
  if (member.id === 'member-you' && !member.active) return '准备开始'
  if (!member.active) return '暂时离开'
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
  try {
    const room = await studyLoomApi.room()
    roomName.value = room.name
    memberCount.value = room.member_count
    collectiveMinutes.value = room.collective_minutes
    milestoneTargetMinutes.value = room.milestone_target_minutes
    members.value = room.members
    track.value = room.track
    stitches.value = room.stitches
    hasLoadedRoom.value = true
    connectionNote.value = ''
  } catch {
    connectionNote.value = hasLoadedRoom.value ? '连接已断开 · 正在显示上次加载的数据' : '房间暂未连接 · 当前为示例数据，请连接后重试'
  }
}

async function toggleFocus() {
  if (isSaving.value) return
  isSaving.value = true
  connectionNote.value = ''
  try {
    if (!isFocusing.value) {
      const session = await studyLoomApi.startFocus()
      activeSessionId.value = session.id
      isFocusing.value = true
      timer = window.setInterval(() => elapsedSeconds.value += 1, 1000)
    } else if (activeSessionId.value) {
      const session = await studyLoomApi.stopFocus(activeSessionId.value)
      collectiveMinutes.value += session.duration_minutes ?? 0
      isFocusing.value = false
      activeSessionId.value = null
      if (timer) window.clearInterval(timer)
      timer = undefined
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
  } catch (error) {
    connectionNote.value = error instanceof Error ? error.message : '留言暂未保存，请重试'
  } finally {
    isSaving.value = false
  }
}

onMounted(loadRoom)
onBeforeUnmount(() => { if (timer) window.clearInterval(timer) })
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
      <div class="world-heading"><div class="world-path"><span>{{ theme === 'minecraft' ? '我的世界' : '泰拉大陆' }}</span><span>/</span>{{ roomName }}</div><span class="world-edition">{{ theme === 'minecraft' ? 'OVERWORLD' : 'TERRARIA WORLD' }} <i></i> 私密房间</span></div>
      <TerrariaWorld v-if="theme === 'terraria'" :room-name="roomName" :focusing="isFocusing" :active-count="activeCount"/>
      <MinecraftWorld v-else :room-name="roomName" :focusing="isFocusing" :active-count="activeCount" :minutes="collectiveMinutes"/>
      <p v-if="connectionNote" class="connection-note" role="status">{{ connectionNote }} <button @click="loadRoom">重新连接 ↻</button></p>
      <div class="dashboard">
        <section class="progress-panel panel" aria-labelledby="progress-title">
          <div class="panel-heading"><div><TerrariaSprite v-if="theme === 'terraria'" name="Work_Bench"/><MinecraftItem v-else name="diamond"/><h2 id="progress-title">{{ theme === 'terraria' ? '世界建造进度' : '进度 · 我们的主世界' }}</h2></div><span>集体专注</span></div>
          <div class="progress-content"><p class="muted">{{ theme === 'terraria' ? '从第一间木屋，到属于我们的城镇' : '将专注积累成经验，解锁村庄的新篇章' }}</p><div class="time-total"><strong>{{ collectiveHours }}</strong><span>小时</span><strong>{{ collectiveRemainder }}</strong><span>分钟</span></div>
            <div class="milestone-label"><span><PixelIcon kind="star"/>下一座里程碑</span><b>{{ Math.round(milestoneProgress) }}%</b></div>
            <div class="xp-bar" role="progressbar" aria-label="集体专注里程碑进度" :aria-valuenow="Math.round(milestoneProgress)" :aria-valuemin="0" :aria-valuemax="100"><span :style="{ width: milestoneProgress + '%' }"></span></div>
            <p class="milestone-note">再一起专注 <b>{{ nextMilestoneLabel }}</b>，{{ theme === 'minecraft' ? '解锁进度「更上一层楼」。' : '点亮新的微光。' }}</p>
            <div v-if="theme === 'terraria'" class="achievement-shelf"><div :class="{ unlocked: collectiveMinutes >= 600 }"><TerrariaSprite v-if="theme === 'terraria'" name="Work_Bench"/><MinecraftItem v-else name="crafting_table_front"/><span>{{ theme === 'terraria' ? '安家落户' : '初次开拓' }}</span><small>10 小时</small></div><div :class="{ unlocked: collectiveMinutes >= 1500 }"><TerrariaSprite v-if="theme === 'terraria'" name="Life_Crystal"/><PixelIcon v-else kind="tree"/><span>{{ theme === 'terraria' ? '生命之光' : '枝繁叶茂' }}</span><small>25 小时</small></div><div :class="{ unlocked: collectiveMinutes >= milestoneTargetMinutes }"><TerrariaSprite v-if="theme === 'terraria'" name="Forest_Pylon"/><PixelIcon v-else kind="chest"/><span>{{ theme === 'terraria' ? '晶塔相连' : '下一束光' }}</span><small>{{ Math.round(milestoneTargetMinutes / 60) }} 小时</small></div></div>
            <div v-else class="mc-advancements"><div class="mc-advancement" :class="{ unlocked: collectiveMinutes >= 600 }"><span><MinecraftItem name="crafting_table_front"/></span><b>开拓者</b><small>10 小时 · 放下第一块</small></div><div class="mc-advancement" :class="{ unlocked: collectiveMinutes >= 1500 }"><span><MinecraftItem name="book"/></span><b>知识就是力量</b><small>25 小时 · 建起图书馆</small></div><div class="mc-advancement" :class="{ unlocked: collectiveMinutes >= milestoneTargetMinutes }"><span><MinecraftItem name="diamond"/></span><b>更上一层楼</b><small>{{ Math.round(milestoneTargetMinutes / 60) }} 小时 · 新篇章</small></div></div>
          </div>
        </section>
        <section class="focus-panel panel" aria-labelledby="focus-title"><div class="panel-heading"><div><TerrariaSprite v-if="theme === 'terraria'" name="Campfire"/><MinecraftItem v-else name="crafting_table_front"/><h2 id="focus-title">{{ theme === 'minecraft' ? '你的工作台' : '篝火旁的时光' }}</h2></div><span>{{ isFocusing ? '专注进行中' : '准备就绪' }}</span></div>
          <div class="focus-content"><div v-if="theme === 'minecraft'" class="mc-crafting" aria-label="装饰性合成界面：把时间变成经验"><div class="mc-crafting-grid"><span v-for="slot in 9" :key="slot" class="mc-slot"><MinecraftItem v-if="[2, 5, 8].includes(slot)" :name="slot === 8 ? 'book' : 'diamond'"/></span></div><span aria-hidden="true">➜</span><span class="mc-slot mc-crafting-output"><MinecraftItem name="diamond_pickaxe"/></span></div><div v-if="theme === 'terraria'" class="tr-focus-buff"><TerrariaSprite name="Campfire"/><span>温暖篝火<small>{{ isFocusing ? '专注进行中' : '在这里，安心做自己的事' }}</small></span></div><p class="eyebrow">{{ isFocusing ? 'ONE MINUTE AT A TIME' : 'MAKE ROOM FOR A LITTLE FOCUS' }}</p><div class="timer" role="timer" aria-label="本次专注时长">{{ timerLabel }}</div><p>{{ isFocusing ? '安静地做自己的事，我们都在这里。' : '不必急着抵达，先从这一分钟开始。' }}</p><button class="focus-button" :disabled="isSaving" @click="toggleFocus"><TerrariaSprite v-if="theme === 'terraria'" :name="isFocusing ? 'Gold_Chest' : 'Copper_Pickaxe'"/><MinecraftItem v-else :name="isFocusing ? 'emerald' : 'diamond_pickaxe'"/>{{ isSaving ? '正在保存…' : isFocusing ? '结束专注 · 保存时光' : '开始专注' }}<span>{{ isFocusing ? '■' : '▶' }}</span></button><small>专注时，留言会暂时收起</small></div>
        </section>
        <section id="radio" class="radio-panel panel" aria-labelledby="radio-title"><div class="panel-heading"><div><TerrariaSprite v-if="theme === 'terraria'" name="Music_Box"/><MinecraftItem v-else name="jukebox_side"/><h2 id="radio-title">{{ theme === 'terraria' ? '营地音乐盒' : '唱片机' }}</h2></div><span>房间曲目</span></div><div class="radio-content"><div class="record-cover"><TerrariaSprite v-if="theme === 'terraria'" name="Music_Box"/><MinecraftItem v-else name="jukebox_side"/><span class="sound-bars" aria-hidden="true"><i></i><i></i><i></i><i></i></span></div><div class="track-info"><strong>{{ track.title }}</strong><span>{{ track.artist }} · {{ track.album }}</span></div><div class="track-progress"><span :style="{ width: trackProgress }"></span></div><div class="track-times"><span>{{ formatSeconds(track.position_seconds) }}</span><span>{{ formatSeconds(track.duration_seconds) }}</span></div><div class="radio-detail"><span>≈ {{ track.white_noise || '环境音关闭' }}</span><span>{{ track.white_noise_volume }}%</span></div><p class="dj-note">下一首由 <strong>{{ track.next_dj }}</strong> 选择</p></div></section>
      </div>
      <section id="companions" class="companions panel" aria-labelledby="companions-title"><div class="panel-heading"><div><PixelIcon :kind="theme === 'minecraft' ? 'heart' : 'life'"/><h2 id="companions-title">{{ theme === 'terraria' ? '城镇居民 · 同行的冒险者' : '同一片世界里的伙伴' }}</h2></div><span>{{ memberCount }} 位成员</span></div><div class="member-list"><article v-for="member in focusMembers" :key="member.id" class="member" :class="{ 'is-active': member.active }"><div class="portrait" :style="{ '--avatar-color': member.color }"><svg v-if="theme === 'terraria'" class="tr-player" viewBox="0 0 16 24" aria-hidden="true" shape-rendering="crispEdges"><path fill="#18213b" d="M4 1h8v3h2v7h-2v2h2v7h-2v4H8v-3H7v3H3v-5H1v-6h3z"/><path fill="#a07651" d="M4 2h7v2h2v3H3V4h1z"/><path fill="#edbf90" d="M4 6h8v5H4zM2 14h2v5H2zm10 0h2v5h-2z"/><path fill="#f8dab0" d="M6 6h6v3H6z"/><path fill="#263145" d="M10 7h2v2h-2z"/><path fill="var(--avatar-color)" d="M4 12h8v7H4z"/><path fill="#6782a5" d="M4 19h3v3H4zm5 0h3v3H9z"/><path fill="#b5d1de" opacity=".5" d="M4 13h2v5H4z"/></svg><span v-else class="pixel-face"><i></i></span><span class="member-presence"></span></div><div><strong>{{ member.name }} <small v-if="member.id === 'member-you'">YOU</small></strong><p>{{ memberStatus(member) }}</p></div><PixelIcon v-if="member.active" :kind="theme === 'minecraft' ? 'pickaxe' : 'star'"/></article></div></section>
      <section id="journal" class="journal panel" aria-labelledby="journal-title"><div class="panel-heading"><div><PixelIcon kind="book"/><h2 id="journal-title">营地留言簿</h2><span class="journal-subtitle">休息一下，再继续出发</span></div><button :aria-expanded="journalOpen" aria-controls="journal-content" @click="journalOpen = !journalOpen">{{ journalOpen ? '收起 −' : '展开 +' }}</button></div><div v-if="journalOpen" id="journal-content"><div v-if="isFocusing" class="folded-stitches"><PixelIcon kind="book"/>{{ stitches.length }} 条留言在这里等你，休息时再来看。</div><div v-else class="journal-body"><div class="stitch-list" aria-live="polite"><article v-for="stitch in stitches" :key="stitch.id" class="stitch"><span class="initial-avatar" :style="{ '--avatar-color': stitch.color }">{{ stitch.initials }}</span><div><div class="stitch-meta"><strong>{{ stitch.author }}</strong><time>{{ stitchTime(stitch.created_at) }}</time></div><p>{{ stitch.content }}</p></div></article><p v-if="!stitches.length" class="muted">这里还很安静，留下第一条留言吧。</p></div><form class="message-form" @submit.prevent="sendStitch"><label for="stitch-message">留句话，给同行的伙伴</label><textarea id="stitch-message" v-model="message" maxlength="180" placeholder="今天也有好好努力。" rows="3"></textarea><div><span>{{ message.length }} / 180</span><button :disabled="!message.trim() || isSaving">留下留言 ↗</button></div></form></div></div></section>
      <details v-if="theme === 'terraria'" class="tr-credits"><summary>关于这片泰拉世界 · 灵感与素材</summary><p>致敬 Terraria / Re-Logic。NPC 与物品精灵取自 Terraria Wiki 并保存在本地；场景为原创 SVG，学习对话为原创改写。星星收藏在离开主题或刷新后重置，晶塔用于切换主题风景。</p><a href="https://terraria.wiki.gg/wiki/Guide" target="_blank" rel="noreferrer">NPC · 向导 ↗</a><a href="https://terraria.wiki.gg/wiki/Inventory" target="_blank" rel="noreferrer">物品栏 ↗</a><a href="https://terraria.wiki.gg/wiki/Biomes" target="_blank" rel="noreferrer">生态环境 ↗</a><a href="https://terraria.huijiwiki.com/wiki/首页" target="_blank" rel="noreferrer">灰机 Wiki ↗</a><a href="https://terraria.fandom.com/wiki/Terraria_Wiki" target="_blank" rel="noreferrer">Fandom Wiki ↗</a></details>
      <details v-if="theme === 'minecraft'" class="mc-credits"><summary>世界档案 · 灵感与素材</summary><p>致敬 Minecraft / Mojang Studios。九格快捷栏、经验条、工作台与村民职业参考中文 Minecraft Wiki；村庄场景及生物插画为原创 SVG。方块与物品贴图为 Minecraft 游戏素材，本地保存，来源记录见项目素材清单。本项目为非官方学习主题。</p><p>这里的经验等级、进度名称与村民对话是自习主题的创意改编；快捷栏切换风景，访客发现会在离开主题后重置。</p><a href="https://zh.minecraft.wiki/" target="_blank" rel="noreferrer">中文 Minecraft Wiki ↗</a><a href="https://zh.minecraft.wiki/w/平视显示器" target="_blank" rel="noreferrer">平视显示器 ↗</a><a href="https://zh.minecraft.wiki/w/村民" target="_blank" rel="noreferrer">村民与职业 ↗</a><a href="https://zh.minecraft.wiki/w/生物群系" target="_blank" rel="noreferrer">生物群系 ↗</a></details>
      <footer><span><PixelIcon :kind="theme === 'minecraft' ? 'grass' : 'tree'"/>StudyLoom · 小小世界，慢慢生长</span><span>不比较进度，只分享陪伴。</span></footer>
    </main>
  </div>
</template>
