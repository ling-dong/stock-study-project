<template>
  <div id="app-root" :class="{ 'sidebar-collapsed': collapsed, 'sidebar-mobile-open': !collapsed && isMobile }" :style="rootStyle">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">
          <IAIcon name="activity" size="xl" />
        </div>
        <div class="brand-text">
          投资学院
          <span>Investment Academy</span>
        </div>
        <button class="sidebar-toggle" @click="toggleSidebar" :title="collapsed ? '展开侧边栏' : '收起侧边栏'">
          <IAIcon :name="collapsed ? 'chevron-right' : 'chevron-left'" size="md" />
        </button>
      </div>

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
  data() {
    const savedTheme = typeof localStorage !== 'undefined' ? localStorage.getItem('ia-bg-theme') : 'dark'
    return {
      phases: [],
      labs: [],
      apiOk: false,
      collapsed: false,
      isMobile: false,
      bgTheme: savedTheme || 'dark',
      bgThemes: {
        dark: '#08080C',
        navy: '#0A0F1C',
        graphite: '#121212',
        plum: '#150C18',
        ink: '#0C0A0F',
      },
    }
  },
  computed: {
    rootStyle() {
      return { '--ia-bg': this.bgThemes[this.bgTheme] || this.bgThemes.dark }
    },
  },
  async created() {
    this.checkMobile()
    window.addEventListener('resize', this.checkMobile)
    window.addEventListener('ia-bg-theme', this.onBgTheme)
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
    window.removeEventListener('ia-bg-theme', this.onBgTheme)
  },
  methods: {
    checkMobile() {
      this.isMobile = window.innerWidth <= 768
    },
    toggleSidebar() {
      this.collapsed = !this.collapsed
    },
    onBgTheme(e) {
      const t = e.detail
      if (this.bgThemes[t]) {
        this.bgTheme = t
        if (typeof localStorage !== 'undefined') localStorage.setItem('ia-bg-theme', t)
      }
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
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--ia-gold-soft);
  color: var(--ia-gold);
  border: 1px solid rgba(240, 185, 11, 0.15);
  flex-shrink: 0;
  box-shadow: 0 0 12px rgba(240, 185, 11, 0.08);
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
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.10);
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--ia-transition-fast);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(240, 185, 11, 0.08);
  backdrop-filter: blur(4px);
}

.sidebar-toggle:hover {
  color: #ffffff;
  border-color: var(--ia-gold);
  background: var(--ia-gold-soft);
  box-shadow: 0 0 14px rgba(240, 185, 11, 0.35), 0 2px 8px rgba(0, 0, 0, 0.2);
  transform: translateX(-1px);
}

.sidebar-toggle:active {
  transform: scale(0.95);
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
  padding: 0.55rem 0.7rem;
  border-radius: var(--ia-radius-xs);
  font-size: 0.85rem;
  color: var(--ia-text-secondary);
  text-decoration: none;
  transition: all var(--ia-transition-fast);
  white-space: nowrap;
  overflow: hidden;
  border: 1px solid transparent;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.04);
  color: var(--ia-text);
  border-color: var(--ia-glass-border);
}

.nav-item--active {
  background: var(--ia-gold-soft);
  color: var(--ia-gold);
  border: 1px solid rgba(240, 185, 11, 0.18);
  box-shadow: 0 0 12px rgba(240, 185, 11, 0.06);
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
  border-radius: var(--ia-radius-xs);
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
  padding: 0.65rem;
}

.sidebar-collapsed .api-badge {
  padding: 0.5rem;
  border-radius: 50%;
}

.sidebar-collapsed .sidebar-brand {
  justify-content: center;
  padding: 0 0.6rem;
  gap: 0.4rem;
  flex-direction: column;
}

.sidebar-collapsed .sidebar-toggle {
  width: 30px;
  height: 30px;
  margin: 0.4rem auto 0;
  border: 1px solid rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.10);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(240, 185, 11, 0.08);
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
