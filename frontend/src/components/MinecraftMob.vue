<script setup lang="ts">
withDefaults(defineProps<{ kind?: 'villager' | 'creeper' | 'golem' | 'bee'; label?: string }>(), { kind: 'villager' })
</script>

<template>
  <svg class="mc-mob" viewBox="0 0 24 36" shape-rendering="crispEdges" role="img" :aria-label="label || kind">
    <template v-if="kind === 'villager'">
      <path fill="#543729" d="M5 1h14v13H5zM4 15h16v15H4zM5 30h6v6H5zm8 0h6v6h-6z"/>
      <path fill="#ba906d" d="M6 2h12v11H6zM3 19h18v5H3z"/><path fill="#e1b68a" d="M7 2h10v5H7z"/>
      <path fill="#e4dbbb" d="M4 15h16v4H4zM5 24h14v6H5z"/><path fill="#a22e32" d="M4 14h5v16H4zm11 0h5v16h-5zM5 1h14v3H5z"/>
      <path fill="#343329" d="M6 7h5v3H6zm7 0h5v3h-5z"/><path fill="#72a75c" d="M8 8h2v2H8zm6 0h2v2h-2z"/>
      <path fill="#98704e" d="M10 9h4v7h-4z"/><path fill="#d2a17b" d="M10 9h3v5h-3z"/>
    </template>
    <template v-else-if="kind === 'creeper'">
      <path fill="#3c7937" d="M4 3h16v14H4zM7 17h10v13H7zM3 29h8v7H3zm10 0h8v7h-8z"/><path fill="#79b851" d="M4 3h12v4H4zM5 7h5v7H5zm7 11h5v8h-5zM3 29h5v4H3zm13 1h5v4h-5z"/><path fill="#a1cb70" d="M17 4h3v5h-3zM5 14h5v3H5zM8 20h3v4H8z"/><path fill="#192619" d="M6 8h4v4H6zm8 0h4v4h-4zM10 11h4v3h-4zM8 14h8v3h-8zM8 17h3v2H8zm5 0h3v2h-3z"/>
    </template>
    <template v-else-if="kind === 'golem'">
      <path fill="#c8c7b3" d="M8 0h9v10H8zM5 11h15v15H5zM0 12h5v17H0zm20 0h4v17h-4zM5 26h6v10H5zm9 0h6v10h-6z"/><path fill="#ece5d3" d="M8 0h7v5H8zM6 11h12v8H6zM0 12h3v12H0z"/><path fill="#768551" d="M6 12h2v7H6zM8 18h3v3H8zM16 22h3v4h-3z"/><path fill="#923c35" d="M9 5h2v2H9zm5 0h2v2h-2z"/><path fill="#a5a28c" d="M11 7h3v5h-3z"/>
    </template>
    <template v-else>
      <path fill="#d8eaf4" opacity=".8" d="M2 7h8v8H2zm13-2h7v10h-7z"/><path fill="#e5b940" d="M3 15h18v12H3z"/><path fill="#593c28" d="M8 15h3v12H8zm7 0h3v12h-3zM4 27h2v4H4zm9 0h2v4h-2z"/><path fill="#242329" d="M3 18h2v3H3zm4 0h2v3H7z"/>
    </template>
  </svg>
</template>
