<template>
  <span class="ia-badge" :class="[`ia-badge--${variant}`, { 'ia-badge--dot': dot }]">
    <slot />
  </span>
</template>

<script>
export default {
  name: 'IABadge',
  props: {
    variant: { type: String, default: 'neutral' }, // gold, green, red, blue, neutral
    dot: { type: Boolean, default: false },
  },
}
</script>
