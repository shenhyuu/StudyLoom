<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import MinecraftItem from './MinecraftItem.vue'
const props = defineProps<{ minutes: number }>()
// Names and game requirements from zh.minecraft.wiki/w/成就 (Bedrock achievements).
// Time thresholds and ordering are StudyLoom adaptations, not game achievement requirements.
const achievements = [
  { name:'制作工作台', icon:'crafting_table', minutes:120, requirement:'用四块木板合成工作台' },
  { name:'采矿时间到！', icon:'wooden_pickaxe', minutes:300, requirement:'制作并取得一把镐' },
  { name:'“热”门话题', icon:'furnace', minutes:480, requirement:'用八块圆石合成熔炉' },
  { name:'获得升级', icon:'stone_pickaxe', minutes:660, requirement:'制作木镐之外的镐' },
  { name:'来硬的', icon:'iron_ingot', minutes:840, requirement:'从熔炉或高炉中取得铁锭' },
  { name:'烤面包', icon:'bread', minutes:1020, requirement:'用小麦合成并取得面包' },
  { name:'钻石！', icon:'diamond', minutes:1200, requirement:'捡起一颗钻石' },
  { name:'图书管理员', icon:'bookshelf', minutes:1500, requirement:'合成并取得书架' },
  { name:'附魔师', icon:'enchanting_table', minutes:2100, requirement:'合成并取得附魔台' },
  { name:'结束了？', icon:'ender_eye', minutes:2700, requirement:'进入末地传送门' },
  { name:'开始了。', icon:'nether_star', minutes:3600, requirement:'击败凋灵并在附近见证它死亡' },
] as const
const nextIndex = computed(()=>achievements.findIndex(a=>props.minutes<a.minutes))
const next = computed(()=>nextIndex.value<0 ? null : achievements[nextIndex.value]!)
const progress = computed(()=>{
  if (!next.value) return 100
  const from=achievements[nextIndex.value-1]?.minutes ?? 0
  return Math.max(0,Math.min(100,(props.minutes-from)/(next.value.minutes-from)*100))
})
const remaining = computed(()=>Math.max(0,(next.value?.minutes ?? props.minutes)-props.minutes))
const track = ref<HTMLElement|null>(null)
watch(nextIndex,async()=>{
  await nextTick()
  const current=track.value?.querySelector<HTMLElement>('.current, .latest')
  if(current && track.value) track.value.scrollTo({left:current.offsetLeft-(track.value.clientWidth-current.offsetWidth)/2,behavior:'smooth'})
},{immediate:true,flush:'post'})
</script>

<template>
  <div class="mc-achievement-progress">
    <div class="milestone-label"><span>下一项成就 · {{ next?.name || '全部达成' }}</span><b>{{ Math.round(progress) }}%</b></div>
    <div class="xp-bar" role="progressbar" aria-label="下一项成就的集体专注进度" :aria-valuenow="Math.round(progress)" :aria-valuemin="0" :aria-valuemax="100"><span :style="{width:progress+'%'}"/></div>
    <p class="milestone-note" v-if="next">再一起专注 <b>{{ Math.floor(remaining/60) }} 小时 {{ remaining%60 }} 分</b>，解锁「{{ next.name }}」。</p><p class="milestone-note" v-else>全部成就已点亮，继续一起让主世界生长。</p>
    <div ref="track" class="mc-achievement-track" aria-label="主世界成就里程碑，可横向滚动">
      <article v-for="(achievement,index) in achievements" :key="achievement.name" class="mc-achievement-card" :class="{unlocked:minutes>=achievement.minutes,current:index===nextIndex,latest:index===(nextIndex<0?achievements.length-1:nextIndex-1)}" :style="{'--achievement-progress':progress+'%'}">
        <span class="mc-achievement-frame"><MinecraftItem :name="achievement.icon" :label="achievement.name"/></span><b>{{ achievement.name }}</b><small>{{ achievement.minutes/60 }} 小时</small><p>{{ achievement.requirement }}</p><span class="mc-achievement-state">{{ minutes>=achievement.minutes?'✓ 已达成':index===nextIndex?'正在解锁':'尚未解锁' }}</span>
      </article>
    </div>
    <p class="mc-achievement-reference"><a href="https://zh.minecraft.wiki/w/成就" target="_blank" rel="noreferrer">Minecraft Wiki · 基岩版成就 ↗</a><small>名称与图示条件参考游戏；时长解锁与排列为本站的集体专注改编。</small></p>
  </div>
</template>
