<script setup lang="ts">
withDefaults(defineProps<{ kind?: 'villager' | 'creeper' | 'golem' | 'bee'; label?: string }>(), { kind: 'villager' })
</script>

<template>
  <img v-if="kind === 'villager' || kind === 'creeper'" class="mc-mob" :src="`/minecraft/${kind === 'villager' ? 'librarian.png' : 'creeper.webp'}`" :alt="label || (kind === 'villager' ? '图书管理员' : '苦力怕')"/>
  <svg v-else class="mc-mob" viewBox="0 0 24 36" shape-rendering="crispEdges" role="img" :aria-label="label || kind">
    <template v-if="kind === 'golem'">
      <path fill="#c8c7b3" d="M8 0h9v10H8zM5 11h15v15H5zM0 12h5v17H0zm20 0h4v17h-4zM5 26h6v10H5zm9 0h6v10h-6z"/><path fill="#ece5d3" d="M8 0h7v5H8zM6 11h12v8H6zM0 12h3v12H0z"/><path fill="#768551" d="M6 12h2v7H6zM8 18h3v3H8zM16 22h3v4h-3z"/><path fill="#923c35" d="M9 5h2v2H9zm5 0h2v2h-2z"/><path fill="#a5a28c" d="M11 7h3v5h-3z"/>
    </template>
    <template v-else>
      <path fill="#d8eaf4" opacity=".8" d="M2 7h8v8H2zm13-2h7v10h-7z"/><path fill="#e5b940" d="M3 15h18v12H3z"/><path fill="#593c28" d="M8 15h3v12H8zm7 0h3v12h-3zM4 27h2v4H4zm9 0h2v4h-2z"/><path fill="#242329" d="M3 18h2v3H3zm4 0h2v3H7z"/>
    </template>
  </svg>
</template>
