<template>
  <div class="progress-bar-wrap">
    <div class="progress-bar-track">
      <div
        class="progress-bar-fill"
        :style="{ width: pct + '%' }"
        :class="fillClass"
      ></div>
    </div>
    <span class="progress-bar-label">{{ label || pct + '%' }}</span>
  </div>
</template>

<script>
export default {
  name: 'ProgressBar',
  props: {
    value: { type: Number, default: 0 },   // 0-100
    max: { type: Number, default: 100 },
    label: { type: String, default: '' },
    color: { type: String, default: 'gold' },  // gold | green
  },
  computed: {
    pct() {
      return Math.min(100, Math.round((this.value / this.max) * 100))
    },
    fillClass() {
      return this.color === 'green' ? 'fill-green' : 'fill-gold'
    },
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
  background: #1A1A1D;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}

.fill-gold {
  background: linear-gradient(90deg, #F0B90B88, #F0B90B);
}

.fill-green {
  background: linear-gradient(90deg, #4ADE8044, #4ADE80);
}

.progress-bar-label {
  font-size: 0.75rem;
  color: #6B6B7B;
  min-width: 42px;
  text-align: right;
}
</style>
