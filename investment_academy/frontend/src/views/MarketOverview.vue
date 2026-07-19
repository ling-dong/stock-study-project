<template>
  <div class="overview-page ia-page">
    <IAPageHeader
      title="市场概览"
      subtitle="SPAS 系统沉淀的投资知识资产"
      :breadcrumbs="[{ label: '首页', to: '/' }, { label: '市场概览' }]"
    />

    <div v-if="loading" class="ia-loading">
      <IAIcon name="spinner" size="lg" class="ia-anim-spin" />
      <p>加载市场数据…</p>
    </div>
    <div v-else-if="error" class="ia-alert ia-alert--danger">
      <IAIcon name="warning" size="sm" />{{ error }}
    </div>

    <template v-else>
      <IASectionTitle icon="market" title="行业板块" />
      <div class="sector-grid">
        <div v-for="s in sectors" :key="s.id" class="ia-card sector-card">
          <div class="sector-header">
            <span class="sector-id">{{ s.id }}</span>
            <span class="sector-name">{{ s.name }}</span>
          </div>
          <div class="sector-body">
            <div class="sector-row">
              <span class="sector-label">ETF</span>
              <code class="ia-table__code">{{ s.etf_code || '无' }}</code>
            </div>
            <div v-if="s.constituents && s.constituents.length" class="sector-row">
              <span class="sector-label">代表股</span>
              <code v-for="c in s.constituents" :key="c" class="ia-table__code">{{ c }}</code>
            </div>
          </div>
        </div>
      </div>

      <div class="ia-divider"></div>

      <IASectionTitle icon="chart" title="K 线微观结构 · 6 维特征因子" />
      <div class="factor-grid">
        <div v-for="f in factors" :key="f.name" class="ia-card factor-card">
          <div class="factor-hd">
            <span class="factor-name">{{ f.chinese }}</span>
            <code class="ia-table__code">{{ f.name }}</code>
          </div>
          <p class="factor-formula"><strong>公式:</strong> {{ f.formula }}</p>
          <p class="factor-meaning">{{ f.meaning }}</p>
          <IABadge variant="neutral">范围: {{ f.range }}</IABadge>
        </div>
      </div>

      <div class="ia-divider"></div>

      <IASectionTitle icon="activity" title="市场状态机参数" />
      <IAPanel v-if="marketParams" icon="activity">
        <div class="params-grid">
          <div v-for="(val, key) in marketParams" :key="key" class="param-item">
            <span class="param-name">{{ key }}</span>
            <span class="param-value">{{ val }}</span>
          </div>
        </div>
      </IAPanel>

      <div class="ia-divider"></div>

      <IASectionTitle icon="analysis" title="Wyckoff 交易 Setup" />
      <div class="setup-grid">
        <div v-for="s in setups" :key="s.name" class="ia-card setup-card">
          <div class="setup-hd">
            <span class="setup-name">{{ s.name }}</span>
            <span class="setup-chinese">{{ s.chinese }}</span>
            <IABadge variant="neutral">{{ s.theory }}</IABadge>
          </div>
          <p class="setup-desc">{{ s.description }}</p>
          <div class="setup-meta">
            <IABadge variant="green">基础胜率 {{ (s.base_winrate * 100).toFixed(0) }}%</IABadge>
          </div>
          <div class="setup-factors">
            <IABadge v-for="qf in s.quality_factors" :key="qf" variant="neutral">{{ qf }}</IABadge>
          </div>
        </div>
      </div>

      <div class="ia-divider"></div>

      <IASectionTitle icon="warning" title="风控约束层级" />
      <div class="risk-list">
        <div v-for="r in riskConstraints" :key="r.layer" class="ia-card risk-card">
          <IABadge variant="gold">{{ r.layer }}</IABadge>
          <span class="risk-threshold">{{ r.threshold }}</span>
          <span class="risk-action">→ {{ r.action }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { IAPageHeader, IASectionTitle, IAPanel, IABadge, IAIcon } from '../components/ui'
import { getSectors, getFactors, getMarketParams, getRiskConstraints, getSetups } from '../api/knowledge'

export default {
  name: 'MarketOverview',
  components: { IAPageHeader, IASectionTitle, IAPanel, IABadge, IAIcon },
  data() {
    return {
      sectors: [],
      factors: [],
      marketParams: null,
      riskConstraints: [],
      setups: [],
      loading: true,
      error: null,
    }
  },
  async created() {
    try {
      const [sectorsRes, factorsRes, paramsRes, riskRes, setupsRes] = await Promise.all([
        getSectors(), getFactors(), getMarketParams(), getRiskConstraints(), getSetups(),
      ])
      this.sectors = sectorsRes.data || []
      this.factors = factorsRes.data || []
      this.marketParams = paramsRes.data || null
      this.riskConstraints = riskRes.data || []
      this.setups = setupsRes.data || []
    } catch (e) {
      console.error('加载市场概览失败:', e)
      this.error = '加载失败，请确认后端已启动'
    } finally {
      this.loading = false
    }
  },
}
</script>

<style scoped>
.sector-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--ia-space-md);
}

.sector-card { padding: var(--ia-space-md); background: var(--ia-surface-glass); border: 1px solid var(--ia-glass-border); border-radius: var(--ia-radius); box-shadow: var(--ia-shadow-sm); backdrop-filter: blur(var(--ia-glass-blur)); -webkit-backdrop-filter: blur(var(--ia-glass-blur)); transition: all var(--ia-transition-base); }
.sector-card:hover { border-color: var(--ia-border-strong); box-shadow: var(--ia-shadow-md); transform: translateY(-2px); }
.sector-header { display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.5rem; }
.sector-id { font-size: var(--ia-font-size-xs); color: var(--ia-gold); font-family: var(--ia-font-mono); }
.sector-name { font-size: var(--ia-font-size-md); color: var(--ia-text); font-weight: 500; }
.sector-body { display: flex; flex-direction: column; gap: 0.3rem; }
.sector-row { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.sector-label { font-size: var(--ia-font-size-xs); color: var(--ia-text-tertiary); letter-spacing: 0.1em; }

.factor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: var(--ia-space-md);
}

.factor-card { padding: var(--ia-space-md); background: var(--ia-surface-glass); border: 1px solid var(--ia-glass-border); border-radius: var(--ia-radius); box-shadow: var(--ia-shadow-sm); backdrop-filter: blur(var(--ia-glass-blur)); -webkit-backdrop-filter: blur(var(--ia-glass-blur)); transition: all var(--ia-transition-base); }
.factor-card:hover { border-color: var(--ia-border-strong); box-shadow: var(--ia-shadow-md); transform: translateY(-2px); }
.factor-hd { display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.4rem; }
.factor-name { font-size: var(--ia-font-size-lg); color: var(--ia-text); font-weight: 500; }
.factor-formula { font-size: var(--ia-font-size-sm); color: var(--ia-text-secondary); margin-bottom: 0.3rem; }
.factor-meaning { font-size: var(--ia-font-size-sm); color: var(--ia-text-tertiary); margin-bottom: 0.5rem; line-height: 1.6; }

.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--ia-space-md);
}
.param-item {
  background: var(--ia-surface-glass);
  border: 1px solid var(--ia-glass-border);
  border-radius: var(--ia-radius-xs);
  padding: 0.6rem 0.8rem;
  backdrop-filter: blur(var(--ia-glass-blur));
  -webkit-backdrop-filter: blur(var(--ia-glass-blur));
  transition: all var(--ia-transition-fast);
}
.param-item:hover { border-color: var(--ia-border-strong); box-shadow: var(--ia-shadow-sm); }
.param-name { display: block; font-size: var(--ia-font-size-xs); color: var(--ia-text-tertiary); letter-spacing: 0.05em; }
.param-value { display: block; font-size: 1.1rem; color: var(--ia-gold); font-weight: 300; margin-top: 0.15rem; font-variant-numeric: tabular-nums; }

.setup-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: var(--ia-space-md);
}
.setup-card { padding: var(--ia-space-md); background: var(--ia-surface-glass); border: 1px solid var(--ia-glass-border); border-radius: var(--ia-radius); box-shadow: var(--ia-shadow-sm); backdrop-filter: blur(var(--ia-glass-blur)); -webkit-backdrop-filter: blur(var(--ia-glass-blur)); transition: all var(--ia-transition-base); }
.setup-card:hover { border-color: var(--ia-border-strong); box-shadow: var(--ia-shadow-md); transform: translateY(-2px); }
.setup-hd { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem; flex-wrap: wrap; }
.setup-name { font-size: var(--ia-font-size-lg); color: var(--ia-gold); font-weight: 500; }
.setup-chinese { font-size: var(--ia-font-size-md); color: var(--ia-text); }
.setup-desc { font-size: var(--ia-font-size-sm); color: var(--ia-text-secondary); margin-bottom: 0.5rem; line-height: 1.6; }
.setup-meta { margin-bottom: 0.4rem; }
.setup-factors { display: flex; gap: 0.3rem; flex-wrap: wrap; }

.risk-list { display: flex; flex-direction: column; gap: 0.5rem; }
.risk-card { display: flex; align-items: center; gap: 1rem; padding: 0.8rem 1rem; font-size: var(--ia-font-size-md); background: var(--ia-surface-glass); border: 1px solid var(--ia-glass-border); border-radius: var(--ia-radius-xs); backdrop-filter: blur(var(--ia-glass-blur)); -webkit-backdrop-filter: blur(var(--ia-glass-blur)); transition: all var(--ia-transition-fast); }
.risk-card:hover { border-color: var(--ia-border-strong); box-shadow: var(--ia-shadow-sm); }
.risk-threshold { color: var(--ia-red); font-weight: 500; }
.risk-action { color: var(--ia-text-secondary); }

@media (max-width: 640px) {
  .sector-grid, .factor-grid, .setup-grid { grid-template-columns: 1fr; }
  .risk-card { flex-direction: column; align-items: flex-start; gap: 0.3rem; }
}
</style>
