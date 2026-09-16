<script setup lang="ts">
defineProps<{ name: string; label?: string }>()
</script>
<template><img class="mc-item" :src="`/minecraft/${name}.png`" :alt="label || ''" width="32" height="32" /></template>
