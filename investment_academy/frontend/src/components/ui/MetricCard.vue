<template>
  <div class="ia-metric-card" :class="[`ia-metric-card--${trend}`]">
    <div class="ia-metric-card__label">{{ label }}</div>
    <div class="ia-metric-card__value">
      {{ displayValue }}
      <span v-if="unit">{{ unit }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IAMetricCard',
  props: {
    label: { type: String, required: true },
    value: { type: [Number, String], required: true },
    unit: { type: String, default: '' },
    trend: { type: String, default: 'neutral' }, // up, down, neutral
    decimals: { type: Number, default: 0 },
  },
  computed: {
    displayValue() {
      if (typeof this.value === 'number') {
        return this.value.toFixed(this.decimals)
      }
      return this.value
    },
  },
}
</script>

<style scoped>
.ia-metric-card--up:hover {
  border-color: var(--ia-green);
  box-shadow: var(--ia-glow-green);
}
.ia-metric-card--down:hover {
  border-color: var(--ia-red);
  box-shadow: var(--ia-glow-red);
}
.ia-metric-card__value {
  display: flex;
  align-items: baseline;
  gap: 0.2rem;
}
</style>
