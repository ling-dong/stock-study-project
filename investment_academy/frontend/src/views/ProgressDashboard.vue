<template>
  <div class="dashboard-page ia-page">
    <IAPageHeader
      title="学习进度仪表盘"
      subtitle="追踪你的学习旅程"
      :breadcrumbs="[{ label: '首页', to: '/' }, { label: '学习进度' }]"
    />

    <div class="ia-metric-grid">
      <IAMetricCard label="已完成章节" :value="completedCount" :unit="`/${totalCount}`" trend="up" />
      <IAMetricCard label="总体进度" :value="overallPct" unit="%" trend="up" />
      <IAMetricCard label="测验均分" :value="avgScore" unit="分" />
      <IAMetricCard label="测验次数" :value="totalAttempts" />
    </div>

    <IAPanel title="总体进度" icon="chart">
      <ProgressBar :value="completedCount" :max="totalCount" :label="completedCount + ' / ' + totalCount + ' 章'" />
    </IAPanel>

    <IASectionTitle icon="book" title="知识轨道" />
    <div class="phase-grid">
      <div v-for="phase in phases" :key="phase.id" class="ia-card phase-card">
        <div class="phase-hd">
          <span class="phase-label">{{ formatPhase(phase.id) }}</span>
          <IABadge :variant="phaseDone(phase.id) === phase.total ? 'green' : 'neutral'">
            {{ phaseDone(phase.id) }}/{{ phase.total }} 章
          </IABadge>
        </div>
        <ProgressBar :value="phaseDone(phase.id)" :max="phase.total" color="gold" />
        <div class="chapter-list">
          <div
            v-for="ch in phase.chapters" :key="ch.id"
            class="chapter-row"
            :class="{ 'chapter-done': ch.completed }"
          >
            <IAIcon :name="ch.completed ? 'check' : 'book'" size="sm" />
            <span class="ch-name">{{ ch.title }}</span>
            <span class="ch-score" v-if="ch.quiz_score > 0">{{ (ch.quiz_score * 100).toFixed(0) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <IASectionTitle icon="lab" title="实践轨道" />
    <div class="phase-grid">
      <div v-for="lab in labs" :key="lab.id" class="ia-card phase-card">
        <div class="phase-hd">
          <span class="phase-label">{{ formatLab(lab.id) }}</span>
          <IABadge :variant="labDone(lab.id) ? 'green' : 'neutral'">
            {{ labDone(lab.id) ? '完成' : '待完成' }}
          </IABadge>
        </div>
        <p class="lab-desc-text">{{ labDesc(lab.id) }}</p>
      </div>
    </div>

    <IASectionTitle icon="clock" title="最近活动" />
    <div v-if="recentActivity.length" class="timeline">
      <div v-for="item in recentActivity" :key="item.chapter_id" class="timeline-item">
        <span class="tl-dot"></span>
        <div>
          <span class="tl-title">{{ item.chapter_id }}</span>
          <span class="tl-time">{{ item.last_accessed || '未知时间' }}</span>
          <span class="tl-score" v-if="item.quiz_score > 0">测验 {{ (item.quiz_score * 100).toFixed(0) }}%</span>
        </div>
      </div>
    </div>
    <div v-else class="ia-empty">暂无学习记录</div>
  </div>
</template>

<script>
import { IAPageHeader, IAMetricCard, IASectionTitle, IAPanel, IABadge, IAIcon } from '../components/ui'
import { getProgress } from '../api/progress'
import { getLabs } from '../api/content'
import ProgressBar from '../components/ProgressBar.vue'

const PHASE_DEFS = {
  p1_basics: { chapters: [
    { id: 'p1_ch1', title: 'Ch1: 什么是股票？' }, { id: 'p1_ch2', title: 'Ch2: ETF 入门' },
    { id: 'p1_ch3', title: 'Ch3: A股交易规则' }, { id: 'p1_ch4', title: 'Ch4: K线图入门' },
    { id: 'p1_ch5', title: 'Ch5: 基本术语' },
  ]},
  p2_technical: { chapters: [
    { id: 'p2_ch1', title: 'Ch1: 趋势判断' }, { id: 'p2_ch2', title: 'Ch2: K线微观结构' },
    { id: 'p2_ch3', title: 'Ch3: 均线与ADX' }, { id: 'p2_ch4', title: 'Ch4: Wyckoff理论' },
    { id: 'p2_ch5', title: 'Ch5: 多时间框架' }, { id: 'p2_ch6', title: 'Ch6: Al Brooks 价格行为' },
  ]},
  p3_sectors: { chapters: [
    { id: 'p3_ch1', title: 'Ch1: 行业分类' }, { id: 'p3_ch2', title: 'Ch2: 产业链分析' },
    { id: 'p3_ch3', title: 'Ch3: 板块轮动' }, { id: 'p3_ch4', title: 'Ch4: ETF 实战' },
  ]},
  p4_quant: { chapters: [
    { id: 'p4_ch1', title: 'Ch1: 概率思维' }, { id: 'p4_ch2', title: 'Ch2: 规则策略' },
    { id: 'p4_ch3', title: 'Ch3: 特征工程' }, { id: 'p4_ch4', title: 'Ch4: ML 应用' },
    { id: 'p4_ch5', title: 'Ch5: 融合决策' },
  ]},
  p5_risk: { chapters: [
    { id: 'p5_ch1', title: 'Ch1: 仓位管理' }, { id: 'p5_ch2', title: 'Ch2: 回撤控制' },
    { id: 'p5_ch3', title: 'Ch3: 波动率适应' }, { id: 'p5_ch4', title: 'Ch4: 尾部风险' },
    { id: 'p5_ch5', title: 'Ch5: 流动性管理' },
  ]},
  p6_psychology: { chapters: [
    { id: 'p6_ch1', title: 'Ch1: 自我认知' }, { id: 'p6_ch2', title: 'Ch2: 情绪管理' },
    { id: 'p6_ch3', title: 'Ch3: 认知偏差' }, { id: 'p6_ch4', title: 'Ch4: 纪律规则' },
    { id: 'p6_ch5', title: 'Ch5: 市场情绪' }, { id: 'p6_ch6', title: 'Ch6: 交易日志' },
  ]},
  p7_integration: { chapters: [
    { id: 'p7_ch1', title: 'Ch1: 回测验证' }, { id: 'p7_ch2', title: 'Ch2: 前视偏差' },
    { id: 'p7_ch3', title: 'Ch3: 期望值计算' }, { id: 'p7_ch4', title: 'Ch4: 完整系统' },
  ]},
}

const LAB_DEFS = {
  m1_data_lab: { desc: '浏览ETF数据、对比走势、认识数据质量' },
  m2_feature_lab: { desc: '调节参数看特征变化、识别H2/L2形态' },
}

export default {
  name: 'ProgressDashboard',
  components: { IAPageHeader, IAMetricCard, IASectionTitle, IAPanel, IABadge, IAIcon, ProgressBar },
  data() {
    return {
      progress: [],
      labs: [],
    }
  },
  computed: {
    progressMap() {
      const map = {}
      this.progress.forEach(p => { map[p.chapter_id] = p })
      return map
    },
    totalCount() { return 34 },
    completedCount() { return this.progress.filter(p => p.completed).length },
    overallPct() { return Math.round((this.completedCount / this.totalCount) * 100) },
    avgScore() {
      const scored = this.progress.filter(p => p.quiz_score > 0)
      if (!scored.length) return 0
      return (scored.reduce((s, p) => s + p.quiz_score, 0) / scored.length * 100).toFixed(0)
    },
    totalAttempts() { return this.progress.reduce((s, p) => s + (p.quiz_attempts || 0), 0) },
    phases() {
      return Object.entries(PHASE_DEFS).map(([id, def]) => {
        const chapters = def.chapters.map(ch => ({
          ...ch,
          completed: !!(this.progressMap[ch.id]?.completed),
          quiz_score: this.progressMap[ch.id]?.quiz_score || 0,
        }))
        return { id, chapters, total: chapters.length }
      })
    },
    recentActivity() {
      return this.progress
        .filter(p => p.last_accessed)
        .sort((a, b) => (b.last_accessed || '').localeCompare(a.last_accessed || ''))
        .slice(0, 10)
    },
  },
  async created() {
    try {
      const [pRes, lRes] = await Promise.all([getProgress(), getLabs()])
      this.progress = pRes.data || []
      this.labs = lRes.data || []
    } catch (e) {
      console.error('加载进度失败:', e)
    }
  },
  methods: {
    phaseDone(phaseId) {
      const def = PHASE_DEFS[phaseId]
      if (!def) return 0
      return def.chapters.filter(ch => this.progressMap[ch.id]?.completed).length
    },
    labDone(labId) { return !!(this.progressMap[labId]?.completed) },
    formatPhase(id) {
      const map = {
        p1_basics: 'P1 股市基础', p2_technical: 'P2 技术分析',
        p3_sectors: 'P3 板块产业链', p4_quant: 'P4 量化策略',
        p5_risk: 'P5 风险管理', p6_psychology: 'P6 交易心理',
        p7_integration: 'P7 实战整合',
      }
      return map[id] || id
    },
    formatLab(id) {
      const map = { m1_data_lab: 'M1 数据勘探', m2_feature_lab: 'M2 特征工程' }
      return map[id] || id
    },
    labDesc(id) { return (LAB_DEFS[id] && LAB_DEFS[id].desc) || '' },
  },
}
</script>

<style scoped>
.phase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: var(--ia-space-md);
  margin-bottom: var(--ia-space-xl);
}
.phase-card { padding: var(--ia-space-md); }
.phase-hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.phase-label { font-size: var(--ia-font-size-md); color: var(--ia-text); font-weight: 500; }
.chapter-list { display: flex; flex-direction: column; gap: 0.25rem; margin-top: 0.5rem; }
.chapter-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.4rem;
  border-radius: 4px;
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text-secondary);
}
.chapter-row:hover { background: var(--ia-surface-hover); }
.chapter-done { color: var(--ia-green); }
.chapter-done svg { color: var(--ia-green); }
.ch-name { flex: 1; }
.ch-score { font-size: var(--ia-font-size-xs); color: var(--ia-gold); }
.lab-desc-text { font-size: var(--ia-font-size-sm); color: var(--ia-text-tertiary); margin-top: 0.3rem; }

.timeline { display: flex; flex-direction: column; gap: 0.5rem; }
.timeline-item { display: flex; align-items: center; gap: 0.6rem; padding: 0.4rem 0; }
.tl-dot { width: 6px; height: 6px; background: var(--ia-gold); border-radius: 50%; flex-shrink: 0; }
.tl-title { font-size: var(--ia-font-size-md); color: var(--ia-text); margin-right: 0.5rem; }
.tl-time { font-size: var(--ia-font-size-xs); color: var(--ia-text-tertiary); margin-right: 0.5rem; }
.tl-score { font-size: var(--ia-font-size-xs); color: var(--ia-gold); }
</style>
