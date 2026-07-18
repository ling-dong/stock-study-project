<template>
  <div class="probability-ring" :style="{ width: size + 'px', height: size + 'px' }">
    <svg class="ring-svg" :viewBox="`0 0 ${size} ${size}`" :width="size" :height="size">
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        class="ring-bg"
        :stroke-width="strokeWidth"
      />
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        class="ring-fill"
        :stroke-width="strokeWidth"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="circumference * (1 - clampValue)"
        :stroke="activeColor"
      />
    </svg>
    <div class="ring-center">
      <span class="ring-value" :style="{ color: activeColor }">{{ (clampValue * 100).toFixed(0) }}</span>
      <span class="ring-unit">%</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProbabilityRing',
  props: {
    value: { type: Number, default: 0.5 },
    size: { type: Number, default: 120 },
    strokeWidth: { type: Number, default: 6 },
  },
  computed: {
    clampValue() {
      return Math.max(0, Math.min(1, this.value))
    },
    radius() {
      return (this.size - this.strokeWidth) / 2
    },
    circumference() {
      return 2 * Math.PI * this.radius
    },
    activeColor() {
      if (this.clampValue >= 0.55) return 'var(--ia-green)'
      if (this.clampValue <= 0.45) return 'var(--ia-red)'
      return 'var(--ia-gold)'
    },
  },
}
</script>

<style scoped>
.probability-ring {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.ring-svg {
  transform: rotate(-90deg);
}
.ring-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.06);
}
.ring-fill {
  fill: none;
  stroke-linecap: round;
  transition: stroke-dashoffset 1s ease-out;
}
.ring-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.ring-value {
  font-size: 1.7rem;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.03em;
}
.ring-unit {
  font-size: 0.65rem;
  color: var(--ia-text-tertiary);
  margin-top: 0.1rem;
}
</style>
