<template>
  <div class="progress-bar-wrap">
    <div class="progress-bar-track">
      <div class="progress-bar-fill" :style="{ width: pct + '%' }" :class="fillClass"></div>
    </div>
    <span class="progress-bar-label">{{ label || pct + '%' }}</span>
  </div>
</template>

<script>
export default {
  name: 'ProgressBar',
  props: {
    value: { type: Number, default: 0 },
    max: { type: Number, default: 100 },
    label: { type: String, default: '' },
    color: { type: String, default: 'gold' },
  },
  computed: {
    pct() { return Math.min(100, Math.round((this.value / this.max) * 100)) },
    fillClass() { return this.color === 'green' ? 'fill-green' : 'fill-gold' },
  },
}
</script>

<style scoped>
.progress-bar-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.progress-bar-track {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 3px;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}
.fill-gold { background: linear-gradient(90deg, rgba(240, 185, 11, 0.5), var(--ia-gold)); }
.fill-green { background: linear-gradient(90deg, rgba(14, 203, 129, 0.3), var(--ia-green)); }
.progress-bar-label {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
  min-width: 42px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}
</style>
