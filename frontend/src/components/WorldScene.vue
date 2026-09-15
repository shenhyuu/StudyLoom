<script setup lang="ts">
defineProps<{ theme: 'minecraft' | 'terraria'; focusing: boolean }>()
</script>
<template>
<svg class="world-scene" viewBox="0 0 960 380" preserveAspectRatio="xMidYMid slice" shape-rendering="crispEdges" role="img" :aria-label="theme === 'minecraft' ? '方块山谷中的自习小屋，草地、橡树和工作台' : '繁星下的森林树屋，篝火与发光蘑菇'">
<defs>
  <pattern id="dirt" width="24" height="24" patternUnits="userSpaceOnUse"><rect width="24" height="24" fill="#70533b"/><path d="M0 3h8v4H0zm13 12h8v5h-8z" fill="#896747"/><path d="M4 17h6v4H4zm14-15h6v5h-6z" fill="#594332"/></pattern>
  <pattern id="planks" width="40" height="16" patternUnits="userSpaceOnUse"><rect width="40" height="16" fill="#ab8152"/><path d="M0 15h40M20 0v15" stroke="#795a3b" stroke-width="2"/><path d="M3 4h12m10 5h10" stroke="#c59a63" stroke-width="2"/></pattern>
  <pattern id="leaves" width="20" height="20" patternUnits="userSpaceOnUse"><rect width="20" height="20" fill="#4e783d"/><path d="M0 0h8v6H0zm10 11h8v6h-8z" fill="#608d43"/><path d="M2 12h5v4H2zm11-10h6v4h-6z" fill="#426536"/></pattern>
  <pattern id="stone" width="30" height="20" patternUnits="userSpaceOnUse"><rect width="30" height="20" fill="#82867a"/><path d="M0 19h30M15 0v19" stroke="#676d65" stroke-width="2"/><path d="M2 3h10m6 0h9" stroke="#a4a69a" stroke-width="2"/></pattern>
</defs>
<template v-if="theme === 'minecraft'">
  <path fill="#a8d3db" d="M0 0h960v380H0z"/><path fill="#c3e1dc" d="M0 122h960v258H0z"/>
  <g fill="#eff1d8"><path d="M46 54h44V42h68v12h54v16H46zm268-19h72V23h46v12h32v15H314zm340 35h48V58h70v12h75v15H654z"/><path d="M853 26h36V16h71v27H853z"/></g>
  <rect x="570" y="40" width="43" height="43" fill="#fff1af"/>
  <path fill="#94b3a0" d="M0 184h48v-35h55v-20h48v-30h61v25h60v39h63v-33h55v-36h55v40h40v35h64v-51h49V93h61v50h65v30h49v-37h65v-33h52v33h70v37h80v207H0z"/>
  <path fill="#72917a" d="M0 211h92v-38h70v27h56v-24h60v43h109v-41h66v34h86v-27h75v-30h49v58h81v-25h88v-32h58v43h70v181H0z"/>
  <path fill="#537859" d="M0 248h134v-19h66v20h109v-18h64v20h181v-20h145v21h128v-26h133v154H0z"/>
  <path fill="url(#dirt)" d="M0 305h165v-12h169v15h322v-20h185v17h119v75H0z"/>
  <path fill="#83a955" d="M0 298h165v-12h169v15h322v-20h185v17h119v12H0z"/><path fill="#557e3b" d="M0 310h170v-12h162v16h325v-21h184v17h119v9H0z"/>
  <g><path fill="#60452e" d="M99 175h28v123H99z"/><path fill="#8b673f" d="M104 175h8v123h-8z"/><path fill="url(#leaves)" d="M40 123h25V93h91v21h39v65h-28v28H63v-25H40z"/><path fill="#70984b" d="M65 93h91v10H65zM40 123h25v10H40z"/></g>
  <g><path fill="#60452e" d="M839 183h22v117h-22z"/><path fill="url(#leaves)" d="M783 137h20v-25h78v20h34v58h-24v17h-88v-22h-20z"/></g>
  <path fill="#493b2b" d="M352 177h260v131H352z"/><path fill="url(#planks)" d="M365 182h234v112H365z"/>
  <path fill="#533d2d" d="M332 177v-15h28v-15h28v-15h28v-15h130v15h28v15h29v15h29v15z"/>
  <path fill="#7d5e3b" d="M341 161h282v9H341zm28-16h225v8H369zm28-15h168v7H397z"/>
  <path fill="url(#stone)" d="M352 290h260v18H352zM566 101h28v49h-28z"/>
  <path fill="#55402c" d="M457 225h44v69h-44z"/><path fill="#c09454" d="M464 230h30v64h-30z"/><path fill="#755639" d="M469 235h19v23h-19zm0 32h19v22h-19z"/><rect x="486" y="261" width="4" height="5" fill="#e5d394"/>
  <g stroke="#654a32" stroke-width="6" :fill="focusing ? '#ffdf83' : '#d6e9be'"><path d="M381 210h48v43h-48zM528 210h48v43h-48z"/></g><path d="M405 210v43m-24-22h48m123-21v43m-24-22h48" stroke="#856941" stroke-width="4"/>
  <path fill="#b9976b" d="M456 308h47v13h27v13h29v15H408v-16h23v-12h25z"/>
  <g transform="translate(265 264)"><path fill="#4e3928" d="M0 0h37v34H0z"/><path fill="#b1804c" d="M3 3h31v27H3z"/><path fill="#dfb479" d="M3 3h31v8H3z"/><path fill="#795337" d="M10 3v8m13-8v8M3 17h31M8 20v10m19-10v10" stroke="#61432c" stroke-width="3"/></g>
  <g transform="translate(670 259)"><rect width="40" height="28" fill="#553b28"/><rect x="3" y="3" width="34" height="23" fill="#b88343"/><path d="M3 13h34" stroke="#5d4029" stroke-width="4"/><rect x="18" y="10" width="6" height="9" fill="#edcb76"/></g>
  <g fill="#a9c775"><path d="M35 290v-10h4v10h5v-15h4v23H35zm706-15v-10h4v10h5v-17h4v23h-13zm165 16v-10h4v10h5v-16h4v23h-13z"/></g>
  <g fill="#e6bb65"><path d="M226 280h5v9h-5zm513 11h5v8h-5z"/></g><path d="M224 278h9v5h-9zm513 10h9v4h-9z" fill="#f2d278"/>
</template>

</svg>
</template>

