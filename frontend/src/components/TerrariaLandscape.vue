<script setup lang="ts">
defineProps<{ biome: 'forest' | 'mushroom' | 'hallow'; night: boolean; focusing: boolean }>()
const trees = [{ x: 34, y: 194, s: 1.15 }, { x: 179, y: 214, s: .9 }, { x: 477, y: 191, s: 1.17 }, { x: 1017, y: 171, s: 1.36 }, { x: 1140, y: 227, s: .78 }]
</script>

<template>
  <svg class="terraria-landscape" :class="[biome, { night, lit: focusing }]" viewBox="0 0 1200 440" preserveAspectRatio="xMidYMax slice" shape-rendering="crispEdges" role="img" :aria-label="`${biome === 'forest' ? '森林' : biome === 'mushroom' ? '发光蘑菇地' : '神圣之地'}中的双层木屋、篝火和城镇居民`">
    <defs>
      <linearGradient id="tr-sky" x2="0" y2="1"><stop stop-color="var(--sky-top)"/><stop offset="1" stop-color="var(--sky-bottom)"/></linearGradient>
      <pattern id="tr-earth" width="24" height="24" patternUnits="userSpaceOnUse"><rect width="24" height="24" fill="#604535"/><path d="M0 0h8v4H0zm12 8h8v5h-8zM2 17h6v4H2zm17 4h7v3h-7z" fill="#473529"/><path d="M2 3h4v2H2zm11 5h6v2h-6zM3 17h4v2H3z" fill="#946143"/><path d="M20 2h3v3h-3zM10 19h3v3h-3z" fill="#776151"/></pattern>
      <pattern id="tr-wall" width="26" height="18" patternUnits="userSpaceOnUse"><rect width="26" height="18" fill="#775033"/><path d="M0 0h26M0 17h26" stroke="#402c24" stroke-width="2"/><path d="M2 4h14m-6 8h14" stroke="#946445" stroke-width="2"/></pattern>
      <pattern id="tr-roof" width="20" height="10" patternUnits="userSpaceOnUse"><rect width="20" height="10" fill="#774335"/><path d="M0 9h20M10 0v9" stroke="#492d2b" stroke-width="2"/><path d="M1 1h18" stroke="#a86646" stroke-width="2"/></pattern>
      <radialGradient id="tr-glow"><stop stop-color="#ffcf66" stop-opacity=".5"/><stop offset="1" stop-color="#ffad4c" stop-opacity="0"/></radialGradient>
      <g id="tr-tree"><path d="M-6 20h15v122h9v6H-15v-7h9zM-6 54h-15V35h-5v24h20M7 80h20V54h-5v20H7" fill="#382b28"/><path d="M-3 5h8v137h-8z" fill="#846044"/><path d="M1 24h3v41H1zm-3 58h3v31h-3z" fill="#b18758"/><path d="M-58-13h10v-17h23v-12H5v-6h22v17h23v15h16V9H52v14H30v12H5v-9h-30v-8h-29V6h-12v-19z" fill="var(--leaf-dark)"/><path d="M-53-15h12v-13h21v-9H8v-6h16v18h21v12h15V4H39v14H17V9H-5v9h-20V6h-28z" fill="var(--leaf)"/><path d="M-36-23h21v-8H7v-7h14v12h14v10H16v9H-9v-8h-27zM-48-9h17V0h-17zM29 2h18v6H29z" fill="var(--leaf-light)"/><path d="M-30-18h9v3h-9zM-7-29h13v3H-7zM18-16h10v4H18zM-6 4h10v3H-6z" fill="#e0f5ad" opacity=".3"/></g>
      <g id="tr-mushroom"><path d="M-6-2h13v143H-6z" fill="#6875b0"/><path d="M-2 4h5v137h-5z" fill="#b4b7df"/><path d="M-57-4v-17h13v-17h22v-10h39v10h23v15h15V-4z" fill="#153c8a"/><path d="M-52-9v-12h13v-14h21v-9h32v11h22v14h14v10z" fill="#347ad5"/><path d="M-52-9H50v8H-52z" fill="#81d6fb"/><path d="M-25-34h12v9h-12zM7-30h16v11H7zM-39-16h8v6h-8zM30-13h10v6H30z" fill="#b0e8ff"/></g>
    </defs>
    <path fill="url(#tr-sky)" d="M0 0h1200v440H0z"/>
    <g v-if="night || biome === 'mushroom'" fill="#def0ff"><rect v-for="n in 65" :key="n" :x="(n * 137) % 1200" :y="(n * 53) % 225 + 12" :width="n % 4 === 0 ? 3 : 2" height="2" :opacity=".25 + (n % 4) * .2"/></g>
    <g v-if="night" transform="translate(951 87)"><path d="M-17-24h30v7h10v28H13v10h-30V11h-9v-28h9z" fill="#d8e4c5"/><path d="M-13-15h9v9h-9zM2 5h12v10H2zM9-16h8v7H9z" fill="#afc1b6"/></g>
    <g v-else-if="biome !== 'mushroom'"><circle cx="954" cy="89" r="38" fill="#ffe6a5" opacity=".12"/><path d="M934 66h36v8h8v32h-8v8h-36v-8h-8V74h8z" fill="#ffe6a5"/></g>
    <g fill="#c0d5ed" :opacity="night ? .07 : .22"><path d="M50 96h31V84h46V74h45v12h40v13h34v10H50zM439 56h29V42h72v12h43v14H439zM1000 146h30v-14h40v-12h55v16h34v12h41v14h-200z"/></g>
    <path d="M0 264l72-48 46 23 91-113 75 74 58-26 96 98 76-83 66 34 92-115 103 96 64-49 92 109 78-65 76 62 75-42 40 46v175H0z" fill="var(--mountain-back)"/>
    <path d="M0 299l94-40 45 29 73-52 76 63 78-78 91 56 63-39 77 62 105-87 111 63 61-31 79 58 65-83 63 55 72-21v185H0z" fill="var(--mountain-front)"/>
    <g fill="var(--distant-tree)" opacity=".8"><path v-for="n in 28" :key="n" :transform="`translate(${n * 47 - 40} ${242 + (n % 4) * 13})`" d="M-3 0h6v104h-6zM0-49l-21 44h12l-20 25h18l-20 28h62L12 20h16L9-5h12z"/></g>
    <g v-for="tree in trees" :key="tree.x" :transform="`translate(${tree.x} ${tree.y}) scale(${tree.s})`"><use :href="biome === 'mushroom' ? '#tr-mushroom' : '#tr-tree'"/></g>
    <path d="M0 363h137v-8h153v8h191v-8h377v8h148v-6h194v83H0z" fill="url(#tr-earth)"/>
    <path d="M0 359h137v-8h153v8h191v-8h377v8h148v-6h194v8h-194v7H858v-8H481v8H290v-8H137v8H0z" fill="var(--grass-dark)"/>
    <path d="M0 356h137v-8h153v8h191v-8h377v8h148v-6h194v5h-194v7H858v-8H481v8H290v-8H137v8H0z" fill="var(--grass)"/>
    <g fill="var(--grass)"><path v-for="n in 55" :key="n" :transform="`translate(${n * 23} ${n > 20 && n < 37 ? 348 : 356})`" d="M0 0v-8h2v5h2v-10h2v8h4v-5h2v10z"/></g>
    <!-- A side-on, two-storey starter house: background walls, platforms, furniture and doors. -->
    <path d="M622 211h278v139H622z" fill="url(#tr-wall)"/>
    <path d="M608 213v-8h16v-12h16v-12h16v-12h225v12h17v12h17v12h14v8z" fill="#302527"/>
    <path d="M620 204h16v-12h17v-12h223v12h16v12h23v7H620z" fill="url(#tr-roof)"/>
    <path d="M623 213h7v137h-7zM895 213h7v137h-7zM623 278h279v8H623zM618 347h290v9H618z" fill="#3b2d24"/>
    <path d="M626 216h3v130h-3zM898 216h3v130h-3zM631 279h262v3H631zM619 348h288v3H619z" fill="#cb9257"/>
    <g fill="#1e2d43" stroke="#c99b68" stroke-width="4"><path d="M660 227h36v37h-36zM761 227h36v37h-36zM850 227h26v37h-26zM736 300h38v31h-38z"/></g>
    <path d="M678 228v35m-17-18h34m84-17v35m-17-18h34m67-17v35m-11-18h24m-121 56v29m-18-16h36" stroke="#896440" stroke-width="3"/>
    <g fill="#30221e"><path d="M638 306h26v42h-26zM855 303h26v44h-26z"/></g><path d="M642 308h18v38h-18zM859 307h18v38h-18z" fill="#ad7744"/><path d="M645 312h12v12h-12zm0 17h12v12h-12z" fill="#86522f"/><path d="M655 325h3v3h-3zM871 326h3v3h-3z" fill="#ffd45e"/>
    <path d="M793 328h42v5h-42zM797 333h4v15h-4zM828 333h4v15h-4zM779 320h4v27h-4zM779 336h12v4h-12zM789 340h3v7h-3z" fill="#c48c51"/>
    <path d="M701 316h6v10h-6zM696 326h16v8h-16z" fill="#e45d4e"/><path d="M703 317h2v7h-2z" fill="#fff0c5"/>
    <ellipse cx="722" cy="239" rx="53" ry="50" fill="url(#tr-glow)"/><ellipse cx="829" cy="308" rx="58" ry="54" fill="url(#tr-glow)"/>
    <image href="/terraria/Torch.png" x="716" y="224" width="14" height="30"/><image href="/terraria/Torch.png" x="823" y="294" width="14" height="30"/>
    <image href="/terraria/Work_Bench.png" x="647" y="260" width="40" height="18"/><image href="/terraria/Gold_Chest.png" x="817" y="255" width="32" height="24"/>
    <g class="town-npc npc-guide" aria-label="向导在屋里来回走动"><image href="/terraria/Guide.png" x="692" y="297" width="26" height="52"/></g>
    <g class="town-npc npc-merchant" aria-label="商人在二楼巡视"><image href="/terraria/Merchant.png" x="772" y="229" width="28" height="50"/></g>
    <ellipse cx="553" cy="337" rx="73" ry="59" fill="url(#tr-glow)" class="camp-glow"/><image href="/terraria/Campfire.png" x="533" y="322" width="44" height="28"/>
    <g class="town-npc npc-biome" :aria-label="biome === 'mushroom' ? '松露人在蘑菇地里待机' : '树妖在草地上待机'"><image :href="`/terraria/${biome === 'mushroom' ? 'Truffle' : 'Dryad'}.png`" x="929" y="305" width="29" height="51"/></g>
    <image href="/terraria/Bunny.png" x="421" y="333" width="25" height="24"/>
    <image href="/terraria/Blue_Slime.png" x="1072" y="332" width="32" height="24" class="slime-hop"/>
    <image v-for="n in 7" :key="n" :href="`/terraria/${biome === 'mushroom' ? 'Glowing_Mushroom' : 'Sunflower'}.png`" :x="n < 4 ? n * 37 + 238 : n * 28 + 1000" :y="biome === 'mushroom' ? 336 : 314" width="24" :height="biome === 'mushroom' ? 22 : 44"/>
    <g fill="var(--ore)"><path v-for="n in 12" :key="n" :transform="`translate(${(n * 173) % 1190} ${384 + n % 3 * 15})`" d="M0 0h8v4h5v7H5V7H0z"/></g>
    <g v-if="night || biome === 'mushroom'" class="fireflies" fill="var(--spark)"><rect v-for="n in 16" :key="n" :x="(n * 179) % 1180" :y="260 + n % 5 * 17" width="3" height="3" :style="{ animationDelay: `${n * -.37}s` }"/></g>
  </svg>
</template>

<style>
.terraria-landscape{--sky-top:#344f8d;--sky-bottom:#9ac4ca;--mountain-back:#5778a0;--mountain-front:#446483;--distant-tree:#304b61;--leaf-dark:#214335;--leaf:#397040;--leaf-light:#62994e;--grass:#85b54e;--grass-dark:#3b6632;--ore:#b2936a;--spark:#f9e888;display:block;width:100%;height:440px;background:#172039;image-rendering:pixelated}
.terraria-landscape.night{--sky-top:#101b3a;--sky-bottom:#3f5b83;--mountain-back:#2c405f;--mountain-front:#23394e;--distant-tree:#1b313b;--leaf-dark:#192f2c;--leaf:#2d5137;--leaf-light:#477445}
.terraria-landscape.hallow{--leaf-dark:#554480;--leaf:#a26ab0;--leaf-light:#e39acb;--grass:#58d5d3;--grass-dark:#328eaa;--ore:#a97cec;--spark:#e9c6ff}
.terraria-landscape.mushroom{--sky-top:#0d1338;--sky-bottom:#293965;--mountain-back:#252953;--mountain-front:#1b2248;--distant-tree:#171e3d;--grass:#66b7ef;--grass-dark:#385bad;--ore:#6668b8;--spark:#82dffe}
.town-npc{transform-box:fill-box;transform-origin:center bottom;will-change:transform}.npc-guide{animation:tr-guide-walk 9s steps(8,end) infinite}.npc-merchant{animation:tr-merchant-idle 6.5s steps(2,end) infinite}.npc-biome{animation:tr-biome-idle 4.8s steps(3,end) infinite}.slime-hop{animation:tr-hop 4s steps(3,end) infinite;transform-box:fill-box;transform-origin:bottom}.camp-glow{animation:tr-glow 3s ease-in-out infinite}.lit .camp-glow{opacity:1}.fireflies rect{animation:tr-glow 3.4s ease-in-out infinite alternate}
/* The source sprite faces left: mirror it while moving right, then restore it for the return trip. */
@keyframes tr-guide-walk{0%,10%{transform:translateX(0) scaleX(-1)}42%{transform:translateX(43px) scaleX(-1)}43%,55%{transform:translateX(43px)}88%,100%{transform:translateX(0)}}
@keyframes tr-merchant-idle{0%,42%,100%{transform:translate(0,0)}44%,48%{transform:translate(2px,-2px)}50%,76%{transform:translate(4px,0)}78%,82%{transform:translate(2px,-2px)}}
@keyframes tr-biome-idle{0%,100%{transform:translateY(0) rotate(0)}28%{transform:translateY(-2px) rotate(-1deg)}58%{transform:translateY(0) rotate(0)}78%{transform:translateY(-1px) rotate(1deg)}}
@keyframes tr-hop{0%,75%,100%{transform:translateY(0)}82%{transform:scale(1.12,.8)}90%{transform:translateY(-12px)}}@keyframes tr-glow{0%,100%{opacity:.45}50%{opacity:1}}
@media(prefers-reduced-motion:reduce){.town-npc,.slime-hop,.camp-glow,.fireflies rect{animation:none}}
</style>
