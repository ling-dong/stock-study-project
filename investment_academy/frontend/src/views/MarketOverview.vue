<template>
  <div class="overview-page">
    <div class="breadcrumb">
      <router-link to="/">首页</router-link>
      <span> / </span>
      <span><strong>市场概览</strong></span>
    </div>

    <h1>🏦 市场概览</h1>
    <p class="page-desc">SPAS 系统沉淀的投资知识资产</p>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">加载市场数据…</div>
    <div v-else-if="error" class="loading">{{ error }}</div>

    <!-- 行业板块 -->
    <h2 v-if="!loading">📊 行业板块</h2>
    <div class="sector-grid" v-if="sectors.length">
      <div v-for="s in sectors" :key="s.id" class="sector-card card">
        <div class="sector-header">
          <span class="sector-id">{{ s.id }}</span>
          <span class="sector-name">{{ s.name }}</span>
        </div>
        <div class="sector-body">
          <div class="sector-etf">
            <span class="tag-label">ETF</span>
            <code>{{ s.etf_code || '无' }}</code>
          </div>
          <div class="sector-constituents" v-if="s.constituents && s.constituents.length">
            <span class="tag-label">代表股</span>
            <code v-for="c in s.constituents" :key="c" class="const-code">{{ c }}</code>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="loading">加载中…</div>

    <div class="divider"></div>

    <!-- 特征因子定义 -->
    <h2>🔬 K 线微观结构 · 6 维特征因子</h2>
    <div class="factor-list">
      <div v-for="f in factors" :key="f.name" class="factor-card card">
        <div class="factor-hd">
          <span class="factor-name">{{ f.chinese }}</span>
          <code class="factor-var">{{ f.name }}</code>
        </div>
        <p class="factor-formula"><strong>公式:</strong> {{ f.formula }}</p>
        <p class="factor-meaning">{{ f.meaning }}</p>
        <span class="factor-range">范围: {{ f.range }}</span>
      </div>
    </div>

    <div class="divider"></div>

    <!-- 市场状态机参数 -->
    <h2>⚙️ 市场状态机参数</h2>
    <div class="params-card card" v-if="marketParams">
      <div class="params-grid">
        <div class="param-item" v-for="(val, key) in marketParams" :key="key">
          <span class="param-name">{{ key }}</span>
          <span class="param-value">{{ val }}</span>
        </div>
      </div>
    </div>

    <div class="divider"></div>

    <!-- Wyckoff Setup -->
    <h2>🎯 Wyckoff 交易 Setup</h2>
    <div class="setup-list">
      <div v-for="s in setups" :key="s.name" class="setup-card card">
        <div class="setup-hd">
          <span class="setup-name">{{ s.name }}</span>
          <span class="setup-chinese">{{ s.chinese }}</span>
          <span class="setup-theory">{{ s.theory }}</span>
        </div>
        <p class="setup-desc">{{ s.description }}</p>
        <div class="setup-meta">
          <span class="setup-winrate">基础胜率: {{ (s.base_winrate * 100).toFixed(0) }}%</span>
        </div>
        <div class="setup-factors">
          <span v-for="qf in s.quality_factors" :key="qf" class="qf-tag">{{ qf }}</span>
        </div>
      </div>
    </div>

    <div class="divider"></div>

    <!-- 风控约束 -->
    <h2>🛡️ 风控约束层级</h2>
    <div class="risk-list" v-if="riskConstraints.length">
      <div v-for="r in riskConstraints" :key="r.layer" class="risk-card card">
        <span class="risk-layer">{{ r.layer }}</span>
        <span class="risk-threshold">{{ r.threshold }}</span>
        <span class="risk-action">→ {{ r.action }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { getSectors, getFactors, getMarketParams, getRiskConstraints, getSetups } from '../api/knowledge'

export default {
  name: 'MarketOverview',
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
.page-desc { font-size: 0.9rem; color: #6B6B7B; margin-bottom: 1.5rem; }
.breadcrumb { font-size: 0.78rem; color: #6B6B7B; margin-bottom: 1.2rem; }
.breadcrumb span { color: #F0B90B; }
.breadcrumb a { color: #6B6B7B; text-decoration: none; }
.breadcrumb strong { color: #F5F0E0; }

.card { background: #0D0D10; border: 1px solid #151518; border-radius: 10px; padding: 1.2rem; }

/* Sectors */
.sector-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.7rem; margin-bottom: 1.5rem; }
.sector-card { padding: 0.9rem 1rem; }
.sector-header { display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.5rem; }
.sector-id { font-size: 0.65rem; color: #F0B90B; font-family: monospace; }
.sector-name { font-size: 0.9rem; color: #F5F0E0; }
.sector-body { display: flex; flex-direction: column; gap: 0.3rem; }
.sector-etf, .sector-constituents { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.tag-label { font-size: 0.63rem; color: #6B6B7B; letter-spacing: 0.1em; }
code { background: #141417; padding: 0.15rem 0.4rem; border-radius: 3px; font-size: 0.75rem; color: #F0B90B; font-family: 'SF Mono', Consolas, monospace; }
.const-code { font-size: 0.7rem; }

/* Factors */
.factor-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 0.8rem; margin-bottom: 1.5rem; }
.factor-hd { display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.4rem; }
.factor-name { font-size: 1rem; color: #F5F0E0; }
.factor-var { font-size: 0.72rem; }
.factor-formula { font-size: 0.82rem; color: #C8C6C3; margin-bottom: 0.3rem; }
.factor-meaning { font-size: 0.8rem; color: #A0A0A8; margin-bottom: 0.3rem; }
.factor-range { font-size: 0.7rem; color: #6B6B7B; }

/* Market Params */
.params-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 0.6rem; }
.param-item { background: #0A0A0B; border: 1px solid #151518; border-radius: 6px; padding: 0.5rem 0.7rem; }
.param-name { display: block; font-size: 0.63rem; color: #6B6B7B; letter-spacing: 0.05em; }
.param-value { display: block; font-size: 1.1rem; color: #F0B90B; font-weight: 300; margin-top: 0.15rem; }

/* Setups */
.setup-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 0.8rem; margin-bottom: 1.5rem; }
.setup-hd { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem; }
.setup-name { font-size: 1.1rem; color: #F0B90B; font-weight: 400; }
.setup-chinese { font-size: 0.85rem; color: #F5F0E0; }
.setup-theory { font-size: 0.68rem; color: #6B6B7B; background: #141417; padding: 0.15rem 0.4rem; border-radius: 3px; }
.setup-desc { font-size: 0.82rem; color: #C8C6C3; margin-bottom: 0.5rem; line-height: 1.6; }
.setup-meta { margin-bottom: 0.4rem; }
.setup-winrate { font-size: 0.75rem; color: #4ADE80; }
.setup-factors { display: flex; gap: 0.3rem; flex-wrap: wrap; }
.qf-tag { font-size: 0.68rem; color: #A0A0A8; background: #141417; padding: 0.2rem 0.5rem; border-radius: 4px; }

/* Risk */
.risk-list { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1.5rem; }
.risk-card { display: flex; align-items: center; gap: 1rem; padding: 0.8rem 1rem; font-size: 0.9rem; }
.risk-layer { font-size: 0.72rem; color: #F0B90B; background: #141417; padding: 0.2rem 0.5rem; border-radius: 4px; min-width: 36px; text-align: center; }
.risk-threshold { color: #EF5350; font-weight: 500; }
.risk-action { color: #A0A0A8; }

.loading { padding: 2rem; text-align: center; color: #6B6B7B; }
</style>
