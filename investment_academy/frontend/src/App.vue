<template>
  <div id="app-root">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">📈</div>
        <div class="brand-text">投资学院</div>
        <div class="brand-sub">Investment Academy</div>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/" class="nav-section-title">
          🏠 首页
        </router-link>

        <div class="nav-section-title">📚 知识轨道</div>
        <router-link
          v-for="p in phases" :key="p.id"
          :to="`/knowledge/${p.id}`"
          class="nav-item"
          active-class="nav-item--active"
        >
          <span class="nav-label">{{ formatPhaseLabel(p.id) }}</span>
          <span class="nav-count">{{ p.chapter_count }}章</span>
        </router-link>

        <div class="nav-section-title">🔬 实践轨道</div>
        <router-link
          v-for="lab in labs" :key="lab.id"
          :to="`/practice/${lab.id}`"
          class="nav-item"
          active-class="nav-item--active"
        >
          <span class="nav-label">{{ formatLabLabel(lab.id) }}</span>
          <span class="nav-status" v-if="lab.has_guide">📖</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="api-badge" :class="{ 'api-ok': apiOk }">
          {{ apiOk ? '🟢 API 已连接' : '🔴 API 未连接' }}
        </div>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import { getPhases, getLabs } from './api/content'
import { healthCheck } from './api/index'

export default {
  name: 'App',
  data() {
    return {
      phases: [],
      labs: [],
      apiOk: false,
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
      this.phases = (await getPhases()).data || []
      this.labs = (await getLabs()).data || []
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
/* === Layout === */
#app-root {
  display: flex;
  min-height: 100vh;
  background: #0A0A0B;
  background-image: radial-gradient(circle, #1A1A1D 1px, transparent 1px);
  background-size: 24px 24px;
}

/* === Sidebar === */
.sidebar {
  width: 240px;
  min-width: 240px;
  background: #050506;
  border-right: 1px solid #151518;
  display: flex;
  flex-direction: column;
  padding: 1.5rem 0;
}

.sidebar-brand {
  padding: 0 1.2rem;
  margin-bottom: 1.5rem;
}

.brand-icon {
  font-size: 1.6rem;
  margin-bottom: 0.3rem;
}

.brand-text {
  font-size: 1.15rem;
  font-weight: 400;
  color: #F5F0E0;
  letter-spacing: 0.05em;
}

.brand-sub {
  font-size: 0.65rem;
  color: #4A4A55;
  letter-spacing: 0.1em;
  margin-top: 0.15rem;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0 0.8rem;
}

.nav-section-title {
  display: block;
  font-size: 0.65rem;
  color: #6B6B7B;
  letter-spacing: 0.15em;
  padding: 0.8rem 0.5rem 0.3rem;
  text-decoration: none;
  text-transform: uppercase;
}

.nav-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.45rem 0.6rem;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #A0A0A8;
  text-decoration: none;
  transition: all 0.2s;
}

.nav-item:hover {
  background: #141417;
  color: #E8E6E3;
}

.nav-item--active {
  background: #F0B90B15;
  color: #F0B90B;
  border: 1px solid #F0B90B22;
}

.nav-count {
  font-size: 0.68rem;
  color: #4A4A55;
}

.nav-status {
  font-size: 0.7rem;
}

.sidebar-footer {
  padding: 1rem 1.2rem;
  border-top: 1px solid #151518;
}

.api-badge {
  font-size: 0.68rem;
  color: #6B6B7B;
  padding: 0.35rem 0.6rem;
  border-radius: 4px;
  background: #0D0D10;
  border: 1px solid #151518;
}

/* === Main === */
.main-content {
  flex: 1;
  padding: 2rem 2.5rem;
  max-width: 1100px;
  overflow-y: auto;
}

/* === Typography === */
h1, h2, h3 {
  color: #F5F0E0;
  letter-spacing: 0.03em;
  font-weight: 300;
}

h1 { font-size: 1.8rem; }
h2 { font-size: 1.3rem; margin-top: 2rem; margin-bottom: 0.8rem; }
h3 { font-size: 1.05rem; margin-top: 1.5rem; }

p {
  line-height: 1.8;
  margin-bottom: 0.8rem;
  color: #C8C6C3;
}

a {
  color: #F0B90B;
  text-decoration: none;
}

/* === Utility === */
.divider {
  height: 1px;
  background: linear-gradient(to right, #F0B90B44, transparent);
  margin: 2rem 0;
}

.card {
  background: #0D0D10;
  border: 1px solid #151518;
  border-radius: 10px;
  padding: 1.5rem;
  transition: border-color 0.3s;
}

.card:hover {
  border-color: #F0B90B33;
}
</style>
