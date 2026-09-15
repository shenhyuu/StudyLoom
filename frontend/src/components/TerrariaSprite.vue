<script setup lang="ts">
defineProps<{ name: string; label?: string }>()
</script>

<template>
  <img class="terraria-sprite" :src="`/terraria/${name}.png`" :alt="label || ''" draggable="false" />
</template>

<style>
.terraria-sprite { width: 28px; height: 28px; object-fit: contain; image-rendering: pixelated; flex-shrink: 0; vertical-align: middle; }
</style>
