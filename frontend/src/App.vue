<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'

type Member = { name: string; initials: string; color: string; status: string }
type Stitch = { author: string; initials: string; color: string; time: string; content: string }

const members: Member[] = [
  { name: '小雨', initials: '雨', color: '#ef7f5a', status: '已编织 42 分钟' },
  { name: '阿禾', initials: '禾', color: '#5f8e7d', status: '已编织 18 分钟' },
  { name: 'Lin', initials: 'L', color: '#7789b5', status: '已编织 1 小时' },
  { name: '你', initials: '你', color: '#b07d9f', status: '准备开始' },
]

const stitches = ref<Stitch[]>([
  { author: '阿禾', initials: '禾', color: '#5f8e7d', time: '21:06', content: '图书馆今晚很安静，适合把最后两章收尾。' },
  { author: '小雨', initials: '雨', color: '#ef7f5a', time: '20:42', content: '刚做完一套题，先休息十分钟。你们也加油 🧵' },
])

const isFocusing = ref(false)
const elapsedSeconds = ref(0)
const message = ref('')
let timer: number | undefined

const timerLabel = computed(() => {
  const minutes = Math.floor(elapsedSeconds.value / 60).toString().padStart(2, '0')
  const seconds = (elapsedSeconds.value % 60).toString().padStart(2, '0')
  return `${minutes}:${seconds}`
})

function toggleFocus() {
  isFocusing.value = !isFocusing.value
  if (isFocusing.value) timer = window.setInterval(() => elapsedSeconds.value += 1, 1000)
  else if (timer) {
    window.clearInterval(timer)
    timer = undefined
  }
}

function sendStitch() {
  const content = message.value.trim()
  if (!content) return
  stitches.value.unshift({
    author: '你', initials: '你', color: '#b07d9f',
    time: new Intl.DateTimeFormat('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date()),
    content,
  })
  message.value = ''
}

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
        <span class="room-dot"></span><span>晚风自习室</span><span class="member-count">8 位成员</span>
      </div>
      <button class="avatar" type="button" aria-label="打开个人菜单">你</button>
    </header>

    <main class="workspace">
      <section class="loom-panel" aria-labelledby="loom-title">
        <div class="section-heading">
          <div><p class="eyebrow">本周经线 · 第 37 周</p><h1 id="loom-title">我们正在编织</h1></div>
          <div class="collective-time"><strong>32</strong><span>小时</span><strong>48</strong><span>分</span><small>全员共同积累</small></div>
        </div>

        <div class="fabric-stage" aria-label="本周集体专注织物，已完成百分之六十八">
          <div class="fabric-shadow"></div>
          <div class="fabric">
            <div v-for="row in 12" :key="row" class="fabric-row">
              <span v-for="column in 18" :key="column" :class="['thread', `thread-${(row + column) % 5}`]"></span>
            </div>
            <span class="milestone milestone-one" title="10 小时里程碑"></span>
            <span class="milestone milestone-two" title="25 小时里程碑"></span>
          </div>
          <div class="fabric-caption"><span>周一</span><span class="progress-note"><i></i> 距离下一束微光还有 2 小时 12 分</span><span>周日</span></div>
        </div>

        <div class="weaving-now">
          <div class="weaving-label"><span class="pulse"></span><strong>3 人正在编织</strong></div>
          <div class="member-list">
            <div v-for="member in members" :key="member.name" class="member">
              <span class="member-avatar" :style="{ '--avatar-color': member.color }">{{ member.initials }}</span>
              <span class="member-copy"><strong>{{ member.name }}</strong><small>{{ member.status }}</small></span>
            </div>
          </div>
        </div>

        <div class="focus-action">
          <button class="focus-button" type="button" @click="toggleFocus">
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
          <div class="track-info"><strong>夜空中最亮的星</strong><span>逃跑计划 · 世界</span></div>
          <div class="track-progress"><span></span></div><div class="track-times"><span>02:16</span><span>-02:28</span></div>
          <div class="radio-actions">
            <button type="button" aria-label="白噪音">≈<span>雨声 30%</span></button>
            <button class="play-button" type="button" aria-label="暂停">Ⅱ</button>
            <button type="button" aria-label="投票跳过">↝<span>跳过 2/5</span></button>
          </div>
          <p class="dj-note">下一首由 <strong>Lin</strong> 选择</p>
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
              <button type="submit" :disabled="!message.trim()" aria-label="发送消息">↑</button>
            </form>
            <div class="stitch-list" aria-live="polite">
              <article v-for="stitch in stitches" :key="`${stitch.author}-${stitch.time}-${stitch.content}`" class="stitch">
                <span class="member-avatar small" :style="{ '--avatar-color': stitch.color }">{{ stitch.initials }}</span>
                <div><div class="stitch-meta"><strong>{{ stitch.author }}</strong><time>{{ stitch.time }}</time></div><p>{{ stitch.content }}</p></div>
              </article>
            </div>
          </template>
        </section>
      </aside>
    </main>
  </div>
</template>
