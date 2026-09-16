<script setup lang="ts">
defineProps<{ name: string; label?: string }>()
const inventoryIcons: Record<string, string> = { oak_planks: 'oak_planks_item', cobblestone: 'cobblestone_item', bookshelf: 'bookshelf_item' }
</script>
<template><img class="mc-item" :src="`/minecraft/${inventoryIcons[name] || name}.png`" :alt="label || ''" width="32" height="32" /></template>
