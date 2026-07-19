<template>
  <button
    class="ia-btn"
    :class="[`ia-btn--${variant}`, `ia-btn--${size}`, { 'ia-btn--pill': pill }]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <IAIcon v-if="loading" name="spinner" size="sm" class="ia-btn__spinner" />
    <slot />
  </button>
</template>

<script>
import IAIcon from './Icon.vue'

export default {
  name: 'IAButton',
  components: { IAIcon },
  props: {
    variant: { type: String, default: 'primary' }, // primary, secondary, ghost, danger
    size: { type: String, default: 'md' }, // sm, md, lg
    pill: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
    loading: { type: Boolean, default: false },
  },
}
</script>
