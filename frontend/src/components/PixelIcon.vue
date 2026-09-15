<script setup lang="ts">
defineProps<{ kind: string }>()
</script>
<template>
  <svg class="pixel-icon" viewBox="0 0 16 16" fill="none" shape-rendering="crispEdges" aria-hidden="true">
    <g v-if="kind === 'grass'"><path fill="#483125" d="M1 5h14v10H1z"/><path fill="#8a6040" d="M2 6h12v8H2z"/><path fill="#79bd45" d="M1 2h14v5h-3v2H9V7H6v2H3V7H1z"/><path fill="#b2d775" d="M2 2h12v2H2z"/><path fill="#af8050" d="M3 10h3v2H3zm6 2h3v2H9z"/></g>
    <g v-else-if="kind === 'tree'"><path fill="#94613f" d="M7 6h3v9H5v-2h2z"/><path fill="#315d37" d="M3 2h9v2h3v5h-3v2H3V9H1V4h2z"/><path fill="#73b856" d="M4 1h7v2h2v4H9v2H3V4h1z"/><path fill="#a6d475" d="M4 2h5v2H4z"/></g>
    <g v-else-if="kind === 'pickaxe'"><path fill="#503b2c" d="m2 13 9-9 2 2-9 9H2z"/><path fill="#b68a50" d="m3 12 8-8 1 1-8 8H3z"/><path fill="#284645" d="M5 1h7v2h2v2h1v6h-3V6h-2V4H5z"/><path fill="#71ded3" d="M5 1h6v2h2v2h1v4h-1V5h-3V3H5z"/></g>
    <g v-else-if="kind === 'book'"><path fill="#413524" d="M1 3h6l1 1 1-1h6v11H9l-1 1-1-1H1z"/><path fill="#f1deb0" d="M2 2h5v10H2zm7 0h5v10H9z"/><path fill="#b99a62" d="M3 5h3v1H3zm0 3h3v1H3zm7-3h3v1h-3zm0 3h3v1h-3z"/></g>
    <g v-else-if="kind === 'chest'"><path fill="#392923" d="M1 3h14v12H1z"/><path fill="#ad743d" d="M2 4h12v9H2z"/><path fill="#e1b15e" d="M2 4h12v2H2z"/><path fill="#523927" d="M2 8h12v2H2z"/><path fill="#ffe18b" d="M7 7h3v4H7z"/></g>
    <g v-else-if="kind === 'music'"><path fill="#483127" d="M1 2h14v13H1z"/><path fill="#986447" d="M2 3h12v11H2z"/><path fill="#c99561" d="M3 4h10v2H3z"/><path fill="#302c31" d="M5 7h6v6H5z"/><path fill="#adce6a" d="M7 9h2v2H7z"/></g>
    <g v-else-if="kind === 'fire'"><path fill="#714830" d="M2 13h12v2H2z"/><path fill="#d9793f" d="M4 6h2V3h2V1h2v5h2v3h1v3H3V8h1z"/><path fill="#ffd46e" d="M6 7h2V5h1v4h2v3H5V9h1z"/><path fill="#fff0ba" d="M7 9h2v3H7z"/></g>
    <g v-else-if="kind === 'torch'"><path fill="#4e3119" d="M6 9h4v6H6z"/><path fill="#7d5230" d="M7 9h2v6H7z"/><path fill="#e8542a" d="M5 1h6v2h2v4h-2v2H5V7H3V3h2z"/><path fill="#ffb43a" d="M6 2h4v1h2v3H6z"/><path fill="#fff3b0" d="M7 4h2v3H7z"/></g>
    <g v-else-if="kind === 'coin'"><path fill="#7a5a1c" d="M5 1h6v2h2v2h2v6h-2v2h-2v2H5v-2H3v-2H1V5h2V3h2z"/><path fill="#d9a43c" d="M5 2h6v1h2v2h2v6h-2v2h-2v1H5v-1H3v-2H1V5h2V3h2z"/><path fill="#ffe08a" d="M5 3h6v1h2v4H3V5h1z"/><path fill="#fff3c4" d="M4 4h3v2H4z"/></g>
    <g v-else-if="kind === 'life'"><path fill="#3d0d0c" d="M2 2h4v2h4V2h4v3h1v5h-2v2h-2v2h-2v2H7v-2H5v-2H3v-2H1V5h1z"/><path fill="#cf2b22" d="M2 3h4v2h4V3h4v2v4h-1v2h-2v2h-2v2H7v-2H5v-2H3V9H2z"/><path fill="#f2624f" d="M3 4h3v2h2v1h2V6h1V4h1v4h-1v2h-2v2H8v1H7v-1H5V9H3z"/><path fill="#ffd9cd" d="M4 5h2v2H4z"/></g>
    <g v-else-if="kind === 'star'"><path fill="#8e633b" d="M6 1h4v4h5v5h-3v4H9v-2H7v2H3v-4H1V5h5z"/><path fill="#f4cf66" d="M7 2h2v4h5v2h-3v5H9v-3H7v3H5V8H2V6h5z"/><path fill="#fff1ae" d="M7 4h2v4H5V6h2z"/></g>
    <g v-else><path fill="#442f29" d="M2 2h5v2h2V2h5v2h1v5h-2v2h-2v2H9v2H7v-2H5v-2H3V9H1V4h1z"/><path fill="#e77969" d="M3 3h3v2h4V3h3v5h-2v2H9v2H7v-2H5V8H3z"/><path fill="#ffb6a0" d="M3 3h3v2H3z"/></g>
  </svg>
</template>
