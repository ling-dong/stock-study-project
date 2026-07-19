<template>
  <transition name="modal-fade">
    <div v-if="visible" class="ia-modal-overlay" @click.self="close">
      <div class="ia-modal" role="dialog" aria-modal="true" tabindex="-1" ref="modal" @keydown.esc="close">
        <div class="ia-modal__header">
          <h3 class="ia-modal__title">{{ title }}</h3>
          <button class="ia-modal__close" @click="close" aria-label="关闭">
            <IAIcon name="close" size="md" />
          </button>
        </div>
        <div ref="body" class="ia-modal__body">
          <slot />
        </div>
        <div v-if="$slots.footer" class="ia-modal__footer">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import IAIcon from './Icon.vue'

export default {
  name: 'IAModal',
  components: { IAIcon },
  props: {
    visible: { type: Boolean, default: false },
    title: { type: String, default: '' },
  },
  watch: {
    visible(val) {
      if (val) {
        this.$nextTick(() => {
          const modal = this.$refs.modal
          if (modal) modal.focus()
        })
      }
    },
  },
  methods: {
    close() {
      this.$emit('close')
    },
  },
}
</script>

<style scoped>
.ia-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 10002;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  padding: var(--ia-space-xl);
}

.ia-modal {
  width: 100%;
  min-width: 560px;
  max-width: 720px;
  max-height: 86vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: var(--ia-surface-elevated);
  border: 1px solid var(--ia-border-strong);
  border-radius: var(--ia-radius-xl);
  box-shadow: var(--ia-shadow-lg), 0 0 0 1px rgba(255, 255, 255, 0.04);
  transform-origin: center;
  margin: auto;
  outline: none;
}

.ia-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--ia-space-md);
  padding: var(--ia-space-xl) var(--ia-space-2xl) var(--ia-space-lg);
  border-bottom: 1px solid var(--ia-glass-border);
  flex-shrink: 0;
}

.ia-modal__title {
  font-size: var(--ia-font-size-xl);
  font-weight: 600;
  color: var(--ia-text);
  margin: 0;
  line-height: 1.3;
}

.ia-modal__close {
  width: 44px;
  height: 44px;
  border-radius: var(--ia-radius);
  border: 1px solid var(--ia-glass-border);
  background: transparent;
  color: var(--ia-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--ia-transition-fast);
  flex-shrink: 0;
}

.ia-modal__close:hover {
  border-color: var(--ia-gold);
  color: var(--ia-gold);
  background: var(--ia-gold-soft);
  transform: rotate(90deg);
}

.ia-modal__body {
  padding: var(--ia-space-2xl);
  overflow-y: auto;
}

.ia-modal__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--ia-space-lg);
  padding: var(--ia-space-lg) var(--ia-space-2xl);
  border-top: 1px solid var(--ia-glass-border);
  background: rgba(255, 255, 255, 0.02);
  flex-shrink: 0;
}

.ia-modal__footer ::v-deep .ia-btn {
  min-width: 120px;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-active .ia-modal,
.modal-fade-leave-active .ia-modal {
  transition: transform 0.35s var(--ia-transition-spring), opacity 0.25s ease;
}

.modal-fade-enter,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter .ia-modal,
.modal-fade-leave-to .ia-modal {
  opacity: 0;
  transform: scale(0.92) translateY(12px);
}

@media (max-width: 640px) {
  .ia-modal-overlay {
    padding: var(--ia-space-md);
    align-items: flex-end;
  }
  .ia-modal {
    min-width: auto;
    max-width: 100vw;
    max-height: 92vh;
    border-radius: var(--ia-radius-lg) var(--ia-radius-lg) 0 0;
    margin-bottom: 0;
  }
  .ia-modal__header,
  .ia-modal__body,
  .ia-modal__footer {
    padding-left: var(--ia-space-lg);
    padding-right: var(--ia-space-lg);
  }
  .ia-modal__header {
    padding-top: var(--ia-space-lg);
  }
  .ia-modal__body {
    padding-top: var(--ia-space-lg);
    padding-bottom: var(--ia-space-lg);
  }
  .ia-modal__footer {
    padding-top: var(--ia-space-md);
    padding-bottom: var(--ia-space-md);
  }
}
</style>
