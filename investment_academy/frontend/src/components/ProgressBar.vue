<template>
  <div class="progress-bar-wrap" :class="[`progress-bar-wrap--${size}`]">
    <div class="progress-bar-track">
      <div class="progress-bar-fill" :style="{ width: pct + '%' }" :class="fillClass">
        <div class="progress-bar-shimmer"></div>
      </div>
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
    size: { type: String, default: 'default' }, // thin, default, large
  },
  computed: {
    pct() { return Math.min(100, Math.round((this.value / this.max) * 100)) },
    fillClass() {
      const map = { green: 'fill-green', gold: 'fill-gold', blue: 'fill-blue', red: 'fill-red' }
      return map[this.color] || 'fill-gold'
    },
  },
}
</script>

<style scoped>
.progress-bar-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.progress-bar-track {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.progress-bar-wrap--thin .progress-bar-track { height: 4px; }
.progress-bar-wrap--large .progress-bar-track { height: 12px; border-radius: 6px; }

.progress-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 12px rgba(240, 185, 11, 0.18);
}

.progress-bar-wrap--large .progress-bar-fill { border-radius: 6px; }

.fill-gold {
  background: linear-gradient(90deg, rgba(240, 185, 11, 0.35), var(--ia-gold));
}

.fill-green {
  background: linear-gradient(90deg, rgba(14, 203, 129, 0.35), var(--ia-green));
  box-shadow: 0 0 12px rgba(14, 203, 129, 0.18);
}

.fill-blue {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.35), var(--ia-blue));
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.18);
}

.fill-red {
  background: linear-gradient(90deg, rgba(246, 70, 93, 0.35), var(--ia-red));
  box-shadow: 0 0 12px rgba(246, 70, 93, 0.18);
}

.progress-bar-shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.25) 50%,
    transparent 100%
  );
  transform: translateX(-100%);
  animation: shimmer 2.2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}

.progress-bar-label {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
  min-width: 48px;
  text-align: right;
  font-variant-numeric: tabular-nums;
  transition: color 0.3s ease;
  font-weight: 500;
}

.progress-bar-wrap:hover .progress-bar-label {
  color: var(--ia-gold);
}
</style>
