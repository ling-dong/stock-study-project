<template>
  <div id="app-root" :class="{ 'sidebar-collapsed': collapsed }">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">
          <IAIcon name="activity" size="xl" />
        </div>
        <div class="brand-text">
          投资学院
          <span>Investment Academy</span>
        </div>
        <button class="sidebar-toggle" @click="collapsed = !collapsed" title="收起/展开">
          <IAIcon name="menu" size="md" />
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
        <div class="api-badge" :class="apiOk ? 'ia-badge--green' : 'ia-badge--red'">
          <IAIcon name="dot" size="xs" />
          {{ apiOk ? 'API 已连接' : 'API 未连接' }}
        </div>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import { IAIcon } from './components/ui'
import { getPhases, getLabs } from './api/content'
import { healthCheck } from './api/index'

export default {
  name: 'App',
  components: { IAIcon },
  data() {
    return {
      phases: [],
      labs: [],
      apiOk: false,
      collapsed: false,
    }
  },
  async created() {
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
  methods: {
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
  background-image: radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 28px 28px;
}

/* Sidebar */
.sidebar {
  width: var(--ia-sidebar-width);
  min-width: var(--ia-sidebar-width);
  height: 100vh;
  position: sticky;
  top: 0;
  background: var(--ia-surface);
  border-right: 1px solid var(--ia-border);
  display: flex;
  flex-direction: column;
  padding: 1.5rem 0;
  overflow-y: auto;
  transition: width 0.25s ease, min-width 0.25s ease;
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
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid var(--ia-border);
  background: transparent;
  color: var(--ia-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sidebar-toggle:hover {
  color: var(--ia-gold);
  border-color: var(--ia-gold);
  background: var(--ia-gold-soft);
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
  transition: all 0.2s;
  white-space: nowrap;
  overflow: hidden;
}

.nav-item:hover {
  background: var(--ia-surface-hover);
  color: var(--ia-text);
}

.nav-item--active {
  background: var(--ia-gold-soft);
  color: var(--ia-gold);
  border: 1px solid rgba(240, 185, 11, 0.15);
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
  border-top: 1px solid var(--ia-border);
}

.api-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-size: 0.68rem;
  padding: 0.4rem 0.6rem;
  border-radius: 20px;
  background: var(--ia-surface-elevated);
  border: 1px solid var(--ia-border);
  color: var(--ia-text-secondary);
  white-space: nowrap;
}

.api-badge svg {
  color: currentColor;
}

/* Main content */
.main-content {
  flex: 1;
  min-width: 0;
}

/* Collapsed sidebar state */
.sidebar-collapsed .sidebar {
  width: 72px;
  min-width: 72px;
}

.sidebar-collapsed .brand-text,
.sidebar-collapsed .nav-section-title,
.sidebar-collapsed .nav-label,
.sidebar-collapsed .nav-count,
.sidebar-collapsed .nav-guide,
.sidebar-collapsed .api-badge span {
  display: none;
}

.sidebar-collapsed .brand-icon {
  margin: 0 auto;
}

.sidebar-collapsed .sidebar-toggle {
  display: none;
}

.sidebar-collapsed .nav-item {
  justify-content: center;
}

.sidebar-collapsed .api-badge {
  padding: 0.5rem;
}

.sidebar-collapsed .sidebar-brand {
  justify-content: center;
  padding: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    z-index: 100;
    transform: translateX(0);
  }
  .sidebar-collapsed .sidebar {
    transform: translateX(-100%);
  }
  #app-root:not(.sidebar-collapsed)::after {
    content: '';
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    z-index: 99;
  }
  .main-content {
    padding-top: 0;
  }
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--ia-bg); }
::-webkit-scrollbar-thumb { background: rgba(240, 185, 11, 0.2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(240, 185, 11, 0.35); }

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

/* View transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter, .fade-leave-to { opacity: 0; }
</style>
