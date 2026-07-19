<template>
  <div class="home ia-page">
    <IAPageHeader
      title="投资学院"
      title-highlight="Investment Academy"
      subtitle="基于真实 A 股 ETF 数据 · 理论实战双轨并行 · 完全本地运行"
      :breadcrumbs="[{ label: '首页' }]"
    />

    <div class="theme-picker">
      <button class="theme-picker__btn" @click="themeOpen = !themeOpen" title="切换背景色">
        <IAIcon name="palette" size="md" />
      </button>
      <transition name="fade">
        <div v-if="themeOpen" class="theme-picker__panel">
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

    <div class="ia-metric-grid">
      <IAMetricCard label="已完成章节" :value="progressStats.completed" unit="章" trend="up" />
      <IAMetricCard label="课程章节" :value="progressStats.total" unit="章" />
      <IAMetricCard label="学习进度" :value="progressStats.pct" unit="%" trend="up" />
      <IAMetricCard label="可用 ETF" :value="etfCount" unit="只" />
    </div>

    <div class="ia-divider"></div>

    <IASectionTitle icon="book" title="知识轨道" subtitle="系统学习投资理论，从基础概念到完整交易系统" />
    <div class="card-grid">
      <router-link
        v-for="p in phases" :key="p.id"
        :to="`/knowledge/${p.id}`"
        class="track-card"
      >
        <div class="track-num">{{ formatPhaseId(p.id) }}</div>
        <div class="track-name">{{ formatPhaseLabel(p.id) }}</div>
        <div class="track-desc">{{ formatPhaseDesc(p.id) }}</div>
        <div class="track-meta">
          <IABadge variant="neutral">{{ p.chapter_count }} 章</IABadge>
          <IABadge v-if="p.has_quiz" variant="gold">含测验</IABadge>
        </div>
      </router-link>
    </div>

    <div class="ia-divider"></div>

    <IASectionTitle icon="lab" title="实践轨道" subtitle="动手操作，用真实市场数据检验你的理解" />
    <div class="card-grid">
      <router-link
        v-for="lab in labs" :key="lab.id"
        :to="`/practice/${lab.id}`"
        class="track-card"
      >
        <div class="track-num">{{ formatLabId(lab.id) }}</div>
        <div class="track-name">{{ formatLabLabel(lab.id) }}</div>
        <div class="track-desc">{{ formatLabDesc(lab.id) }}</div>
        <div class="track-meta">
          <IABadge v-if="lab.has_guide" variant="green">实验指南</IABadge>
          <IABadge variant="neutral">可实验</IABadge>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script>
import { IAPageHeader, IAMetricCard, IASectionTitle, IABadge, IAIcon } from '../components/ui'
import { getPhases, getLabs } from '../api/content'
import { getProgress } from '../api/progress'
import { getETFs } from '../api/market'

export default {
  name: 'Home',
  components: { IAPageHeader, IAMetricCard, IASectionTitle, IABadge, IAIcon },
  data() {
    return {
      phases: [],
      labs: [],
      progressStats: { completed: 0, total: 34, pct: 0 },
      etfCount: 0,
      themeOpen: false,
      currentTheme: 'dark',
      themes: [
        { key: 'dark', label: '深邃黑', color: '#08080C' },
        { key: 'navy', label: '暗夜蓝', color: '#0A0F1C' },
        { key: 'graphite', label: '石墨灰', color: '#121212' },
        { key: 'plum', label: '暗梅紫', color: '#150C18' },
        { key: 'ink', label: '墨蓝黑', color: '#0C0A0F' },
      ],
    }
  },
  async created() {
    try {
      const saved = typeof localStorage !== 'undefined' ? localStorage.getItem('ia-bg-theme') : 'dark'
      this.currentTheme = saved || 'dark'
      const [phasesRes, labsRes, progressRes, etfsRes] = await Promise.all([
        getPhases(), getLabs(), getProgress(), getETFs(),
      ])
      this.phases = phasesRes.data || []
      this.labs = labsRes.data || []
      this.etfCount = (etfsRes.data || []).length

      const progress = progressRes.data || []
      const completed = progress.filter(p => p.completed).length
      this.progressStats.completed = completed
      this.progressStats.pct = Math.round((completed / 34) * 100)
    } catch (e) {
      console.error('首页加载失败:', e)
    }
  },
  methods: {
    setTheme(key) {
      window.dispatchEvent(new CustomEvent('ia-bg-theme', { detail: key }))
      this.currentTheme = key
      this.themeOpen = false
    },
    formatPhaseId(id) { return (id.match(/p(\d+)/) || [])[0]?.toUpperCase() || id },
    formatPhaseLabel(id) {
      const map = {
        p1_basics: '股市基础', p2_technical: '技术分析入门',
        p3_sectors: '板块与产业链', p4_quant: '量化策略思维',
        p5_risk: '风险管理', p6_psychology: '交易心理与情绪',
        p7_integration: '实战整合',
      }
      return map[id] || id
    },
    formatPhaseDesc(id) {
      const map = {
        p1_basics: '股票是什么、ETF入门、K线图、基本术语',
        p2_technical: '趋势判断、K线微观结构、均线、Wyckoff理论',
        p3_sectors: '行业分类、产业链、板块轮动、ETF实战',
        p4_quant: '概率思维、规则策略、特征工程、ML应用',
        p5_risk: '仓位管理、回撤控制、波动率适应、尾部风险',
        p6_psychology: '自我认知、情绪管理、认知偏差、复盘体系',
        p7_integration: '回测验证、前视偏差、期望值、完整系统',
      }
      return map[id] || ''
    },
    formatLabId(id) { return (id.match(/m(\d+)/) || [])[0]?.toUpperCase() || id },
    formatLabLabel(id) {
      const map = { m1_data_lab: '数据勘探实验室', m2_feature_lab: '特征工程实验室' }
      return map[id] || id
    },
    formatLabDesc(id) {
      const map = {
        m1_data_lab: '浏览真实ETF数据、查看K线图、对比走势',
        m2_feature_lab: '调节参数观察特征变化、识别H2/L2形态',
      }
      return map[id] || ''
    },
  },
}
</script>

<style scoped>
.home {
  padding-top: var(--ia-space-md);
  position: relative;
}

.theme-picker {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 200;
}

.theme-picker__btn {
  width: 42px;
  height: 42px;
  border-radius: var(--ia-radius);
  border: 1px solid rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.10);
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--ia-transition-fast);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(240, 185, 11, 0.08);
  backdrop-filter: blur(4px);
}

.theme-picker__btn:hover {
  border-color: var(--ia-gold);
  color: var(--ia-gold);
  background: var(--ia-gold-soft);
  box-shadow: 0 0 16px rgba(240, 185, 11, 0.35), 0 2px 10px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.theme-picker__btn:active {
  transform: scale(0.95);
}

.theme-picker__panel {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  min-width: 150px;
  padding: 0.6rem;
  background: var(--ia-surface-elevated);
  border: 1px solid var(--ia-border-strong);
  border-radius: var(--ia-radius);
  box-shadow: var(--ia-shadow-lg);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.7rem;
  border-radius: var(--ia-radius-xs);
  cursor: pointer;
  transition: all var(--ia-transition-fast);
}

.theme-option:hover {
  background: rgba(255, 255, 255, 0.05);
}

.theme-option.active {
  background: var(--ia-gold-soft);
}

.theme-swatch {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1px solid var(--ia-glass-border);
  flex-shrink: 0;
}

.theme-label {
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text);
  white-space: nowrap;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--ia-space-md);
}

.track-card {
  background: var(--ia-surface-glass);
  border: 1px solid var(--ia-glass-border);
  border-radius: var(--ia-radius);
  padding: var(--ia-space-lg);
  cursor: pointer;
  transition: all var(--ia-transition-base);
  text-decoration: none;
  display: flex;
  flex-direction: column;
  min-height: 160px;
  backdrop-filter: blur(var(--ia-glass-blur));
  -webkit-backdrop-filter: blur(var(--ia-glass-blur));
  box-shadow: var(--ia-shadow-sm);
}

.track-card:hover {
  border-color: var(--ia-gold);
  box-shadow: var(--ia-shadow-gold);
  transform: translateY(-4px);
}

.track-num {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-gold);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-bottom: var(--ia-space-sm);
  font-weight: 600;
  text-shadow: 0 0 10px rgba(240, 185, 11, 0.15);
}

.track-name {
  font-size: var(--ia-font-size-lg);
  color: var(--ia-text);
  font-weight: 500;
  margin-bottom: var(--ia-space-sm);
}

.track-desc {
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text-secondary);
  line-height: 1.6;
  margin-bottom: var(--ia-space-md);
  flex: 1;
}

.track-meta {
  display: flex;
  gap: var(--ia-space-sm);
  align-items: center;
  flex-wrap: wrap;
}

@media (max-width: 640px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
