<template>
  <transition-group
    name="toast"
    tag="div"
    class="toast-container"
    @mouseenter="paused = true"
    @mouseleave="paused = false"
  >
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="toast"
      :class="[`toast--${toast.type}`]"
      @click="remove(toast.id)"
    >
      <span class="toast-icon"><IAIcon :name="iconName(toast.type)" size="sm" /></span>
      <span class="toast-message">{{ toast.message }}</span>
      <div class="toast-progress-wrap">
        <div class="toast-progress" :style="{ width: progressWidth(toast) + '%' }"></div>
        <div class="toast-progress-shimmer"></div>
      </div>
      <div class="toast-glow"></div>
    </div>
  </transition-group>
</template>

<script>
import IAIcon from './Icon.vue'

let nextId = 1

export default {
  name: 'IAToast',
  components: { IAIcon },
  data() {
    return {
      toasts: [],
      paused: false,
      tick: 0,
      timer: null,
    }
  },
  mounted() {
    this.timer = setInterval(() => {
      if (!this.paused) {
        this.tick++
        this.toasts = this.toasts.filter(t => {
          const elapsed = this.tick - t.startTick
          return elapsed < t.duration / 100
        })
      }
    }, 100)
  },
  beforeDestroy() {
    if (this.timer) clearInterval(this.timer)
  },
  methods: {
    add(message, type = 'info', duration = 3000) {
      const id = nextId++
      this.toasts.push({ id, message, type, duration, startTick: this.tick })
      if (this.toasts.length > 5) this.toasts.shift()
    },
    remove(id) {
      this.toasts = this.toasts.filter(t => t.id !== id)
    },
    iconName(type) {
      return { success: 'check', error: 'warning', warning: 'warning', info: 'dot' }[type] || 'dot'
    },
    progressWidth(toast) {
      const elapsed = (this.tick - toast.startTick) * 100
      const remaining = Math.max(0, toast.duration - elapsed)
      return (remaining / toast.duration) * 100
    },
  },
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1.1rem;
  right: 1.1rem;
  z-index: 10000;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  pointer-events: none;
}

.toast {
  pointer-events: auto;
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  min-width: 300px;
  max-width: 460px;
  padding: 1.05rem 1.2rem;
  border-radius: var(--ia-radius);
  background: var(--ia-surface-glass);
  border: 1px solid var(--ia-glass-border);
  box-shadow: var(--ia-shadow-md), 0 0 0 1px rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(var(--ia-glass-blur));
  -webkit-backdrop-filter: blur(var(--ia-glass-blur));
  cursor: pointer;
  overflow: hidden;
  transition: transform var(--ia-transition-fast), box-shadow var(--ia-transition-fast), border-color var(--ia-transition-fast);
}

.toast:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: var(--ia-shadow-lg), 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.toast-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
}

.toast-message {
  flex: 1;
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text);
  line-height: 1.45;
}

.toast-progress-wrap {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.04);
}

.toast-progress {
  height: 100%;
  background: currentColor;
  opacity: 0.55;
  box-shadow: 0 0 10px currentColor;
  transition: width 0.1s linear;
}

.toast-progress-shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.35), transparent);
  transform: translateX(-100%);
  animation: shimmer 1.8s infinite;
  pointer-events: none;
}

.toast-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.08;
  background: radial-gradient(circle at 80% 0%, currentColor, transparent 60%);
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}

.toast--success { border-color: rgba(14, 203, 129, 0.30); color: var(--ia-green); }
.toast--success .toast-icon { color: var(--ia-green); }
.toast--success .toast-message { color: var(--ia-green); }
.toast--success .toast-glow { opacity: 0.12; }

.toast--error { border-color: rgba(246, 70, 93, 0.30); color: var(--ia-red); }
.toast--error .toast-icon { color: var(--ia-red); }
.toast--error .toast-message { color: var(--ia-red); }
.toast--error .toast-glow { opacity: 0.12; }

.toast--warning { border-color: rgba(240, 185, 11, 0.30); color: var(--ia-gold); }
.toast--warning .toast-icon { color: var(--ia-gold); }
.toast--warning .toast-message { color: var(--ia-gold); }
.toast--warning .toast-glow { opacity: 0.12; }

.toast--info { border-color: rgba(96, 165, 250, 0.30); color: var(--ia-blue); }
.toast--info .toast-icon { color: var(--ia-blue); }
.toast--info .toast-message { color: var(--ia-blue); }
.toast--info .toast-glow { opacity: 0.12; }

.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.toast-enter {
  opacity: 0;
  transform: translateX(50px) scale(0.94);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(40px) scale(0.92);
  max-height: 0;
  margin: 0;
  padding: 0;
}

.toast-move {
  transition: transform 0.35s ease;
}

@media (max-width: 640px) {
  .toast-container {
    left: 0.75rem;
    right: 0.75rem;
    top: 0.75rem;
  }
  .toast {
    min-width: auto;
    max-width: none;
  }
}
</style>
