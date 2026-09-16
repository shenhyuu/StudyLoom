<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import TerrariaLandscape from './TerrariaLandscape.vue'
import TerrariaSprite from './TerrariaSprite.vue'

defineProps<{ roomName: string; focusing: boolean; activeCount: number }>()
const biome = ref<'forest' | 'mushroom' | 'hallow'>('forest')
const night = ref(true)
const npc = ref<'Guide' | 'Merchant' | 'Dryad'>('Guide')
const tipIndex = ref(0)
const collected = ref<string[]>([])
const announcement = ref('')
const biomes = [
  { id: 'forest' as const, name: '森林', icon: 'Forest_Pylon', caption: 'FOREST', description: '熟悉的起点，总有一盏灯为你亮着。' },
  { id: 'mushroom' as const, name: '发光蘑菇地', icon: 'Mushroom_Pylon', caption: 'GLOWING MUSHROOM', description: '在幽蓝的菌盖下，让思绪悄悄发光。' },
  { id: 'hallow' as const, name: '神圣之地', icon: 'Hallow_Pylon', caption: 'THE HALLOW', description: '越过彩色的树梢，寻找下一份灵感。' },
]
const place = computed(() => biomes.find(item => item.id === biome.value)!)
const residents = [ { id: 'Guide' as const, name: '向导', role: '你的第一位朋友' }, { id: 'Merchant' as const, name: '商人', role: '把时光装进行囊' }, { id: 'Dryad' as const, name: '树妖', role: '听见世界在生长' } ]
const resident = computed(() => residents.find(item => item.id === npc.value)!)
// Original study-room dialogue inspired by the NPC roles, not quotes from the game.
const tips = {
  Guide: ['一张工作台，一把铜镐，一段属于你的时间。准备好了，就在篝火旁开始今天的探索吧。', '房子需要光源、桌椅和背景墙。你的计划也一样：拆成小块，一步一步把它搭起来。', '夜空偶尔会送来一颗坠落之星。看看营地右侧，也许今天的好运就在那儿。'],
  Merchant: ['铜币、银币、金币……时间可比这些珍贵。今天积攒的每一分钟，都会留在你们共同的世界里。', '收纳行囊，也整理思绪。到留言簿记下一个小目标，再带着轻装出发。', '最好的补给？一杯水、一次伸展，还有休息之后重新出发的你。'],
  Dryad: ['森林在生长，你也是。别急着追赶别人的进度，照顾好自己的那一小片绿意。', '试试晶塔旁的目的地。发光蘑菇地的幽蓝、神圣之地的粉紫，总有一种风景适合此刻的心情。', '篝火给冒险者温暖，伙伴让旅途不再孤单。今天，也一起守护这个小小的世界吧。'],
}
const hotbar = [
  { icon: 'Copper_Shortsword', label: '自习世界', target: '#home' },
  { icon: 'Copper_Pickaxe', label: '开始专注 · 工作台', target: '#focus-title' },
  { icon: 'Copper_Axe', label: '共同建造', target: '#progress-title' },
  { icon: 'Torch', label: '同行伙伴', target: '#companions' },
  { icon: 'Work_Bench', label: '营地留言簿', target: '#journal' },
  { icon: 'Music_Box', label: '音乐盒 · 房间曲目', target: '#radio' },
]
function useHotbar(event: KeyboardEvent) {
  const target = event.target
  if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || event.repeat) return
  if (target instanceof HTMLElement && (target.isContentEditable || target.closest('input, textarea, select'))) return
  const index = Number(event.key) - 1
  if (!/^[1-6]$/.test(event.key)) return
  const shortcut = document.querySelectorAll<HTMLAnchorElement>('.tr-hotbar > a')[index]
  if (shortcut) { event.preventDefault(); shortcut.focus(); shortcut.click() }
}
onMounted(() => window.addEventListener('keydown', useHotbar))
onBeforeUnmount(() => window.removeEventListener('keydown', useHotbar))
function travel(next: typeof biome.value) { biome.value = next; announcement.value = `已抵达${place.value.name}` }
function collectStar() {
  if (collected.value.includes(biome.value)) return
  collected.value.push(biome.value)
  announcement.value = collected.value.length === 3 ? '星光收藏完成！三片风景，三份小小的好运。' : `获得坠落之星！已收藏 ${collected.value.length} / 3，去其他生态找找吧。`
}
</script>

<template>
  <section class="tr-world" aria-labelledby="room-title">
    <div class="tr-stage">
      <TerrariaLandscape :biome="biome" :night="night" :focusing="focusing"/>
      <div class="tr-hud">
        <div class="tr-inventory"><span class="tr-inventory-label">物品栏 <small>选择你的下一步</small></span><nav class="tr-hotbar" aria-label="物品栏快捷导航"><a v-for="(item, index) in hotbar" :key="item.icon" :href="item.target" :aria-label="item.label" :aria-keyshortcuts="String(index + 1)" :data-tip="item.label + ' · ' + (index + 1)" :class="{ 'selected-slot': index === 1 && focusing }"><small>{{ index + 1 }}</small><TerrariaSprite :name="item.icon"/></a><span class="tr-star-slot" :aria-label="`已收藏 ${collected.length} 颗坠落之星`"><TerrariaSprite name="Fallen_Star"/><b>{{ collected.length }}</b></span></nav></div>
        <div class="tr-vitals"><span>生命 <span class="tr-life-caption">好好照顾自己</span></span><div aria-label="生命爱心装饰"><TerrariaSprite v-for="n in 5" :key="n" name="Heart"/></div><span class="tr-mana">魔力 <TerrariaSprite v-for="n in 3" :key="n" name="Mana_Star"/></span></div>
      </div>
      <div class="tr-world-copy"><p class="tr-kicker"><i></i> {{ place.caption }} · {{ night ? '星夜' : '白昼' }}</p><h1 id="room-title">{{ roomName }}</h1><p class="tr-room-motto">挖掘一点灵感，<br/>建造一整个世界。</p><p class="tr-world-description">{{ place.description }}</p><a class="tr-join" href="#focus-title"><TerrariaSprite name="Campfire"/>去篝火旁坐坐 <span>→</span></a></div>
      <button class="tr-time-toggle" @click="night = !night" :aria-label="night ? '切换白昼场景' : '切换星夜场景'"><span>{{ night ? '☾' : '☀' }}</span>{{ night ? '星夜' : '白昼' }} <small>切换</small></button>
      <div class="tr-house-label">⌂ 城镇环境 <span>适合居住</span></div>
      <button v-if="night && !collected.includes(biome)" class="tr-fallen-star" aria-label="拾取坠落之星" title="坠落之星 · 点击拾取" @click="collectStar"><TerrariaSprite name="Fallen_Star"/></button>
      <div class="tr-scene-bottom"><span><i class="status-dot"></i>{{ activeCount }} 位冒险者正在专注</span><span><TerrariaSprite name="Campfire"/>{{ focusing ? '温暖篝火 · 专注进行中' : '温暖篝火 · 等你入座' }}</span></div>
    </div>
    <div class="tr-travel"><span class="tr-travel-label"><TerrariaSprite :name="place.icon"/>晶塔旅行 <small>换一片风景</small></span><div role="group" aria-label="切换生态场景"><button v-for="destination in biomes" :key="destination.id" :class="{ active: biome === destination.id }" :aria-pressed="biome === destination.id" @click="travel(destination.id)"><TerrariaSprite :name="destination.icon"/>{{ destination.name }}<span v-if="collected.includes(destination.id)" class="tr-collected" aria-label="已找到星星">✦</span></button></div></div>
    <p class="tr-announcement" role="status" aria-live="polite">{{ announcement }}</p>
  </section>
  <section class="tr-npc-dialog" aria-label="城镇 NPC 对话">
    <div class="tr-npc-tabs" role="group" aria-label="选择对话居民"><button v-for="character in residents" :key="character.id" :aria-pressed="npc === character.id" :class="{ active: npc === character.id }" @click="npc = character.id; tipIndex = 0"><TerrariaSprite :name="character.id"/><span>{{ character.name }}</span></button></div>
    <div class="tr-dialog-content"><div class="tr-npc-name"><strong>{{ resident.name }}</strong><span>{{ resident.role }}</span></div><p>{{ tips[npc][tipIndex] }}</p></div>
    <button class="tr-next-tip" @click="tipIndex = (tipIndex + 1) % tips[npc].length">再聊一句 <span>›</span></button>
  </section>
</template>
