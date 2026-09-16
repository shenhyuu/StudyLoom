<script setup lang="ts">
import { computed } from 'vue'
import MinecraftItem from './MinecraftItem.vue'
const props = defineProps<{ recipeIndex: number; focusing: boolean }>()
// Row-major 3×3 grids. Empty cells are intentionally empty; each occupied cell is one ingredient.
const recipes = [
  { name: '工作台', output: 'crafting_table', count: 1, materials: '4 块橡木木板', grid: ['oak_planks','oak_planks','','oak_planks','oak_planks','','','',''], wiki: '工作台' },
  { name: '木棍', output: 'stick', count: 4, materials: '2 块橡木木板', grid: ['','oak_planks','','','oak_planks','','','',''], wiki: '木棍' },
  { name: '木镐', output: 'wooden_pickaxe', count: 1, materials: '3 块橡木木板 + 2 根木棍', grid: ['oak_planks','oak_planks','oak_planks','','stick','','','stick',''], wiki: '镐' },
  { name: '石镐', output: 'stone_pickaxe', count: 1, materials: '3 块圆石 + 2 根木棍', grid: ['cobblestone','cobblestone','cobblestone','','stick','','','stick',''], wiki: '镐' },
  { name: '熔炉', output: 'furnace', count: 1, materials: '8 块圆石', grid: ['cobblestone','cobblestone','cobblestone','cobblestone','','cobblestone','cobblestone','cobblestone','cobblestone'], wiki: '熔炉' },
  { name: '火把', output: 'torch', count: 4, materials: '1 个煤炭 + 1 根木棍', grid: ['','coal','','','stick','','','',''], wiki: '火把' },
  { name: '面包', output: 'bread', count: 1, materials: '3 个小麦', grid: ['','','','wheat','wheat','wheat','','',''], wiki: '面包' },
  { name: '铁镐', output: 'iron_pickaxe', count: 1, materials: '3 块铁锭 + 2 根木棍', grid: ['iron_ingot','iron_ingot','iron_ingot','','stick','','','stick',''], wiki: '镐' },
  { name: '书', output: 'book', count: 1, materials: '3 张纸 + 1 个皮革 · 无序配方', grid: ['paper','paper','','paper','leather','','','',''], wiki: '书' },
  { name: '书架', output: 'bookshelf', count: 1, materials: '6 块橡木木板 + 3 本书', grid: ['oak_planks','oak_planks','oak_planks','book','book','book','oak_planks','oak_planks','oak_planks'], wiki: '书架' },
  { name: '钓鱼竿', output: 'fishing_rod', count: 1, materials: '3 根木棍 + 2 根线', grid: ['','','stick','','stick','string','stick','','string'], wiki: '钓鱼竿' },
  { name: '弓', output: 'bow', count: 1, materials: '3 根木棍 + 3 根线', grid: ['','stick','string','stick','','string','','stick','string'], wiki: '弓' },
  { name: '钻石镐', output: 'diamond_pickaxe', count: 1, materials: '3 颗钻石 + 2 根木棍', grid: ['diamond','diamond','diamond','','stick','','','stick',''], wiki: '镐' },
] as const
const recipe = computed(() => recipes[props.recipeIndex % recipes.length]!)
const labels: Record<string,string> = { oak_planks:'橡木木板', cobblestone:'圆石', stick:'木棍', coal:'煤炭', wheat:'小麦', iron_ingot:'铁锭', paper:'纸', leather:'皮革', book:'书', string:'线', diamond:'钻石' }
</script>

<template>
  <div class="mc-recipe">
    <div class="mc-recipe-heading"><span>{{ focusing ? '正在制作' : '本次制作' }}</span><strong>{{ recipe.name }}</strong><small>第 {{ recipeIndex + 1 }} 次建造</small></div>
    <div class="mc-crafting" :aria-label="`${recipe.name}的真实游戏合成配方：${recipe.materials}，产出${recipe.count}个`">
      <div class="mc-crafting-grid"><span v-for="(ingredient,index) in recipe.grid" :key="index" class="mc-slot" :title="labels[ingredient] || '空格'"><MinecraftItem v-if="ingredient" :name="ingredient" :label="labels[ingredient]"/></span></div>
      <span class="mc-crafting-arrow" aria-hidden="true">➜</span><span class="mc-slot mc-crafting-output"><MinecraftItem :name="recipe.output" :label="recipe.name"/><b class="mc-stack-count">{{ recipe.count }}</b></span>
    </div>
    <p class="mc-recipe-materials">{{ recipe.materials }}</p>
    <a :href="`https://zh.minecraft.wiki/w/${encodeURIComponent(recipe.wiki)}`" target="_blank" rel="noreferrer">查看 Wiki 配方 ↗</a>
    <small class="mc-recipe-hint">保存本次专注后，下次制作新物品 · 13 种配方依次轮换</small>
  </div>
</template>
