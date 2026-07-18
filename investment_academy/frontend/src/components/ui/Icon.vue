<template>
  <svg
    class="ia-icon"
    :class="[`ia-icon--${size}`]"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path v-if="name === 'home'" d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <polyline v-if="name === 'home'" points="9 22 9 12 15 12 15 22" />

    <path v-if="name === 'book'" d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
    <path v-if="name === 'book'" d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />

    <path v-if="name === 'lab'" d="M10 2v7.31" />
    <path v-if="name === 'lab'" d="M14 2v7.31" />
    <path v-if="name === 'lab'" d="M8.5 22h7" />
    <path v-if="name === 'lab'" d="M6.75 9.5l-3.5 10.5h17.5l-3.5-10.5" />

    <path v-if="name === 'tool'" d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.3-3.3a1 1 0 0 0 0-1.4l-1.6-1.6" />
    <path v-if="name === 'tool'" d="M17 2l-4 4" />
    <path v-if="name === 'tool'" d="M2 22l6-6" />
    <path v-if="name === 'tool'" d="M4 16l-2 2 2 2 2-2-2-2z" />

    <path v-if="name === 'brain'" d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18a4 4 0 1 0 4-4 4 4 0 0 0-.556-6.588A4 4 0 0 0 12 5z" />
    <path v-if="name === 'brain'" d="M12 13v8" />

    <path v-if="name === 'journal'" d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline v-if="name === 'journal'" points="14 2 14 8 20 8" />

    <path v-if="name === 'chart'" d="M3 3v18h18" />
    <path v-if="name === 'chart'" d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3" />

    <path v-if="name === 'market'" d="M22 12h-4l-3 9L9 3l-3 9H2" />

    <path v-if="name === 'signal'" d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />

    <path v-if="name === 'analysis'" d="M12 20h9" />
    <path v-if="name === 'analysis'" d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />

    <path v-if="name === 'check'" d="M20 6L9 17l-5-5" />

    <path v-if="name === 'close'" d="M18 6L6 18M6 6l12 12" />

    <path v-if="name === 'arrow-left'" d="M19 12H5M12 19l-7-7 7-7" />
    <path v-if="name === 'arrow-right'" d="M5 12h14M12 5l7 7-7 7" />
    <path v-if="name === 'arrow-down'" d="M12 5v14M19 12l-7 7-7-7" />
    <path v-if="name === 'arrow-up'" d="M12 19V5M5 12l7-7 7 7" />

    <circle v-if="name === 'spinner'" cx="12" cy="12" r="10" stroke-opacity="0.2" />
    <path v-if="name === 'spinner'" d="M22 12a10 10 0 0 1-10 10" />

    <path v-if="name === 'menu'" d="M3 12h18M3 6h18M3 18h18" />

    <path v-if="name === 'search'" d="M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z" />
    <path v-if="name === 'search'" d="M21 21l-4.35-4.35" />

    <path v-if="name === 'calendar'" d="M19 4H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2z" />
    <path v-if="name === 'calendar'" d="M16 2v4M8 2v4M3 10h18" />

    <circle v-if="name === 'dot'" cx="12" cy="12" r="10" />

    <path v-if="name === 'warning'" d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
    <line v-if="name === 'warning'" x1="12" y1="9" x2="12" y2="13" />
    <line v-if="name === 'warning'" x1="12" y1="17" x2="12.01" y2="17" />

    <path v-if="name === 'trash'" d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />

    <path v-if="name === 'edit'" d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
    <path v-if="name === 'edit'" d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />

    <path v-if="name === 'grid'" d="M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z" />

    <path v-if="name === 'activity'" d="M22 12h-4l-3 9L9 3l-3 9H2" />

    <path v-if="name === 'trending-up'" d="M23 6l-9.5 9.5-5-5L1 18" />
    <path v-if="name === 'trending-up'" d="M17 6h6v6" />

    <path v-if="name === 'trending-down'" d="M23 18l-9.5-9.5-5 5L1 6" />
    <path v-if="name === 'trending-down'" d="M17 18h6v-6" />

    <path v-if="name === 'clock'" d="M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z" />
    <polyline v-if="name === 'clock'" points="12 6 12 12 16 14" />
  </svg>
</template>

<script>
export default {
  name: 'IAIcon',
  props: {
    name: { type: String, required: true },
    size: { type: String, default: 'md' }, // xs, sm, md, lg, xl
  },
}
</script>

<style scoped>
.ia-icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
}
.ia-icon--xs { width: 12px; height: 12px; }
.ia-icon--sm { width: 14px; height: 14px; }
.ia-icon--md { width: 18px; height: 18px; }
.ia-icon--lg { width: 22px; height: 22px; }
.ia-icon--xl { width: 28px; height: 28px; }
</style>
