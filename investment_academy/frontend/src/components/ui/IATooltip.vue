<template>
  <span class="ia-tooltip-wrap">
    <slot />
    <span class="ia-tooltip" :class="[`ia-tooltip--${position}`]">
      <span class="ia-tooltip__content">{{ content }}</span>
    </span>
  </span>
</template>

<script>
export default {
  name: 'IATooltip',
  props: {
    content: { type: String, required: true },
    position: { type: String, default: 'top' }, // top, bottom, left, right
  },
}
</script>

<style scoped>
.ia-tooltip-wrap {
  position: relative;
  display: inline-flex;
}

.ia-tooltip {
  position: absolute;
  z-index: 5000;
  pointer-events: none;
  opacity: 0;
  transform: translateY(6px) scale(0.96);
  transition: opacity 0.2s ease, transform 0.2s ease;
  padding: 0.35rem 0;
}

.ia-tooltip-wrap:hover .ia-tooltip {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.ia-tooltip__content {
  display: block;
  max-width: 260px;
  padding: 0.55rem 0.85rem;
  border-radius: var(--ia-radius-xs);
  background: var(--ia-surface-glass);
  border: 1px solid var(--ia-glass-border);
  color: var(--ia-text);
  font-size: var(--ia-font-size-xs);
  line-height: 1.45;
  box-shadow: var(--ia-shadow-md);
  backdrop-filter: blur(var(--ia-glass-blur));
  -webkit-backdrop-filter: blur(var(--ia-glass-blur));
  white-space: normal;
  word-break: break-word;
}

.ia-tooltip__content::after {
  content: '';
  position: absolute;
  width: 7px;
  height: 7px;
  background: var(--ia-surface-glass);
  border: 1px solid var(--ia-glass-border);
}

.ia-tooltip--top {
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(6px);
}

.ia-tooltip--top .ia-tooltip__content::after {
  top: 100%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(45deg);
  border-top-color: transparent;
  border-left-color: transparent;
}

.ia-tooltip-wrap:hover .ia-tooltip--top {
  transform: translateX(-50%) translateY(0);
}

.ia-tooltip--bottom {
  top: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(-6px);
}

.ia-tooltip--bottom .ia-tooltip__content::after {
  bottom: 100%;
  left: 50%;
  transform: translate(-50%, 50%) rotate(45deg);
  border-bottom-color: transparent;
  border-right-color: transparent;
}

.ia-tooltip-wrap:hover .ia-tooltip--bottom {
  transform: translateX(-50%) translateY(0);
}

.ia-tooltip--left {
  right: 100%;
  top: 50%;
  transform: translateY(-50%) translateX(-6px);
  padding: 0 0.35rem;
}

.ia-tooltip--left .ia-tooltip__content::after {
  top: 50%;
  left: 100%;
  transform: translate(-50%, -50%) rotate(45deg);
  border-left-color: transparent;
  border-bottom-color: transparent;
}

.ia-tooltip-wrap:hover .ia-tooltip--left {
  transform: translateY(-50%) translateX(0);
}

.ia-tooltip--right {
  left: 100%;
  top: 50%;
  transform: translateY(-50%) translateX(6px);
  padding: 0 0.35rem;
}

.ia-tooltip--right .ia-tooltip__content::after {
  top: 50%;
  right: 100%;
  transform: translate(50%, -50%) rotate(45deg);
  border-right-color: transparent;
  border-top-color: transparent;
}

.ia-tooltip-wrap:hover .ia-tooltip--right {
  transform: translateY(-50%) translateX(0);
}

@media (max-width: 640px) {
  .ia-tooltip__content {
    max-width: 200px;
  }
}
</style>
