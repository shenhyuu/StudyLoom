<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import MinecraftMob from './MinecraftMob.vue'
import MinecraftItem from './MinecraftItem.vue'
const props = defineProps<{ roomName: string; focusing: boolean; activeCount: number; minutes: number }>()
const biome = ref(0)
const night = ref(false)
const selected = ref(0)
const visitor = ref<'villager' | 'golem' | 'bee' | 'creeper'>('villager')
const dialogue = ref('嗯哼。欢迎来到自习村庄！把今天的任务拆成小块，一次完成一块。')
const discoveries = ref<string[]>([])
const biomes = ['平原', '樱花树林', '针叶林']
const tools = [
  { item: 'crafting_table', label: '工作台', action: 'focus' },
  { item: 'book', label: '留言簿', action: 'journal' },
  { item: 'emerald', label: '图书管理员', action: 'villager' },
  { item: 'compass', label: '切换群系', action: 'biome' },
  { item: 'torch', label: '昼夜切换', action: 'night' },
  { item: 'wheat', label: '蜜蜂', action: 'bee' },
  { item: 'music_disc_cat', label: '唱片机', action: 'radio' },
  { item: 'ender_pearl', label: '铁傀儡', action: 'golem' },
  { item: 'diamond', label: '进度', action: 'progress' },
]
const level = computed(() => Math.floor(props.minutes / 60))
function meet(kind: typeof visitor.value) {
  visitor.value = kind
  if (!discoveries.value.includes(kind)) discoveries.value.push(kind)
  dialogue.value = {
    villager: '嗯哼。讲台是我的工作站。你的工作台在哪里？从一个小目标开始吧。',
    golem: '村庄守卫已就位。安心专注吧，我会照看这片小小的世界。',
    bee: '嗡嗡！采一朵花的时间，也能读完一页书。别忘了在休息时伸个懒腰。',
    creeper: '嘶……今天不爆炸，只给你的灵感放个烟花。你发现了树后的秘密访客！',
  }[kind]
}
function useSlot(index: number) {
  const tool = tools[index]
  if (!tool) return
  selected.value = index
  if (tool.action === 'biome') biome.value = (biome.value + 1) % biomes.length
  else if (tool.action === 'night') night.value = !night.value
  else if (tool.action === 'villager' || tool.action === 'bee' || tool.action === 'golem') meet(tool.action)
  else document.getElementById(tool.action === 'focus' ? 'focus-title' : tool.action === 'progress' ? 'progress-title' : tool.action)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}
function keydown(event: KeyboardEvent) {
  if (event.target instanceof HTMLElement && (event.target.matches('input, textarea, select') || event.target.isContentEditable)) return
  if (event.ctrlKey || event.altKey || event.metaKey || event.repeat) return
  if (/^[1-9]$/.test(event.key)) { event.preventDefault(); useSlot(Number(event.key) - 1) }
}
onMounted(() => window.addEventListener('keydown', keydown))
onBeforeUnmount(() => window.removeEventListener('keydown', keydown))
</script>

<template>
  <section class="mc-world" :class="[{ 'mc-night': night || focusing }, `mc-biome-${biome}`]" aria-labelledby="room-title">
    <div class="mc-scene">
      <svg viewBox="0 0 1200 480" preserveAspectRatio="xMidYMid slice" class="mc-landscape" shape-rendering="crispEdges" role="img" :aria-label="`${biomes[biome]}中的方块村庄，橡木小屋、农田、树木与远山`">
        <defs>
          <pattern v-for="texture in ['oak_planks','cobblestone','dirt','oak_log','bookshelf']" :id="`mc-${texture}`" :key="texture" width="32" height="32" patternUnits="userSpaceOnUse"><image :href="`/minecraft/${biome === 2 && ['oak_planks', 'oak_log'].includes(texture) ? texture.replace('oak', 'spruce') : texture}.png`" width="32" height="32" /></pattern>
          <pattern id="mc-leaves" width="32" height="32" patternUnits="userSpaceOnUse"><rect width="32" height="32" class="mc-leaf-base"/><image :class="{ 'mc-tinted-leaves': biome !== 1 }" :href="`/minecraft/${biome === 1 ? 'cherry_leaves' : biome === 2 ? 'spruce_leaves' : 'oak_leaves'}.png`" width="32" height="32" /></pattern>
        </defs>
        <rect width="1200" height="480" class="mc-sky"/>
        <g class="mc-stars" fill="#fff6d0"><path d="M80 42h4v4h-4zM420 26h4v4h-4zM710 72h4v4h-4zM980 30h4v4h-4zM1120 110h4v4h-4zM580 99h4v4h-4zM920 98h4v4h-4z"/></g>
        <rect x="965" y="44" width="52" height="52" class="mc-sun"/>
        <g fill="#fff" opacity=".55" class="mc-clouds"><path d="M62 75h180v16H62zm28-16h100v16H90zM430 53h190v18H430zm50-16h80v16h-80zM1060 135h120v16h-120z"/></g>
        <path fill="#597b82" d="M0 250h90v-35h80v-40h90v45h110v-60h90v-45h60v60h70v70h90v-35h110v-70h75v-55h65v55h60v70h85v40h125v230H0z"/>
        <path fill="#668c52" d="M0 282h140v-32h110v30h170v-45h130v20h120v45h100v-45h130v-20h140v48h160v197H0z"/>
        <path fill="#80a951" d="M0 338h280v-22h170v22h230v-26h220v20h300v148H0z"/>
        <path fill="url(#mc-dirt)" d="M0 442h1200v38H0z"/><path fill="#609334" d="M0 434h1200v12H0z"/>
        <path fill="#bda16c" d="M700 346h82v38h100v34h210v16H774v-31h-88v-25h-60v-22h74z"/>
        <g v-for="(tree, i) in [{x:55,y:243},{x:380,y:255},{x:1010,y:209},{x:1110,y:268}]" :key="i" :transform="`translate(${tree.x} ${tree.y})`"><rect x="40" y="45" width="24" height="110" fill="url(#mc-oak_log)"/><path fill="url(#mc-leaves)" :d="biome === 2 ? 'M32 0h40v24h16v24h16v24h16v24H-8V72H8V48h16V24h8z' : 'M8 0h88v24h24v60H-16V24H8z'"/><path fill="#000" opacity=".12" d="M-16 68h136v16H-16z"/></g>
        <!-- A second cottage and sheltered reading terrace give the village a shared courtyard. -->
        <g transform="translate(238 263)">
          <path fill="#574538" d="M-16 32h16V16h24V0h112v16h24v16h16v16H-16z"/>
          <rect y="48" width="160" height="100" fill="url(#mc-oak_planks)"/><rect y="125" width="160" height="23" fill="url(#mc-cobblestone)"/>
          <path fill="#3d3428" d="M65 81h30v67H65z"/><path fill="#c4e8eb" d="M20 69h30v34H20zm90 0h30v34h-30z"/>
          <path stroke="#eff6dd" stroke-width="3" d="M35 69v34m-15-17h30m75-17v34m-15-17h30"/>
          <rect x="104" y="110" width="40" height="17" fill="url(#mc-bookshelf)"/>
        </g>
        <path fill="#d0b482" d="M324 411h70v15h240v-25h61v33H324z"/>
        <g transform="translate(448 310)">
          <path fill="#6b5138" d="M-12 16h12V0h104v16h12v12H-12z"/><rect y="28" width="8" height="93" fill="url(#mc-oak_log)"/><rect x="96" y="28" width="8" height="93" fill="url(#mc-oak_log)"/>
          <rect x="13" y="76" width="78" height="24" fill="url(#mc-bookshelf)"/><rect x="26" y="103" width="55" height="7" fill="url(#mc-oak_planks)"/><path fill="#624931" d="M29 110h6v15h-6zm43 0h6v15h-6z"/>
          <rect x="49" y="31" width="8" height="18" fill="#544431"/><rect x="44" y="43" width="18" height="20" fill="#ffe6a1" class="mc-torch-glow"/>
        </g>
        <g transform="translate(600 187)">
          <path fill="#473528" d="M-32 62h32V42h32V22h32V2h120v20h32v20h32v20h32v24H-32z"/>
          <path fill="url(#mc-oak_planks)" d="M0 72h248v132H0z"/><path fill="url(#mc-cobblestone)" d="M0 174h248v30H0zM0 72h24v132H0zm224 0h24v132h-24z"/>
          <path fill="#6d4c30" d="M-32 62h312v12H-32zM0 42h248v10H0zM32 22h184v10H32z"/>
          <rect x="100" y="117" width="48" height="87" fill="#423120"/><path fill="#936f40" d="M104 122h36v35h-36zm0 44h36v31h-36z"/><rect x="132" y="160" width="6" height="6" fill="#f1d882"/>
          <path fill="#b9e0de" d="M36 100h44v46H36zm132 0h44v46h-44z"/><path stroke="#e3f0da" stroke-width="4" d="M58 100v46m-22-23h44m110-23v46m-22-23h44"/>
          <rect x="34" y="151" width="48" height="23" fill="url(#mc-bookshelf)"/><rect x="166" y="151" width="48" height="23" fill="url(#mc-bookshelf)"/>
          <rect x="80" y="113" width="5" height="19" fill="#6f4429"/><rect x="78" y="105" width="9" height="10" fill="#ffc755" class="mc-torch-glow"/>
        </g>
        <g transform="translate(912 364)"><path fill="#68462c" d="M0 0h170v48H0z"/><path stroke="#d3b550" stroke-width="6" d="M8 8v27m15-27v27m15-27v27m15-27v27m50-27v27m15-27v27m15-27v27m15-27v27m15-27v27"/><rect x="68" y="0" width="23" height="48" fill="#4d95bc"/></g>
        <g transform="translate(54 379)"><path fill="#7caa86" d="M0 10h160v36H0z"/><path fill="#65afc6" d="M12 14h133v22H12z"/><path fill="#a4d7dc" d="M24 18h35v4H24zm74 9h34v3H98z"/><rect x="87" y="12" width="16" height="6" fill="#568345"/></g>
        <g stroke="#816647" stroke-width="5" fill="none"><path d="M874 398h27m-24-12v29m21-29v29M1065 421h86m-77-13v24m27-24v24m29-24v24"/></g>
        <g v-for="i in 13" :key="i" :transform="`translate(${i * 87} ${420 - (i % 3) * 8})`"><path fill="#416e2e" d="M0 0h3v14H0z"/><path :fill="i % 2 ? '#edce56' : '#e9e3dc'" d="M-3-3h9v7h-9z"/></g>
      </svg>
      <div class="mc-world-copy"><p class="eyebrow">STUDYLOOM / SURVIVAL OF THE FOCUSED</p><h1 id="room-title">{{ roomName }}</h1><p>不用一次建好整个世界。<br/>今天，先放下属于你的那一块。</p><span class="mc-splash">每一分钟都是经验值！</span></div>
      <div class="mc-debug">{{ biomes[biome] }} · {{ night || focusing ? '月光下的村庄' : '晴朗' }}</div>
      <div class="mc-village-sign">自习村庄 · 图书馆庭院<small>沿着小径，找到属于你的安静角落</small></div>
      <button class="mc-secret" aria-label="查看树后的苦力怕" @click="meet('creeper')"><MinecraftMob kind="creeper" label="苦力怕"/></button>
      <button class="mc-villager" aria-label="与图书管理员交谈" @click="meet('villager')"><MinecraftMob label="图书管理员"/><span>图书管理员</span></button>
      <div class="mc-crosshair" aria-hidden="true">+</div>
      <div class="mc-hud">
        <div class="mc-vitals" aria-label="装饰性生存状态"><span class="mc-hearts">♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥</span><span class="mc-hunger">◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆</span></div>
        <div class="mc-level">{{ level }}<small>级 · 集体专注</small></div><div class="mc-hud-xp" role="progressbar" aria-label="下一级集体专注经验" :aria-valuenow="minutes % 60" :aria-valuemin="0" :aria-valuemax="60"><span :style="{ width: `${minutes % 60 / 60 * 100}%` }"/></div>
        <div class="mc-hotbar" role="group" aria-label="九格快捷栏，支持数字键1到9"><button v-for="(tool, index) in tools" :key="tool.item" :class="{ selected: selected === index }" :aria-pressed="selected === index" :aria-label="`${index + 1} · ${tool.label}`" :title="`${index + 1} · ${tool.label}`" @click="useSlot(index)"><MinecraftItem :name="tool.item"/><small>{{ index + 1 }}</small></button></div>
        <p class="mc-tool-caption">{{ tools[selected]?.label }} <span>· 点击物品 / 数字键 1–9</span></p>
      </div>
    </div>
    <div class="mc-world-bottom"><span><i class="status-dot"/> {{ activeCount }} 位玩家正在建造</span><span>主世界 · 自习村庄 <b>●</b></span></div>
    <div class="mc-dialogue" aria-live="polite"><MinecraftMob :kind="visitor"/><div><strong>{{ { villager: '图书管理员', golem: '铁傀儡', bee: '蜜蜂', creeper: '秘密访客 · 苦力怕' }[visitor] }}<small>村庄手记 · {{ discoveries.length }} / 4 位访客</small></strong><p>{{ dialogue }}</p></div></div>
  </section>
</template>
