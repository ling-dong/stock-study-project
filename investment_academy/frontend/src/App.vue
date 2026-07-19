<template>
  <div id="app-root" :class="rootClass" :style="rootStyle">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">
          <IAIcon name="activity" size="xl" />
        </div>
        <div class="brand-text">
          投资学院
          <span>Investment Academy</span>
        </div>
      </div>

      <button class="sidebar-toggle" @click="toggleSidebar" :title="collapsed ? '展开侧边栏' : '收起侧边栏'">
        <IAIcon :name="collapsed ? 'chevron-right' : 'chevron-left'" size="md" />
      </button>

      <nav class="sidebar-nav">
        <div class="nav-section">
          <router-link to="/" class="nav-item" active-class="nav-item--active" exact>
            <IAIcon name="home" size="md" />
            <span class="nav-label">首页</span>
          </router-link>
        </div>

        <div class="nav-section">
          <div class="nav-section-title">学习轨道</div>
          <router-link
            v-for="p in phases" :key="p.id"
            :to="`/knowledge/${p.id}`"
            class="nav-item"
            active-class="nav-item--active"
          >
            <IAIcon name="book" size="md" />
            <span class="nav-label">{{ formatPhaseLabel(p.id) }}</span>
            <span class="nav-count">{{ p.chapter_count }}章</span>
          </router-link>
        </div>

        <div class="nav-section">
          <div class="nav-section-title">实践轨道</div>
          <router-link
            v-for="lab in labs" :key="lab.id"
            :to="`/practice/${lab.id}`"
            class="nav-item"
            active-class="nav-item--active"
          >
            <IAIcon name="lab" size="md" />
            <span class="nav-label">{{ formatLabLabel(lab.id) }}</span>
            <IAIcon v-if="lab.has_guide" name="book" size="xs" class="nav-guide" />
          </router-link>
        </div>

        <div class="nav-section">
          <div class="nav-section-title">工具箱</div>
          <router-link to="/sandbox" class="nav-item" active-class="nav-item--active">
            <IAIcon name="tool" size="md" />
            <span class="nav-label">交易沙盒</span>
          </router-link>
          <router-link to="/psychology" class="nav-item" active-class="nav-item--active">
            <IAIcon name="brain" size="md" />
            <span class="nav-label">心理自检</span>
          </router-link>
          <router-link to="/journal" class="nav-item" active-class="nav-item--active">
            <IAIcon name="journal" size="md" />
            <span class="nav-label">交易日志</span>
          </router-link>
          <router-link to="/progress" class="nav-item" active-class="nav-item--active">
            <IAIcon name="chart" size="md" />
            <span class="nav-label">进度仪表盘</span>
          </router-link>
        </div>

        <div class="nav-section">
          <div class="nav-section-title">市场分析</div>
          <router-link to="/market-overview" class="nav-item" active-class="nav-item--active">
            <IAIcon name="market" size="md" />
            <span class="nav-label">市场概览</span>
          </router-link>
          <router-link to="/spas" class="nav-item" active-class="nav-item--active">
            <IAIcon name="signal" size="md" />
            <span class="nav-label">SPAS 自动信号</span>
          </router-link>
          <router-link to="/manual-analysis" class="nav-item" active-class="nav-item--active">
            <IAIcon name="analysis" size="md" />
            <span class="nav-label">手动指标分析</span>
          </router-link>
        </div>
      </nav>

      <div class="sidebar-footer">
        <IATooltip :content="apiOk ? 'API 已连接' : 'API 未连接'" position="right">
          <div class="api-badge" :class="apiOk ? 'ia-badge--green' : 'ia-badge--red'">
            <IAIcon name="dot" size="xs" class="api-dot" />
            <span class="api-badge-text">{{ apiOk ? 'API 已连接' : 'API 未连接' }}</span>
          </div>
        </IATooltip>
      </div>
    </aside>

    <div class="mobile-overlay" @click="collapsed = true"></div>

    <main class="main-content">
      <div class="mobile-header">
        <button class="mobile-header__toggle" @click="toggleSidebar" title="菜单">
          <IAIcon name="menu" size="md" />
        </button>
        <span class="mobile-header__title">投资学院</span>
      </div>

      <div class="theme-picker">
        <button class="theme-picker__btn" @click="themeOpen = !themeOpen" title="切换背景与主题">
          <IAIcon name="settings" size="md" />
        </button>
        <transition name="fade">
          <div v-if="themeOpen" class="theme-picker__panel" v-click-outside="closeTheme">
            <div
              v-for="t in themes"
              :key="t.key"
              class="theme-option"
              :class="{ active: currentTheme === t.key }"
              @click="setTheme(t.key)"
            >
              <span class="theme-swatch" :style="{ background: t.color }"></span>
              <span class="theme-label">{{ t.label }}</span>
            </div>
          </div>
        </transition>
      </div>

      <transition name="page" mode="out-in">
        <router-view />
      </transition>
    </main>
  </div>
</template>

<script>
import { IAIcon, IATooltip } from './components/ui'
import { getPhases, getLabs } from './api/content'
import { healthCheck } from './api/index'

export default {
  name: 'App',
  components: { IAIcon, IATooltip },
  directives: {
    'click-outside': {
      bind(el, binding, vnode) {
        el._clickOutside = (e) => {
          if (!el.contains(e.target)) {
            vnode.context[binding.expression]()
          }
        }
        document.addEventListener('click', el._clickOutside, true)
      },
      unbind(el) {
        document.removeEventListener('click', el._clickOutside, true)
      },
    },
  },
  data() {
    const savedTheme = typeof localStorage !== 'undefined' ? localStorage.getItem('ia-bg-theme') : 'dark'
    return {
      phases: [],
      labs: [],
      apiOk: false,
      collapsed: false,
      isMobile: false,
      themeOpen: false,
      currentTheme: savedTheme || 'dark',
      themes: [
        { key: 'dark', label: '深邃黑', color: '#0F0E12' },
        { key: 'navy', label: '暗夜蓝', color: '#0A0F1C' },
        { key: 'graphite', label: '石墨灰', color: '#121212' },
        { key: 'plum', label: '暗梅紫', color: '#150C18' },
        { key: 'coffee', label: '暖咖棕', color: '#12100C' },
        { key: 'light', label: '暖白', color: '#F7F3EF' },
      ],
    }
  },
  computed: {
    rootClass() {
      const classes = { 'sidebar-collapsed': this.collapsed, 'sidebar-mobile-open': !this.collapsed && this.isMobile }
      if (this.currentTheme === 'light') classes['ia-light'] = true
      return classes
    },
    rootStyle() {
      const t = this.currentTheme
      if (t === 'light') return { '--ia-bg': '#F7F3EF' }
      const map = {
        dark: '#0F0E12',
        navy: '#0A0F1C',
        graphite: '#121212',
        plum: '#150C18',
        coffee: '#12100C',
      }
      return { '--ia-bg': map[t] || map.dark }
    },
  },
  async created() {
    this.checkMobile()
    window.addEventListener('resize', this.checkMobile)
    try {
      await healthCheck()
      this.apiOk = true
    } catch (e) {
      this.apiOk = false
    }
    try {
      const [phasesRes, labsRes] = await Promise.all([getPhases(), getLabs()])
      this.phases = phasesRes.data || []
      this.labs = labsRes.data || []
    } catch (e) {
      console.error('加载导航失败:', e)
    }
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.checkMobile)
  },
  methods: {
    checkMobile() {
      this.isMobile = window.innerWidth <= 768
    },
    toggleSidebar() {
      this.collapsed = !this.collapsed
    },
    setTheme(key) {
      this.currentTheme = key
      if (typeof localStorage !== 'undefined') localStorage.setItem('ia-bg-theme', key)
      this.themeOpen = false
    },
    closeTheme() {
      this.themeOpen = false
    },
    formatPhaseLabel(id) {
      const map = {
        p1_basics: 'P1 股市基础',
        p2_technical: 'P2 技术分析',
        p3_sectors: 'P3 板块产业链',
        p4_quant: 'P4 量化策略',
        p5_risk: 'P5 风险管理',
        p6_psychology: 'P6 交易心理',
        p7_integration: 'P7 实战整合',
      }
      return map[id] || id
    },
    formatLabLabel(id) {
      const map = {
        m1_data_lab: 'M1 数据勘探',
        m2_feature_lab: 'M2 特征工程',
      }
      return map[id] || id
    },
  },
}
</script>

<style>
/* Layout root */
#app-root {
  display: flex;
  min-height: 100vh;
  background: var(--ia-bg);
  color: var(--ia-text);
}

/* Sidebar */
.sidebar {
  width: var(--ia-sidebar-width);
  min-width: var(--ia-sidebar-width);
  height: 100vh;
  position: sticky;
  top: 0;
  background: var(--ia-surface-glass);
  border-right: 1px solid var(--ia-glass-border);
  display: flex;
  flex-direction: column;
  padding: 1.5rem 0;
  overflow-y: auto;
  transition: width 0.25s ease, min-width 0.25s ease, transform 0.25s ease;
  backdrop-filter: blur(var(--ia-glass-blur));
  -webkit-backdrop-filter: blur(var(--ia-glass-blur));
  box-shadow: var(--ia-shadow-inset), 4px 0 24px rgba(0, 0, 0, 0.18);
  z-index: 101;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0 1.2rem;
  margin-bottom: 1.5rem;
  position: relative;
}

.brand-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--ia-gold-soft);
  color: var(--ia-gold);
  border: 1px solid rgba(240, 185, 11, 0.18);
  flex-shrink: 0;
  box-shadow: 0 0 16px rgba(240, 185, 11, 0.10);
}

.brand-text {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--ia-text);
  letter-spacing: 0.03em;
  line-height: 1.2;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.brand-text span {
  display: block;
  font-size: 0.65rem;
  color: var(--ia-text-tertiary);
  letter-spacing: 0.08em;
  font-weight: 400;
}

.sidebar-toggle {
  position: absolute;
  right: -15px;
  top: 22px;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 2px solid var(--ia-gold);
  background: var(--ia-surface-elevated);
  color: var(--ia-gold);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--ia-transition-fast);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35), 0 0 16px rgba(240, 185, 11, 0.25);
  z-index: 102;
}

.sidebar-toggle:hover {
  background: var(--ia-gold);
  color: var(--ia-bg);
  transform: scale(1.08);
  box-shadow: 0 6px 22px rgba(0, 0, 0, 0.4), 0 0 22px rgba(240, 185, 11, 0.35);
}

.sidebar-toggle:active {
  transform: scale(0.96);
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0 0.9rem;
}

.nav-section {
  margin-bottom: 1.2rem;
}

.nav-section-title {
  font-size: 0.65rem;
  color: var(--ia-text-tertiary);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  padding: 0.6rem 0.5rem 0.4rem;
  pointer-events: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: var(--ia-radius-sm);
  font-size: 0.85rem;
  color: var(--ia-text-secondary);
  text-decoration: none;
  transition: all var(--ia-transition-fast);
  white-space: nowrap;
  overflow: hidden;
  border: 1px solid transparent;
  margin-bottom: 0.15rem;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.04);
  color: var(--ia-text);
  border-color: var(--ia-glass-border);
  transform: translateX(2px);
}

.nav-item--active {
  background: var(--ia-gold-soft);
  color: var(--ia-gold);
  border: 1px solid rgba(240, 185, 11, 0.22);
  box-shadow: 0 0 14px rgba(240, 185, 11, 0.08), var(--ia-shadow-inset);
  font-weight: 500;
}

.nav-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-count {
  font-size: 0.65rem;
  color: var(--ia-text-tertiary);
  flex-shrink: 0;
}

.nav-guide {
  color: var(--ia-text-tertiary);
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 1rem 1.2rem;
  border-top: 1px solid var(--ia-glass-border);
  display: flex;
  justify-content: center;
}

.api-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-size: 0.68rem;
  padding: 0.4rem 0.7rem;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--ia-glass-border);
  color: var(--ia-text-secondary);
  white-space: nowrap;
  transition: all var(--ia-transition-fast);
  cursor: default;
}

.api-dot {
  animation: ia-dot-pulse 2s infinite;
}

/* Main content */
.main-content {
  flex: 1;
  min-width: 0;
  position: relative;
}

/* Theme picker */
.theme-picker {
  position: fixed;
  top: 1.1rem;
  right: 1.1rem;
  z-index: 200;
}

.theme-picker__btn {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  border: 1px solid var(--ia-gold);
  background: var(--ia-surface-elevated);
  color: var(--ia-gold);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--ia-transition-fast);
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.32), 0 0 18px rgba(240, 185, 11, 0.18);
  backdrop-filter: blur(6px);
}

.theme-picker__btn:hover {
  background: var(--ia-gold);
  color: var(--ia-bg);
  transform: translateY(-2px) rotate(15deg);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35), 0 0 28px rgba(240, 185, 11, 0.30);
}

.theme-picker__btn:active {
  transform: scale(0.95);
}

.theme-picker__panel {
  position: absolute;
  top: calc(100% + 0.6rem);
  right: 0;
  min-width: 170px;
  padding: 0.7rem;
  background: var(--ia-surface-elevated);
  border: 1px solid var(--ia-border-strong);
  border-radius: var(--ia-radius);
  box-shadow: var(--ia-shadow-lg);
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  animation: ia-scale-in 0.25s var(--ia-transition-spring) forwards;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.55rem 0.8rem;
  border-radius: var(--ia-radius-sm);
  cursor: pointer;
  transition: all var(--ia-transition-fast);
}

.theme-option:hover {
  background: rgba(255, 255, 255, 0.05);
}

.theme-option.active {
  background: var(--ia-gold-soft);
  border: 1px solid rgba(240, 185, 11, 0.18);
}

.theme-swatch {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid var(--ia-glass-border);
  flex-shrink: 0;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
}

.theme-label {
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text);
  white-space: nowrap;
}

/* Mobile header */
.mobile-header {
  display: none;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--ia-surface-glass);
  border-bottom: 1px solid var(--ia-glass-border);
  backdrop-filter: blur(var(--ia-glass-blur));
  -webkit-backdrop-filter: blur(var(--ia-glass-blur));
  position: sticky;
  top: 0;
  z-index: 50;
}

.mobile-header__toggle {
  width: 34px;
  height: 34px;
  border-radius: var(--ia-radius-sm);
  border: 1px solid var(--ia-glass-border);
  background: transparent;
  color: var(--ia-text);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--ia-transition-fast);
}

.mobile-header__toggle:hover {
  border-color: var(--ia-gold);
  color: var(--ia-gold);
  background: var(--ia-gold-soft);
}

.mobile-header__title {
  font-weight: 600;
  color: var(--ia-text);
  letter-spacing: 0.03em;
}

/* Collapsed sidebar state */
.sidebar-collapsed .sidebar {
  width: var(--ia-sidebar-collapsed-width);
  min-width: var(--ia-sidebar-collapsed-width);
}

.sidebar-collapsed .brand-text,
.sidebar-collapsed .nav-section-title,
.sidebar-collapsed .nav-label,
.sidebar-collapsed .nav-count,
.sidebar-collapsed .nav-guide,
.sidebar-collapsed .api-badge-text {
  display: none;
}

.sidebar-collapsed .brand-icon {
  margin: 0 auto;
}

.sidebar-collapsed .nav-item {
  justify-content: center;
  padding: 0.75rem;
}

.sidebar-collapsed .api-badge {
  padding: 0.5rem;
  border-radius: 50%;
}

.sidebar-collapsed .api-badge .api-dot {
  margin: 0;
}

.sidebar-collapsed .sidebar-brand {
  justify-content: center;
  padding: 0 0.6rem;
  gap: 0.4rem;
  flex-direction: column;
}

.sidebar-collapsed .sidebar-toggle {
  position: static;
  width: 34px;
  height: 34px;
  margin: 0.6rem auto 0;
}

.sidebar-collapsed .sidebar-footer {
  padding: 1rem 0.6rem;
}

/* Mobile overlay */
.mobile-overlay {
  display: none;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    z-index: 100;
    transform: translateX(-100%);
  }
  .sidebar-mobile-open .sidebar {
    transform: translateX(0);
  }
  .sidebar-mobile-open .mobile-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.65);
    backdrop-filter: blur(4px);
    z-index: 99;
  }
  .main-content {
    width: 100%;
  }
  .mobile-header {
    display: flex;
  }
  .sidebar-toggle {
    display: none;
  }
  .theme-picker {
    top: 0.6rem;
    right: 0.6rem;
  }
  .theme-picker__btn {
    width: 40px;
    height: 40px;
  }
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--ia-bg); }
::-webkit-scrollbar-thumb { background: rgba(240, 185, 11, 0.25); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(240, 185, 11, 0.4); }

/* Global typography overrides */
h1, h2, h3, h4 {
  color: var(--ia-text);
  letter-spacing: 0.02em;
  font-weight: 500;
}

p {
  line-height: 1.8;
  color: var(--ia-text-secondary);
}

a { color: var(--ia-gold); text-decoration: none; }

/* Page transitions */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.page-enter {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* View transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter, .fade-leave-to { opacity: 0; }
</style>
