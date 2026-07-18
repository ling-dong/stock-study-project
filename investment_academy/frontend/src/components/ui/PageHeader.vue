<template>
  <header class="ia-page-header">
    <nav v-if="breadcrumbs && breadcrumbs.length" class="ia-breadcrumb">
      <span v-for="(item, idx) in breadcrumbs" :key="idx">
        <router-link v-if="item.to" :to="item.to">{{ item.label }}</router-link>
        <span v-else :class="{ 'ia-breadcrumb__current': idx === breadcrumbs.length - 1 }">
          {{ item.label }}
        </span>
        <span v-if="idx < breadcrumbs.length - 1" class="ia-breadcrumb__sep">/</span>
      </span>
    </nav>
    <div class="ia-page-header__top">
      <div>
        <h1 class="ia-page-header__title">
          {{ title }}
          <span v-if="titleHighlight">{{ titleHighlight }}</span>
        </h1>
        <p v-if="subtitle" class="ia-page-header__subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="ia-page-header__actions">
        <slot name="actions" />
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'IAPageHeader',
  props: {
    title: { type: String, required: true },
    titleHighlight: { type: String, default: '' },
    subtitle: { type: String, default: '' },
    breadcrumbs: { type: Array, default: () => [] },
  },
}
</script>
