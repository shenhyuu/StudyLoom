<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import MinecraftItem from './MinecraftItem.vue'
import TerrariaSprite from './TerrariaSprite.vue'
import { studyLoomApi, type MusicState } from '../services/api'

defineProps<{ theme: 'minecraft' | 'terraria' }>()
const audio = ref<HTMLAudioElement | null>(null)
const state = ref<MusicState | null>(null)
const position = ref(0)
const audioPosition = ref(0)
const listening = ref(false)
const audible = ref(false)
const blocked = ref(false)
const busy = ref(false)
const connected = ref(false)
const error = ref('')
const storedVolume = Number(localStorage.getItem('studyloom-volume') ?? 60)
const volume = ref(Number.isFinite(storedVolume) ? Math.max(0, Math.min(100, storedVolume)) : 60)
const lines = ref<{ time: number; text: string }[]>([])
const lyricNote = ref('')
const track = computed(() => state.value?.track)
const progress = computed(() => Math.min(100, position.value / Math.max(1, track.value?.duration_seconds ?? 0) * 100))
const lyric = computed(() => lines.value.filter(line => line.time <= (audible.value ? audioPosition.value : position.value)).at(-1)?.text || lyricNote.value || (lines.value.length ? '让旋律慢慢靠近' : '此曲为纯音乐，安心听就好'))
function formatTime(seconds: number) {
  return `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${Math.floor(seconds % 60).toString().padStart(2, '0')}`
}
watch(volume, value => {
  if (audio.value) audio.value.volume = value / 100
  localStorage.setItem('studyloom-volume', String(value))
})
let polling = false
let playing = false
let stopped = false
let lyricRequest = 0
let pollTimer: number | undefined
let clockTimer: number | undefined
function targetPosition() {
  const snapshot = state.value
  if (!snapshot?.track) return 0
  return Math.min(snapshot.track.duration_seconds, Math.max(0, snapshot.track.position_seconds + snapshot.transit_seconds + (performance.now() - snapshot.received_at) / 1000))
}
async function loadLyrics(url: string | null) {
  const id = ++lyricRequest
  lines.value = []
  lyricNote.value = url ? '字幕加载中…' : ''
  if (!url) return
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(10000) })
    if (!response.ok) throw new Error()
    const raw = await response.text()
    const offset = Number(raw.match(/\[offset:([+-]?\d+)\]/i)?.[1] ?? 0) / 1000
    const parsed: { time: number; text: string }[] = []
    for (const line of raw.split(/\r?\n/)) {
      const text = line.replace(/\[[^\]]*\]/g, '').trim()
      for (const match of line.matchAll(/\[(\d+):(\d{2})(?:[.:](\d+))?\]/g)) {
        parsed.push({ time: Number(match[1]) * 60 + Number(match[2]) + Number(`0.${match[3] || 0}`) + offset, text })
      }
    }
    if (!stopped && id === lyricRequest) { lines.value = parsed.sort((a, b) => a.time - b.time); lyricNote.value = '' }
  } catch {
    if (!stopped && id === lyricRequest) lyricNote.value = '字幕暂时无法读取'
  }
}
async function alignAudio(force = false) {
  const element = audio.value
  if (!element || !track.value || element.readyState < 1) return
  element.volume = volume.value / 100
  const target = targetPosition()
  const drift = target - element.currentTime
  if (force || Math.abs(drift) > 1) {
    element.currentTime = Math.min(target, Number.isFinite(element.duration) ? Math.max(0, element.duration - 0.05) : target)
    element.playbackRate = 1
  } else element.playbackRate = Math.abs(drift) > 0.15 ? (drift > 0 ? 1.02 : 0.98) : 1
  if (listening.value && connected.value && !blocked.value && element.paused && !playing) {
    playing = true
    try { await element.play() } catch (reason) {
      if (reason instanceof DOMException && reason.name === 'AbortError') return
      blocked.value = true
      audible.value = false
      error.value = '点击收听，继续与伙伴同步'
    } finally { playing = false }
  }
}
async function applyState(snapshot: MusicState) {
  if (stopped) return
  if (state.value && (snapshot.revision < state.value.revision || snapshot.server_time < state.value.server_time)) return
  const changed = snapshot.track?.id !== track.value?.id || snapshot.revision !== state.value?.revision
  const previousId = track.value?.id
  state.value = snapshot
  connected.value = true
  position.value = targetPosition()
  if (changed) {
    audio.value?.pause()
    audioPosition.value = position.value
    if (previousId !== snapshot.track?.id) { blocked.value = false; error.value = '' }
    if (previousId !== snapshot.track?.id) void loadLyrics(snapshot.track?.lyrics_url ?? null)
    await nextTick()
    if (previousId !== snapshot.track?.id) audio.value?.load()
  }
  await alignAudio(changed)
}
async function refresh() {
  if (polling || stopped) return
  polling = true
  try {
    await applyState(await studyLoomApi.music())
    if (!blocked.value) error.value = ''
  } catch (reason) {
    connected.value = false
    audio.value?.pause()
    error.value = reason instanceof Error ? reason.message : '房间音乐连接中断，正在重连'
  } finally { polling = false }
}
async function skip(direction: 'previous' | 'next') {
  if (busy.value || !state.value || !track.value) return
  busy.value = true
  try {
    await applyState(await studyLoomApi.skipMusic(direction, state.value.revision))
    error.value = ''
  } catch (reason) { error.value = reason instanceof Error ? reason.message : '切歌失败，请重试' }
  finally { busy.value = false }
}
async function toggleListening() {
  if (listening.value && !blocked.value) {
    listening.value = false
    audio.value?.pause()
    return
  }
  listening.value = true
  blocked.value = false
  error.value = ''
  // Invoke play in the click gesture; refresh will correct the room clock.
  await alignAudio(true)
  void refresh()
}
function onMetadata() { void alignAudio(true) }
function onVisibility() { if (document.visibilityState === 'visible') void refresh() }
onMounted(() => {
  void refresh()
  pollTimer = window.setInterval(() => void refresh(), 1000)
  clockTimer = window.setInterval(() => {
    if (connected.value) position.value = targetPosition()
    if (listening.value && connected.value) void alignAudio()
  }, 250)
  document.addEventListener('visibilitychange', onVisibility)
})
onBeforeUnmount(() => {
  stopped = true
  lyricRequest++
  window.clearInterval(pollTimer)
  window.clearInterval(clockTimer)
  audio.value?.pause()
  document.removeEventListener('visibilitychange', onVisibility)
})
</script>

<template>
  <section id="radio" class="radio-panel room-radio panel" :class="[theme === 'minecraft' ? 'vinyl-radio' : 'starlight-radio', { 'is-listening': audible }]" aria-labelledby="radio-title">
    <div class="panel-heading"><div><MinecraftItem v-if="theme === 'minecraft'" name="jukebox_side"/><TerrariaSprite v-else name="Music_Box"/><h2 id="radio-title">{{ theme === 'minecraft' ? '村庄唱片机' : '星夜音乐盒' }}</h2></div><span class="radio-live"><i :class="{ online: connected }"></i>{{ connected ? '房间同频' : '连接中' }}</span></div>
    <div class="radio-body">
      <div class="radio-stage" aria-hidden="true">
        <template v-if="theme === 'minecraft'"><span class="stage-caption">JUKEBOX / SHUFFLE</span><div class="vinyl"><MinecraftItem name="music_disc_cat"/></div><span class="tonearm"></span><span class="stage-light"></span></template>
        <template v-else><span class="stage-caption">MELODY UNDER THE STARS</span><i class="radio-star star-one">✦</i><i class="radio-star star-two">✧</i><i class="radio-star star-three">✦</i><span class="music-orbit"></span><TerrariaSprite name="Music_Box"/><span class="music-note note-one">♪</span><span class="music-note note-two">♫</span></template>
      </div>
      <div class="radio-song"><span class="song-eyebrow">随机电台 · 一起听这一首</span><h3>{{ track?.title || (connected ? '音乐库暂时为空' : '正在接收房间旋律…') }}</h3><p>{{ track?.artist || '让专注有一点背景音乐' }}</p></div>
      <div class="radio-subtitle"><span aria-hidden="true">{{ theme === 'minecraft' ? '♫' : '✧' }}</span><p>{{ track ? lyric : '旋律将在这里与你相遇' }}</p></div>
      <div class="radio-timeline" role="progressbar" aria-label="房间统一播放进度" :aria-valuenow="Math.round(position)" :aria-valuemin="0" :aria-valuemax="Math.ceil(track?.duration_seconds ?? 0)"><span :style="{ width: progress + '%' }"></span></div>
      <div class="radio-times"><time>{{ formatTime(position) }}</time><span>{{ audible ? '正在同频收听' : '房间旋律持续播放' }}</span><time>{{ formatTime(track?.duration_seconds ?? 0) }}</time></div>
      <div class="radio-controls">
        <button class="skip-button" aria-label="上一首，房间一起切换" :disabled="busy || !connected || !state?.can_previous" @click="skip('previous')"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5v14M19 5 8 12l11 7z"/></svg><span>上一首</span></button>
        <button class="listen-button" :disabled="!track || !connected" :aria-label="listening && !blocked ? '暂停自己收听' : '加入房间同步收听'" @click="toggleListening"><svg viewBox="0 0 24 24" aria-hidden="true"><path v-if="listening && !blocked" d="M7 5h3v14H7zM14 5h3v14h-3z"/><path v-else d="m8 5 11 7-11 7z"/></svg><span>{{ listening && !blocked ? '暂停收听' : '加入收听' }}</span></button>
        <button class="skip-button" aria-label="下一首，房间一起随机切换" :disabled="busy || !track || !connected" @click="skip('next')"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 5v14M5 5l11 7-11 7z"/></svg><span>下一首</span></button>
      </div>
      <div class="radio-volume"><button :aria-label="volume ? '静音自己的播放器' : '恢复自己的音量'" @click="volume = volume ? 0 : 60"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z"/><path v-if="volume" class="speaker-wave" d="M16 8q5 4 0 8"/><path v-else class="speaker-wave" d="m17 9 4 6m0-6-4 6"/></svg></button><input v-model.number="volume" type="range" min="0" max="100" aria-label="个人音量" :style="{ '--volume': volume + '%' }"/><span>{{ volume }}%</span></div>
      <p class="radio-footnote">切歌全房间同步 · 音量只影响你</p>
      <p v-if="error" class="radio-error" role="status">{{ error }}</p>
      <audio ref="audio" :src="track?.audio_url" preload="metadata" @loadedmetadata="onMetadata" @timeupdate="audioPosition = audio?.currentTime ?? 0" @play="audible = true" @pause="audible = false" @ended="refresh" @error="blocked = true; audible = false; error = '音频暂时无法播放，请重试收听或切换下一首'"></audio>
    </div>
  </section>
</template>

<style scoped>
.room-radio { --radio-accent: #99da62; --radio-surface: #272b22; --radio-line: #50594a; }
.room-radio.vinyl-radio { background: #252c23; color: #e8eadc; }
.room-radio.vinyl-radio .panel-heading { background: #343b2e; border-bottom-color: #151d12; }
.room-radio .panel-heading { padding: 12px 15px; }
.radio-live { display: flex; align-items: center; gap: 5px; font-size: 9px; }
.radio-live i { width: 5px; height: 5px; background: #878787; }
.radio-live i.online { background: var(--radio-accent); box-shadow: 0 0 8px #99da6255; }
.radio-body { padding: 16px 18px 18px; }
.radio-stage { height: 116px; position: relative; display: grid; place-items: center; overflow: hidden; }
.stage-caption { position: absolute; top: 10px; left: 12px; font: 8px 'Courier New', monospace; letter-spacing: 1.4px; }
.vinyl-radio .radio-stage { background: linear-gradient(90deg, #0003 2px, transparent 2px), url('/minecraft/oak_planks.png'); background-size: 25%, 64px; border: 3px solid #262017; box-shadow: inset 2px 2px #b6a28166, inset -3px -3px #0005; }
.vinyl-radio .stage-caption { color: #e6d4b7; text-shadow: 1px 1px #21190f; }
.vinyl { width: 77px; height: 77px; margin-top: 11px; border: 4px solid #1a1a18; border-radius: 50%; background: repeating-radial-gradient(circle, #30302c 0 2px, #1f201c 3px 4px); box-shadow: 3px 5px #0005; display: grid; place-items: center; animation: spin-record 12s linear infinite paused; }
.vinyl :deep(.mc-item) { width: 64px; height: 64px; }
.is-listening .vinyl { animation-play-state: running; }
.tonearm { position: absolute; width: 43px; height: 8px; right: calc(50% - 71px); top: 53px; background: #bdbbaa; border: 2px solid #44443c; transform: rotate(-40deg); box-shadow: 2px 3px #0004; }
.stage-light { position: absolute; right: 13px; bottom: 12px; width: 7px; height: 7px; background: #91af63; box-shadow: 0 0 0 3px #0005; }
.radio-song { margin: 15px 0 12px; min-width: 0; }
.song-eyebrow { font-size: 9px; letter-spacing: 1px; opacity: .6; }
.radio-song h3 { font-size: 15px; line-height: 1.5; margin: 5px 0; overflow-wrap: anywhere; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; min-height: 45px; }
.radio-song > p { font-size: 10px; opacity: .65; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.radio-subtitle { display: flex; gap: 9px; align-items: center; min-height: 58px; padding: 10px 12px; background: var(--radio-surface); border: 1px solid var(--radio-line); font-size: 10px; line-height: 1.7; }
.radio-subtitle > span { color: var(--radio-accent); font-size: 17px; }
.radio-subtitle p { overflow-wrap: anywhere; }
.radio-timeline { height: 6px; margin-top: 17px; background: #171a16; border: 1px solid #10120e; overflow: hidden; }
.radio-timeline > span { display: block; height: 100%; background: var(--radio-accent); transition: width .25s linear; }
.radio-times { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; font: 9px 'Courier New', monospace; opacity: .6; }
.radio-times > span { font-size: 8px; }
.radio-controls { display: grid; grid-template-columns: 1fr 1.35fr 1fr; gap: 7px; margin: 17px 0; }
.radio-controls button { display: flex; align-items: center; justify-content: center; gap: 5px; padding: 10px 3px; font-size: 10px; color: inherit; border: 2px solid #20251c; background: #626955; box-shadow: inset 1px 1px #adb397, inset -1px -2px #3b4231, 0 2px #171b13; }
.radio-controls .listen-button { color: #ecffde; background: #517638; box-shadow: inset 1px 1px #91b570, inset -1px -2px #344f24, 0 2px #171b13; }
.radio-controls button:hover:not(:disabled) { filter: brightness(1.15); }
.radio-controls button:disabled { opacity: .4; cursor: not-allowed; }
.radio-controls svg { width: 15px; height: 15px; fill: currentColor; stroke: currentColor; stroke-width: 1.5; }
.radio-volume { display: flex; gap: 10px; align-items: center; }
.radio-volume button { display: grid; place-items: center; background: none; border: 0; color: inherit; padding: 3px; }
.radio-volume svg { width: 17px; height: 17px; fill: currentColor; }
.speaker-wave { fill: none; stroke: currentColor; stroke-width: 1.5; }
.radio-volume input { appearance: none; height: 5px; flex: 1; min-width: 0; border-radius: 0; background: linear-gradient(to right, var(--radio-accent) var(--volume), #494f42 var(--volume)); cursor: pointer; }
.radio-volume input::-webkit-slider-thumb { appearance: none; width: 10px; height: 14px; background: #dce4cc; border: 2px solid #242c20; }
.radio-volume input::-moz-range-thumb { width: 8px; height: 12px; border-radius: 0; background: #dce4cc; border: 2px solid #242c20; }
.radio-volume > span { width: 30px; text-align: right; font: 9px 'Courier New', monospace; opacity: .7; }
.radio-footnote { margin-top: 12px; font-size: 9px; opacity: .55; text-align: center; }
.radio-error { margin-top: 10px; font-size: 10px; color: #e8af87; line-height: 1.6; }
button:focus-visible, input:focus-visible { outline: 2px solid var(--radio-accent); outline-offset: 3px; }
.starlight-radio { --radio-accent: #d5b5f4; --radio-surface: #172442; --radio-line: #41577b; }
.starlight-radio .radio-stage { background: radial-gradient(ellipse at 50% 90%, #9988ce44, transparent 65%), linear-gradient(#17213e, #24375a); border: 1px solid #58719c; border-radius: 8px; box-shadow: inset 0 0 0 3px #0d183055; }
.starlight-radio .stage-caption { color: #b4c6e5; font-size: 7px; }
.starlight-radio .radio-stage > :deep(.terraria-sprite) { width: 61px; height: 61px; z-index: 1; margin-top: 14px; filter: drop-shadow(0 0 12px #c9b3e97a); }
.radio-star { position: absolute; color: #d9d8f9; font-style: normal; }
.star-one { top: 35px; left: 32px; font-size: 13px; }.star-two { top: 29px; right: 35px; font-size: 18px; }.star-three { bottom: 19px; right: 63px; font-size: 8px; }
.music-orbit { position: absolute; width: 128px; height: 43px; bottom: 12px; border: 1px solid #b9b4e544; border-radius: 50%; transform: rotate(-15deg); }
.music-note { position: absolute; color: #d7c0f1; opacity: .4; animation: float-note 3s ease-in-out infinite paused; }
.note-one { top: 48px; left: calc(50% - 59px); }.note-two { top: 40px; right: calc(50% - 56px); animation-delay: -1.5s; }
.is-listening .music-note { opacity: 1; animation-play-state: running; }
.starlight-radio .radio-subtitle { border-radius: 6px; }
.starlight-radio .radio-timeline { background: #111c35; border-color: #2e4266; border-radius: 5px; height: 5px; }
.starlight-radio .radio-timeline > span { background: linear-gradient(90deg, #779fce, #d5b5f4); }
.starlight-radio .radio-controls button { border: 1px solid #4f6389; border-radius: 6px; background: #283e62; box-shadow: inset 0 1px #6f8abd44, 0 2px #0e1930; }
.starlight-radio .radio-controls .listen-button { background: #685585; border-color: #a38ab8; box-shadow: inset 0 1px #c6b2e355, 0 2px #151a32; }
.starlight-radio .radio-volume input { border-radius: 6px; background: linear-gradient(to right, var(--radio-accent) var(--volume), #2c3c5c var(--volume)); }
.starlight-radio .radio-volume input::-webkit-slider-thumb { border-radius: 50%; height: 12px; width: 12px; border: 2px solid #3a4569; background: #ded3f5; }
.starlight-radio .radio-volume input::-moz-range-thumb { border-radius: 50%; height: 10px; width: 10px; border: 2px solid #3a4569; background: #ded3f5; }
@keyframes spin-record { to { transform: rotate(360deg); } }
@keyframes float-note { 50% { transform: translateY(-6px); } }
@media (min-width: 541px) and (max-width: 800px) { .radio-body { display: grid; grid-template-columns: 180px 1fr; gap: 0 23px; }.radio-stage { grid-column: 1; grid-row: 1/4; height: 155px; }.radio-song { margin-top: 0; }.radio-song, .radio-subtitle, .radio-timeline, .radio-times { grid-column: 2; }.radio-controls { grid-column: 1; grid-row: 4; }.radio-volume { grid-column: 2; grid-row: 4; }.radio-footnote, .radio-error { grid-column: 1/-1; } }
@media (prefers-reduced-motion: reduce) { .vinyl, .music-note { animation: none; }.radio-timeline > span { transition: none; } }
</style>
