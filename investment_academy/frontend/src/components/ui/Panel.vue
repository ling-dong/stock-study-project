<template>
  <div class="ia-panel" :class="{ 'ia-panel--loading': loading }">
    <div v-if="title || subtitle || $slots['header-actions'] || icon" class="ia-panel__header">
      <div v-if="icon" class="ia-panel__icon" :class="{ 'ia-panel__icon--sm': compact }">
        <IAIcon v-if="typeof icon === 'string'" :name="icon" size="md" />
        <slot v-else name="icon" />
      </div>
      <div class="ia-panel__title-group">
        <h3 v-if="title" class="ia-panel__title">{{ title }}</h3>
        <p v-if="subtitle" class="ia-panel__subtitle">{{ subtitle }}</p>
      </div>
      <span v-if="tag" class="ia-panel__tag">{{ tag }}</span>
      <div v-if="$slots['header-actions']" class="ia-panel__actions">
        <slot name="header-actions" />
      </div>
    </div>
    <div class="ia-panel__body" :class="bodyClass">
      <div v-if="loading" class="ia-panel__loading">
        <IAIcon name="spinner" size="md" class="ia-anim-spin" />
        <span>加载中…</span>
      </div>
      <slot v-else />
    </div>
  </div>
</template>

<script>
import IAIcon from './Icon.vue'

export default {
  name: 'IAPanel',
  components: { IAIcon },
  props: {
    title: { type: String, default: '' },
    subtitle: { type: String, default: '' },
    icon: { type: [String, Boolean], default: '' },
    tag: { type: String, default: '' },
    loading: { type: Boolean, default: false },
    compact: { type: Boolean, default: false },
    bodyClass: { type: String, default: '' },
  },
}
</script>

<style scoped>
.ia-panel__loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--ia-space-sm);
  padding: var(--ia-space-xl);
  color: var(--ia-text-secondary);
  font-size: var(--ia-font-size-md);
}
</style>
