<template>
  <div class="spas-signal ia-page">
    <IAPageHeader
      title="SPAS"
      title-highlight="自动信号"
      subtitle="基于 SPAS 核心引擎的自动化涨跌概率分析"
      :breadcrumbs="[{ label: '首页', to: '/' }, { label: 'SPAS 自动信号' }]"
    />

    <IAPanel title="选择 ETF" subtitle="选择要分析的标的" icon="market" :body-class="'ia-flex ia-items-center ia-gap-md'">
      <select v-model="selectedETF" class="ia-select" @change="loadSignal">
        <option value="" disabled>— 选择 ETF —</option>
        <option v-for="etf in etfList" :key="etf.code" :value="etf.code">
          {{ etfNameMap[etf.code] || etf.code }}
        </option>
      </select>
      <IABadge v-if="selectedETF" variant="green">已选择</IABadge>
    </IAPanel>

    <IAPanel v-if="loading" loading title="分析中" icon="spinner" />

    <div v-if="result" class="results ia-anim-fade-in">
      <div class="ia-grid-4 hero-grid">
        <div class="hero-card" :class="directionClass">
          <ProbabilityRing :value="probability" :size="120" />
          <div class="hero-label">涨跌概率</div>
          <IABadge :variant="directionVariant">{{ directionLabel }}</IABadge>
        </div>

        <div class="hero-card position">
          <div class="hero-big-num">
            <span class="big-value">{{ (result.prediction?.r_r_ratio || 0).toFixed(1) }}</span>
          </div>
          <div class="hero-label">风险回报比</div>
          <IABadge variant="blue">R:R</IABadge>
        </div>

        <div class="hero-card success">
          <div class="hero-big-num">
            <span class="big-value">{{ ((result.prediction?.expected_value || 0) * 100).toFixed(2) }}</span>
            <span class="big-unit">%</span>
          </div>
          <div class="hero-label">期望收益</div>
          <IABadge variant="green">5日</IABadge>
        </div>

        <div class="hero-card">
          <div class="hero-big-num">
            <span class="big-value">{{ result.setup_summary?.confirmed_count || 0 }}</span>
          </div>
          <div class="hero-label">历史确认信号</div>
          <IABadge variant="neutral">Setup</IABadge>
        </div>
      </div>

      <IAPanel title="市场状态" icon="market">
        <div class="tech-strip">
          <div class="tech-item">
            <span class="tech-label">状态</span>
            <span :class="['tech-val', stateClass]">{{ result.market_state?.state?.toUpperCase() }}</span>
          </div>
          <div class="tech-item">
            <span class="tech-label">置信度</span>
            <span class="tech-val">{{ result.market_state?.confidence }}</span>
          </div>
          <div class="tech-item">
            <span class="tech-label">持续</span>
            <span class="tech-val">{{ result.market_state?.duration }} 天</span>
          </div>
          <div class="tech-item">
            <span class="tech-label">最新价</span>
            <span class="tech-val">¥{{ result.current_price?.toFixed(3) }}</span>
          </div>
        </div>
      </IAPanel>

      <IAPanel v-if="result.prediction" title="预测详情" icon="analysis">
        <dl class="kv-grid">
          <div class="kv"><dt>Setup 类型</dt><dd>{{ result.prediction.setup_type }}</dd></div>
          <div class="kv"><dt>方向概率</dt><dd>{{ (result.prediction.direction_prob * 100).toFixed(1) }}%</dd></div>
          <div class="kv"><dt>目标达成率</dt><dd>{{ (result.prediction.target_prob * 100).toFixed(1) }}%</dd></div>
          <div class="kv"><dt>止损触发率</dt><dd>{{ (result.prediction.stop_prob * 100).toFixed(1) }}%</dd></div>
          <div class="kv"><dt>风险回报比</dt><dd>{{ result.prediction.r_r_ratio.toFixed(2) }}</dd></div>
          <div class="kv"><dt>置信度</dt><dd>{{ result.prediction.confidence_level }}</dd></div>
        </dl>
      </IAPanel>
    </div>
  </div>
</template>

<script>
import { IAPageHeader, IAPanel, IABadge, ProbabilityRing } from '../components/ui'
import { getSPASSignal, getSPASETFs } from '../api/spasSignal'
import { getETFName } from '../api/market'

export default {
  name: 'SPASSignal',
  components: { IAPageHeader, IAPanel, IABadge, ProbabilityRing },
  data() {
    return {
      etfList: [],
      etfNameMap: {},
      selectedETF: '',
      loading: false,
      result: null,
    }
  },
  computed: {
    probability() {
      return this.result?.prediction?.direction_prob || 0.5
    },
    directionClass() {
      if (this.probability >= 0.55) return 'bullish'
      if (this.probability <= 0.45) return 'bearish'
      return 'neutral'
    },
    directionVariant() {
      if (this.probability >= 0.55) return 'green'
      if (this.probability <= 0.45) return 'red'
      return 'neutral'
    },
    directionLabel() {
      if (this.probability >= 0.55) return '看多'
      if (this.probability <= 0.45) return '看空'
      return '中性'
    },
    stateClass() {
      const s = this.result?.market_state?.state
      return s === 'bull' ? 'ia-text-green' : s === 'bear' ? 'ia-text-red' : ''
    },
  },
  async created() {
    try {
      const r = await getSPASETFs()
      this.etfList = r.data || []
      if (this.etfList.length) {
        this.selectedETF = this.etfList[0].code
        for (const etf of this.etfList) {
          try {
            const nr = await getETFName(etf.code)
            this.$set(this.etfNameMap, etf.code, nr.data.display_name)
          } catch (e) {}
        }
        this.loadSignal()
      }
    } catch (e) {
      console.error(e)
      alert('加载 ETF 列表失败: ' + e.message)
    }
  },
  methods: {
    async loadSignal() {
      if (!this.selectedETF) return
      this.loading = true
      try {
        const r = await getSPASSignal(this.selectedETF)
        this.result = r.data
      } catch (e) {
        alert('分析失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.spas-signal {
  padding-bottom: var(--ia-space-xl);
}

.hero-grid {
  margin-bottom: var(--ia-space-md);
}

.hero-card {
  background: var(--ia-surface);
  border: 1px solid var(--ia-border);
  border-radius: var(--ia-radius);
  padding: var(--ia-space-lg);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.hero-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: transparent;
  transition: background 0.3s;
}

.hero-card.bullish::before { background: var(--ia-green); }
.hero-card.bearish::before { background: var(--ia-red); }
.hero-card.position::before { background: var(--ia-blue); }
.hero-card.success::before { background: var(--ia-green); }

.hero-card:hover {
  border-color: var(--ia-border-strong);
}

.hero-label {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin: var(--ia-space-sm) 0 var(--ia-space-xs);
}

.hero-big-num {
  margin: var(--ia-space-sm) 0;
}

.big-value {
  font-size: 2rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
  color: var(--ia-text);
}

.big-unit {
  font-size: 0.85rem;
  color: var(--ia-text-tertiary);
  margin-left: 0.15rem;
}

.tech-strip {
  display: flex;
  flex-wrap: wrap;
  gap: var(--ia-space-xs);
  align-items: stretch;
}

.tech-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.2rem;
  padding: 0.5rem 0.8rem;
  border-radius: var(--ia-radius-xs);
  min-width: 72px;
  min-height: 48px;
  background: rgba(255, 255, 255, 0.015);
  border: 1px solid transparent;
  transition: all 0.2s;
}

.tech-item:hover {
  border-color: var(--ia-border);
  background: rgba(255, 255, 255, 0.03);
}

.tech-label {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tech-val {
  font-size: var(--ia-font-size-md);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.kv-grid {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.kv {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.45rem 0.6rem;
  border-radius: var(--ia-radius-xs);
}

.kv:nth-child(even) {
  background: rgba(255, 255, 255, 0.015);
}

.kv dt {
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text-tertiary);
}

.kv dd {
  font-size: var(--ia-font-size-md);
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  color: var(--ia-text);
}

.ia-select {
  min-width: 260px;
}
</style>
