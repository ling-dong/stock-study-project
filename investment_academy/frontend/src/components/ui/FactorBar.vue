<template>
  <div class="factor-bar-row" :class="{ positive: contribution > 0, negative: contribution < 0 }">
    <div class="factor-info">
      <span class="factor-name">{{ factor }}</span>
      <span v-if="detail" class="factor-detail" :title="detail">{{ detail }}</span>
    </div>
    <div class="factor-bar-wrap">
      <div class="factor-bar" :style="barStyle"></div>
    </div>
    <span class="factor-value" :class="valueClass">
      {{ contribution > 0 ? '+' : '' }}{{ (contribution * 100).toFixed(0) }}%
    </span>
  </div>
</template>

<script>
export default {
  name: 'FactorBar',
  props: {
    factor: { type: String, required: true },
    contribution: { type: Number, required: true },
    detail: { type: String, default: '' },
    maxWidth: { type: Number, default: 120 },
  },
  computed: {
    barStyle() {
      const abs = Math.abs(this.contribution) * 100
      const width = Math.min(abs * 4, this.maxWidth)
      return {
        width: width + 'px',
      }
    },
    valueClass() {
      if (this.contribution > 0) return 'ia-text-green'
      if (this.contribution < 0) return 'ia-text-red'
      return 'ia-text-tertiary'
    },
  },
}
</script>

<style scoped>
.factor-bar-row {
  display: flex;
  align-items: center;
  gap: var(--ia-space-md);
  padding: 0.45rem 0.6rem;
  border-radius: var(--ia-radius-xs);
  transition: background var(--ia-transition-fast);
}
.factor-bar-row:hover {
  background: rgba(255, 255, 255, 0.02);
}
.factor-bar-row.positive {
  background: linear-gradient(90deg, rgba(14, 203, 129, 0.04), transparent);
}
.factor-bar-row.negative {
  background: linear-gradient(90deg, rgba(246, 70, 93, 0.04), transparent);
}
.factor-info {
  flex: 0 0 160px;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}
.factor-name {
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text);
  font-weight: 500;
}
.factor-detail {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.factor-bar-wrap {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 2px;
  overflow: hidden;
}
.factor-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.8s ease-out;
  background: var(--ia-text-tertiary);
}
.factor-bar-row.positive .factor-bar {
  background: var(--ia-green);
}
.factor-bar-row.negative .factor-bar {
  background: var(--ia-red);
}
.factor-value {
  flex: 0 0 48px;
  text-align: right;
  font-size: var(--ia-font-size-sm);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
</style>
