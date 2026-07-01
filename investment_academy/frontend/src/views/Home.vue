<template>
  <div class="home">
    <div class="hero">
      <div class="hero-eyebrow">INVESTMENT ACADEMY</div>
      <h1 class="hero-title">从零基础<br>到投资大拿</h1>
      <p class="hero-sub">
        基于真实 A 股 ETF 数据 · 理论实战双轨并行 · 完全本地运行
      </p>
    </div>

    <div class="metrics-row">
      <div class="m-card">
        <div class="m-value">{{ progressStats.completed }}</div>
        <div class="m-label">已完成章节</div>
      </div>
      <div class="m-card">
        <div class="m-value">{{ progressStats.total }}</div>
        <div class="m-label">课程章节</div>
      </div>
      <div class="m-card">
        <div class="m-value">{{ progressStats.pct }}%</div>
        <div class="m-label">学习进度</div>
      </div>
      <div class="m-card">
        <div class="m-value">{{ etfCount }}</div>
        <div class="m-label">可用 ETF</div>
      </div>
    </div>

    <div class="divider"></div>

    <div class="section-hd">
      <h2>📚 知识轨道</h2>
      <p>系统学习投资理论，从基础概念到完整交易系统</p>
    </div>

    <div class="card-grid">
      <router-link
        v-for="p in phases" :key="p.id"
        :to="`/knowledge/${p.id}`"
        class="p-card"
      >
        <div class="p-num">{{ formatPhaseId(p.id) }}</div>
        <div class="p-name">{{ formatPhaseLabel(p.id) }}</div>
        <div class="p-desc">{{ formatPhaseDesc(p.id) }}</div>
        <div class="p-meta">
          <span class="p-count">{{ p.chapter_count }} 章{{ p.has_quiz ? ' + 测验' : '' }}</span>
          <span class="p-badge p-badge--ready">可学习</span>
        </div>
      </router-link>
    </div>

    <div class="divider"></div>

    <div class="section-hd">
      <h2>🔬 实践轨道</h2>
      <p>动手操作，用真实市场数据检验你的理解</p>
    </div>

    <div class="card-grid">
      <router-link
        v-for="lab in labs" :key="lab.id"
        :to="`/practice/${lab.id}`"
        class="p-card"
      >
        <div class="p-num">{{ formatLabId(lab.id) }}</div>
        <div class="p-name">{{ formatLabLabel(lab.id) }}</div>
        <div class="p-desc">{{ formatLabDesc(lab.id) }}</div>
        <div class="p-meta">
          <span class="p-count">{{ lab.has_guide ? '📖 实验指南' : '' }}</span>
          <span class="p-badge p-badge--ready">可实验</span>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script>
import { getPhases, getLabs } from '../api/content'
import { getProgress } from '../api/progress'
import { getETFs } from '../api/market'

export default {
  name: 'Home',
  data() {
    return {
      phases: [],
      labs: [],
      progressStats: { completed: 0, total: 34, pct: 0 },
      etfCount: 0,
    }
  },
  async created() {
    try {
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
    formatPhaseId(id) { return (id.match(/p(\d+)/) || [])[0]?.toUpperCase() || id; },
    formatPhaseLabel(id) {
      const map = {
        p1_basics: '股市基础',
        p2_technical: '技术分析入门',
        p3_sectors: '板块与产业链',
        p4_quant: '量化策略思维',
        p5_risk: '风险管理',
        p6_psychology: '交易心理与情绪',
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
    formatLabId(id) { return (id.match(/m(\d+)/) || [])[0]?.toUpperCase() || id; },
    formatLabLabel(id) {
      const map = {
        m1_data_lab: '数据勘探实验室',
        m2_feature_lab: '特征工程实验室',
      }
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
.hero {
  margin: 1rem 0 2.5rem;
}

.hero-eyebrow {
  font-size: 0.65rem;
  letter-spacing: 0.3em;
  color: #6B6B7B;
  margin-bottom: 0.5rem;
}

.hero-title {
  font-size: 2.8rem;
  font-weight: 200;
  color: #F5F0E0;
  line-height: 1.15;
  margin-bottom: 0.5rem;
}

.hero-sub {
  font-size: 0.95rem;
  color: #6B6B7B;
  max-width: 480px;
}

.metrics-row {
  display: flex;
  gap: 1.2rem;
  margin: 1.5rem 0;
}

.m-card {
  flex: 1;
  background: #0D0D10;
  border: 1px solid #1A1A1D;
  border-radius: 10px;
  padding: 1.3rem;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.m-card:hover {
  border-color: #F0B90B33;
  box-shadow: 0 0 20px #F0B90B08;
}

.m-value {
  font-size: 2rem;
  font-weight: 300;
  color: #F5F0E0;
  margin-bottom: 0.2rem;
}

.m-label {
  font-size: 0.75rem;
  color: #6B6B7B;
  letter-spacing: 0.08em;
}

.section-hd {
  margin-bottom: 1.2rem;
}

.section-hd h2 {
  font-size: 1.3rem;
  margin-bottom: 0.2rem;
}

.section-hd p {
  font-size: 0.82rem;
  color: #6B6B7B;
  margin: 0;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0.9rem;
}

.p-card {
  background: #0D0D10;
  border: 1px solid #151518;
  border-radius: 10px;
  padding: 1.3rem;
  cursor: pointer;
  transition: all 0.25s;
  text-decoration: none;
  display: block;
}

.p-card:hover {
  border-color: #F0B90B44;
  box-shadow: 0 0 24px #F0B90B06;
  transform: translateY(-2px);
}

.p-num {
  font-size: 0.65rem;
  color: #F0B90B;
  letter-spacing: 0.15em;
  margin-bottom: 0.4rem;
}

.p-name {
  font-size: 1.05rem;
  font-weight: 400;
  color: #F5F0E0;
  margin-bottom: 0.3rem;
}

.p-desc {
  font-size: 0.78rem;
  color: #6B6B7B;
  margin-bottom: 0.8rem;
  line-height: 1.5;
}

.p-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.p-count {
  font-size: 0.72rem;
  color: #4A4A55;
}

.p-badge {
  font-size: 0.68rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  letter-spacing: 0.05em;
}

.p-badge--ready {
  background: #0A2E0A;
  color: #4ADE80;
  border: 1px solid #166534;
}
</style>
