<template>
  <transition name="confirm-fade">
    <div v-if="visible" class="confirm-overlay" @click.self="onCancel">
      <div class="confirm-dialog" role="dialog" aria-modal="true">
        <div class="confirm-icon">
          <IAIcon name="warning" size="lg" />
        </div>
        <h3 class="confirm-title">{{ title }}</h3>
        <p v-if="message" class="confirm-message">{{ message }}</p>
        <div class="confirm-actions">
          <IAButton variant="ghost" size="lg" @click="onCancel" :disabled="loading">
            {{ cancelText }}
          </IAButton>
          <IAButton variant="danger" size="lg" :loading="loading" @click="onConfirm">
            {{ confirmText }}
          </IAButton>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import IAIcon from './Icon.vue'
import IAButton from './Button.vue'

export default {
  name: 'IAConfirmDialog',
  components: { IAIcon, IAButton },
  data() {
    return {
      visible: false,
      title: '确认操作',
      message: '',
      confirmText: '确认',
      cancelText: '取消',
      loading: false,
      resolve: null,
      reject: null,
    }
  },
  methods: {
    open(options = {}) {
      this.title = options.title || '确认操作'
      this.message = options.message || ''
      this.confirmText = options.confirmText || '确认'
      this.cancelText = options.cancelText || '取消'
      this.loading = false
      this.visible = true
      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    onCancel() {
      if (this.loading) return
      this.visible = false
      if (this.resolve) this.resolve(false)
      this.reset()
    },
    onConfirm() {
      if (this.loading) return
      this.loading = true
      if (this.resolve) this.resolve(true)
      this.close()
    },
    close() {
      this.visible = false
      this.reset()
    },
    reset() {
      setTimeout(() => {
        this.title = '确认操作'
        this.message = ''
        this.confirmText = '确认'
        this.cancelText = '取消'
        this.loading = false
        this.resolve = null
        this.reject = null
      }, 300)
    },
  },
}
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  z-index: 10001;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  padding: var(--ia-space-md);
}

.confirm-dialog {
  width: 100%;
  max-width: 560px;
  background: var(--ia-surface-glass);
  border: 1px solid var(--ia-glass-border);
  border-radius: var(--ia-radius-lg);
  padding: var(--ia-space-3xl) var(--ia-space-2xl);
  box-shadow: var(--ia-shadow-lg), 0 0 0 1px rgba(255, 255, 255, 0.04);
  text-align: center;
  transform-origin: center;
  backdrop-filter: blur(var(--ia-glass-blur));
  -webkit-backdrop-filter: blur(var(--ia-glass-blur));
}

.confirm-icon {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--ia-space-lg);
  background: var(--ia-red-soft);
  color: var(--ia-red);
  border: 1px solid rgba(246, 70, 93, 0.22);
  box-shadow: 0 0 20px rgba(246, 70, 93, 0.12);
}

.confirm-title {
  font-size: var(--ia-font-size-2xl);
  font-weight: 600;
  color: var(--ia-text);
  margin: 0 0 var(--ia-space-sm);
}

.confirm-message {
  font-size: var(--ia-font-size-lg);
  color: var(--ia-text-secondary);
  margin: 0 0 var(--ia-space-xl);
  line-height: 1.6;
}

.confirm-actions {
  display: flex;
  justify-content: center;
  gap: var(--ia-space-xl);
}

.confirm-actions .ia-btn {
  min-width: 160px;
  padding: 1rem 2.5rem;
  font-size: 1rem;
  border-radius: var(--ia-radius);
}

.confirm-fade-enter-active,
.confirm-fade-leave-active {
  transition: opacity 0.25s ease;
}

.confirm-fade-enter-active .confirm-dialog,
.confirm-fade-leave-active .confirm-dialog {
  transition: transform 0.35s var(--ia-transition-spring), opacity 0.25s ease;
}

.confirm-fade-enter,
.confirm-fade-leave-to {
  opacity: 0;
}

.confirm-fade-enter .confirm-dialog,
.confirm-fade-leave-to .confirm-dialog {
  opacity: 0;
  transform: scale(0.92) translateY(12px);
}

@media (max-width: 640px) {
  .confirm-dialog {
    max-width: 90vw;
    padding: var(--ia-space-2xl) var(--ia-space-lg);
  }
  .confirm-actions {
    flex-direction: column;
  }
  .confirm-actions .ia-btn {
    width: 100%;
  }
}
</style>
