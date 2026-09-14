<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { studyLoomApi, type ApiMember, type ApiStitch, type ApiTrack } from './services/api'

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
let timer: number | undefined

const collectiveHours = computed(() => Math.floor(collectiveMinutes.value / 60))
const collectiveRemainder = computed(() => collectiveMinutes.value % 60)
const activeCount = computed(() => members.value.filter((member) => member.active).length)
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
  if (member.active_minutes >= 60) return `已编织 ${Math.floor(member.active_minutes / 60)} 小时`
  return `已编织 ${member.active_minutes} 分钟`
}

function stitchTime(createdAt: string) {
  return new Intl.DateTimeFormat('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date(createdAt))
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
    connectionNote.value = ''
  } catch {
    connectionNote.value = '暂时连不上房间，正在展示最近一次织物'
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
    connectionNote.value = error instanceof Error ? error.message : '这枚针脚暂时没有保存成功'
  } finally {
    isSaving.value = false
  }
}

onMounted(loadRoom)
onBeforeUnmount(() => { if (timer) window.clearInterval(timer) })
</script>

<template>
  <div class="app-shell" :class="{ 'focus-mode': isFocusing }">
    <header class="topbar">
      <a class="brand" href="#" aria-label="StudyLoom 首页">
        <span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span>
        <span>StudyLoom</span>
      </a>
      <div class="room-identity">
        <span class="room-dot"></span><span>{{ roomName }}</span><span class="member-count">{{ memberCount }} 位成员</span>
      </div>
      <button class="avatar" type="button" aria-label="打开个人菜单">你</button>
    </header>

    <p v-if="connectionNote" class="connection-note" role="status">{{ connectionNote }}</p>
    <main class="workspace">
      <section class="loom-panel" aria-labelledby="loom-title">
        <div class="section-heading">
          <div><p class="eyebrow">本周经线 · 第 37 周</p><h1 id="loom-title">我们正在编织</h1></div>
          <div class="collective-time"><strong>{{ collectiveHours }}</strong><span>小时</span><strong>{{ collectiveRemainder }}</strong><span>分</span><small>全员共同积累</small></div>
        </div>

        <div class="fabric-stage" :aria-label="`本周集体专注织物，已积累 ${collectiveHours} 小时 ${collectiveRemainder} 分`">
          <div class="fabric-shadow"></div>
          <div class="fabric">
            <div v-for="row in 12" :key="row" class="fabric-row">
              <span v-for="column in 18" :key="column" :class="['thread', `thread-${(row + column) % 5}`]"></span>
            </div>
            <span class="milestone milestone-one" title="10 小时里程碑"></span>
            <span class="milestone milestone-two" title="25 小时里程碑"></span>
          </div>
          <div class="fabric-caption"><span>周一</span><span class="progress-note"><i></i> 距离下一束微光还有 {{ nextMilestoneLabel }}</span><span>周日</span></div>
        </div>

        <div class="weaving-now">
          <div class="weaving-label"><span class="pulse"></span><strong>{{ activeCount }} 人正在编织</strong></div>
          <div class="member-list">
            <div v-for="member in members" :key="member.id" class="member">
              <span class="member-avatar" :style="{ '--avatar-color': member.color }">{{ member.initials }}</span>
              <span class="member-copy"><strong>{{ member.name }}</strong><small>{{ memberStatus(member) }}</small></span>
            </div>
          </div>
        </div>

        <div class="focus-action">
          <button class="focus-button" type="button" :disabled="isSaving" @click="toggleFocus">
            <span class="shuttle" aria-hidden="true"></span>
            <span v-if="!isFocusing"><strong>开始编织</strong><small>和大家安静地待一会儿</small></span>
            <span v-else><strong>结束本次编织</strong><small>已经专注 {{ timerLabel }}</small></span>
          </button>
          <p v-if="isFocusing" class="focus-whisper">针脚消息已折叠，休息时再慢慢看</p>
        </div>
      </section>

      <aside class="side-panel">
        <section class="radio-card" aria-labelledby="radio-title">
          <div class="card-heading">
            <div><p class="eyebrow">纬线 · 云电台</p><h2 id="radio-title">此刻一起听</h2></div><span class="live-badge">同步中</span>
          </div>
          <div class="album-art" aria-hidden="true"><span class="record"><i></i></span><span class="needle"></span></div>
          <div class="track-info"><strong>{{ track.title }}</strong><span>{{ track.artist }} · {{ track.album }}</span></div>
          <div class="track-progress"><span :style="{ width: trackProgress }"></span></div><div class="track-times"><span>02:16</span><span>-02:28</span></div>
          <div class="radio-actions">
            <button type="button" aria-label="白噪音">≈<span>{{ track.white_noise }} {{ track.white_noise_volume }}%</span></button>
            <button class="play-button" type="button" aria-label="暂停">Ⅱ</button>
            <button type="button" aria-label="投票跳过">↝<span>跳过 {{ track.skip_votes }}/{{ track.votes_needed }}</span></button>
          </div>
          <p class="dj-note">下一首由 <strong>{{ track.next_dj }}</strong> 选择</p>
        </section>

        <section class="stitch-card" :class="{ collapsed: isFocusing }" aria-labelledby="stitch-title">
          <div class="card-heading">
            <div><p class="eyebrow">针脚 · 9 月</p><h2 id="stitch-title">休息时聊聊</h2></div>
            <button class="book-button" type="button">针脚册 <span>›</span></button>
          </div>
          <div v-if="isFocusing" class="folded-stitches"><span class="folded-glow"></span><p>有 {{ stitches.length }} 枚针脚安静地留在这里</p></div>
          <template v-else>
            <form class="message-form" @submit.prevent="sendStitch">
              <label class="sr-only" for="stitch-message">写下一条针脚消息</label>
              <input id="stitch-message" v-model="message" maxlength="180" placeholder="留一枚针脚…" autocomplete="off" />
              <button type="submit" :disabled="!message.trim() || isSaving" aria-label="发送消息">↑</button>
            </form>
            <div class="stitch-list" aria-live="polite">
              <article v-for="stitch in stitches" :key="stitch.id" class="stitch">
                <span class="member-avatar small" :style="{ '--avatar-color': stitch.color }">{{ stitch.initials }}</span>
                <div><div class="stitch-meta"><strong>{{ stitch.author }}</strong><time>{{ stitchTime(stitch.created_at) }}</time></div><p>{{ stitch.content }}</p></div>
              </article>
            </div>
          </template>
        </section>
      </aside>
    </main>
  </div>
</template>
