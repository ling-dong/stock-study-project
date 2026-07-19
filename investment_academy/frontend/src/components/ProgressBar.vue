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
  gap: 0.85rem;
}

.progress-bar-track {
  flex: 1;
  height: 10px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 999px;
  overflow: hidden;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.25);
}

.progress-bar-wrap--thin .progress-bar-track { height: 5px; }
.progress-bar-wrap--large .progress-bar-track { height: 14px; }

.progress-bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.9s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 14px currentColor;
  animation: fill-glow 2.2s ease-in-out infinite;
}

.fill-gold {
  background: linear-gradient(90deg, rgba(240, 185, 11, 0.45), var(--ia-gold), #FFF0A3);
  color: rgba(240, 185, 11, 0.18);
}

.fill-green {
  background: linear-gradient(90deg, rgba(14, 203, 129, 0.45), var(--ia-green));
  color: rgba(14, 203, 129, 0.18);
}

.fill-blue {
  background: linear-gradient(90deg, rgba(96, 165, 250, 0.45), var(--ia-blue));
  color: rgba(96, 165, 250, 0.18);
}

.fill-red {
  background: linear-gradient(90deg, rgba(246, 70, 93, 0.45), var(--ia-red));
  color: rgba(246, 70, 93, 0.18);
}

.progress-bar-shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.35) 50%,
    transparent 100%
  );
  transform: translateX(-100%);
  animation: shimmer 2.2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}

@keyframes fill-glow {
  0%, 100% { filter: brightness(1); }
  50% { filter: brightness(1.12); }
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
