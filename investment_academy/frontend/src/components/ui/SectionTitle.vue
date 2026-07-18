<template>
  <div class="ia-section-title">
    <IAIcon v-if="icon" :name="icon" size="md" class="ia-text-gold" />
    <div>
      <h2>{{ title }}</h2>
      <p v-if="subtitle">{{ subtitle }}</p>
    </div>
  </div>
</template>

<script>
import IAIcon from './Icon.vue'

export default {
  name: 'IASectionTitle',
  components: { IAIcon },
  props: {
    title: { type: String, required: true },
    subtitle: { type: String, default: '' },
    icon: { type: String, default: '' },
  },
}
</script>

<style scoped>
.ia-section-title div {
  display: flex;
  flex-direction: column;
  gap: var(--ia-space-xs);
}
.ia-section-title h2 {
  margin: 0;
}
.ia-section-title p {
  margin: 0;
}
</style>
