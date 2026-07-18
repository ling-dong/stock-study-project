<template>
  <div class="spas-signal">
    <header class="spas-header">
      <nav class="breadcrumb">
        <router-link to="/">Home</router-link>
        <span class="sep">/</span>
        <span class="current">SPAS 自动信号</span>
      </nav>
      <h1 class="title">SPAS <span class="title-dim">自动信号</span></h1>
      <p class="subtitle">基于 SPAS 核心引擎的自动化涨跌概率分析</p>
    </header>

    <section class="panel">
      <div class="panel-header">
        <div class="panel-icon">Ⅰ</div>
        <div class="panel-title-group">
          <h2 class="panel-title">选择 ETF</h2>
          <p class="panel-sub">选择要分析的标的</p>
        </div>
      </div>
      <div class="panel-body">
        <select v-model="selectedETF" class="select-main" @change="loadSignal">
          <option value="" disabled>— 选择 ETF —</option>
          <option v-for="etf in etfList" :key="etf.code" :value="etf.code">
            {{ etfNameMap[etf.code] || etf.code }}
          </option>
        </select>
      </div>
    </section>

    <section class="panel" v-if="loading">
      <div class="panel-body center">分析中...</div>
    </section>

    <div v-if="result" class="results">
      <div class="hero-grid">
        <div :class="['hero-card', directionClass]">
          <div class="hero-ring">
            <svg viewBox="0 0 120 120" class="ring-svg">
              <circle cx="60" cy="60" r="52" class="ring-bg" />
              <circle cx="60" cy="60" r="52" class="ring-fill"
                      :stroke-dasharray="326.7"
                      :stroke-dashoffset="326.7 * (1 - probability)" />
            </svg>
            <div class="ring-center">
              <span class="ring-value">{{ (probability * 100).toFixed(0) }}</span>
              <span class="ring-unit">%</span>
            </div>
          </div>
          <div class="hero-label">涨跌概率</div>
          <div class="hero-badge" :class="directionClass">{{ directionLabel }}</div>
        </div>

        <div class="hero-card position">
          <div class="hero-big-num">
            <span class="big-value">{{ (result.prediction?.r_r_ratio || 0).toFixed(1) }}</span>
          </div>
          <div class="hero-label">风险回报比</div>
          <div class="hero-badge good">R:R</div>
        </div>

        <div class="hero-card success">
          <div class="hero-big-num">
            <span class="big-value">{{ (result.prediction?.expected_value || 0) * 100 }}</span>
            <span class="big-unit">%</span>
          </div>
          <div class="hero-label">期望收益</div>
          <div class="hero-badge good">5日</div>
        </div>

        <div class="hero-card">
          <div class="hero-big-num">
            <span class="big-value">{{ result.setup_summary?.confirmed_count || 0 }}</span>
          </div>
          <div class="hero-label">历史确认信号</div>
          <div class="hero-badge">Setup</div>
        </div>
      </div>

      <section class="panel">
        <div class="panel-header">
          <div class="panel-icon sm">⌬</div>
          <h2 class="panel-title">市场状态</h2>
        </div>
        <div class="panel-body">
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
        </div>
      </section>

      <section class="panel" v-if="result.prediction">
        <div class="panel-header">
          <div class="panel-icon sm">☰</div>
          <h2 class="panel-title">预测详情</h2>
        </div>
        <div class="panel-body">
          <dl class="kv-grid">
            <div class="kv"><dt>Setup 类型</dt><dd>{{ result.prediction.setup_type }}</dd></div>
            <div class="kv"><dt>方向概率</dt><dd>{{ (result.prediction.direction_prob * 100).toFixed(1) }}%</dd></div>
            <div class="kv"><dt>目标达成率</dt><dd>{{ (result.prediction.target_prob * 100).toFixed(1) }}%</dd></div>
            <div class="kv"><dt>止损触发率</dt><dd>{{ (result.prediction.stop_prob * 100).toFixed(1) }}%</dd></div>
            <div class="kv"><dt>风险回报比</dt><dd>{{ result.prediction.r_r_ratio.toFixed(2) }}</dd></div>
            <div class="kv"><dt>置信度</dt><dd>{{ result.prediction.confidence_level }}</dd></div>
          </dl>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { getSPASSignal, getSPASETFs } from '../api/spasSignal'
import { getETFName } from '../api/market'

export default {
  name: 'SPASSignal',
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
    directionLabel() {
      if (this.probability >= 0.55) return '看多'
      if (this.probability <= 0.45) return '看空'
      return '中性'
    },
    stateClass() {
      const s = this.result?.market_state?.state
      return s === 'bull' ? 'text-pos' : s === 'bear' ? 'text-neg' : ''
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
  --bg: #08080C;
  --surface: #0C0C12;
  --border: rgba(255,255,255,0.06);
  --gold: #F0B90B;
  --green: #0ECB81;
  --red: #F6465D;
  --blue: #3B82F6;
  --text: #EAECEF;
  --text2: #848E9C;
  --text3: #5E6673;
  --radius: 12px;
  font-family: -apple-system, 'Inter', 'Segoe UI', sans-serif;
  color: var(--text);
  max-width: 1100px;
}
.spas-header { margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--border); }
.breadcrumb { font-size: 0.72rem; color: var(--text3); margin-bottom: 0.6rem; letter-spacing: 0.04em; text-transform: uppercase; }
.breadcrumb a { color: var(--text3); text-decoration: none; }
.breadcrumb a:hover { color: var(--gold); }
.breadcrumb .sep { margin: 0 0.4rem; }
.breadcrumb .current { color: var(--gold); }
.title { font-size: 1.65rem; font-weight: 700; letter-spacing: -0.02em; margin: 0; }
.title-dim { color: var(--text3); font-weight: 400; }
.subtitle { color: var(--text2); font-size: 0.85rem; margin-top: 0.5rem; }

.panel {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); margin-bottom: 1rem; overflow: hidden;
}
.panel:hover { border-color: rgba(255,255,255,0.1); }
.panel-header {
  display: flex; align-items: center; gap: 0.8rem;
  padding: 1rem 1.3rem; border-bottom: 1px solid var(--border);
  background: rgba(255,255,255,0.015);
}
.panel-icon {
  width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; font-weight: 700;
  background: rgba(240,185,11,0.08); color: var(--gold); border: 1px solid rgba(240,185,11,0.15);
}
.panel-icon.sm { width: 28px; height: 28px; font-size: 0.8rem; border-radius: 8px; }
.panel-title-group { flex: 1; }
.panel-title { font-size: 0.9rem; font-weight: 600; margin: 0; color: var(--text); letter-spacing: -0.01em; }
.panel-sub { font-size: 0.7rem; color: var(--text3); margin: 0.15rem 0 0; }
.panel-body { padding: 1.3rem; }
.panel-body.center { text-align: center; color: var(--text2); }

.select-main {
  width: 100%; max-width: 480px; padding: 0.7rem 0.9rem;
  background: var(--bg); border: 1px solid var(--border);
  border-radius: 8px; color: var(--gold); font-size: 0.9rem;
  outline: none; cursor: pointer; transition: border-color 0.2s;
  appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23848E9C' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 0.8rem center;
}
.select-main:focus { border-color: var(--gold); box-shadow: 0 0 0 3px rgba(240,185,11,0.06); }

.hero-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; margin-bottom: 1rem; }
.hero-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.5rem 1rem;
  text-align: center; transition: all 0.3s; position: relative; overflow: hidden;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 200px;
}
.hero-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: transparent; transition: background 0.3s; }
.hero-card.bullish::before { background: var(--green); }
.hero-card.bearish::before { background: var(--red); }
.hero-card.position::before { background: var(--blue); }
.hero-card.success::before { background: var(--green); }
.hero-label { font-size: 0.7rem; color: var(--text3); text-transform: uppercase; letter-spacing: 0.08em; margin: 0.6rem 0 0.4rem; }
.hero-badge { font-size: 0.65rem; padding: 0.2rem 0.5rem; border-radius: 10px; display: inline-block; letter-spacing: 0.04em; }
.hero-badge.bullish, .hero-badge.good { background: rgba(14,203,129,0.1); color: var(--green); }
.hero-badge.bearish, .hero-badge.bad { background: rgba(246,70,93,0.1); color: var(--red); }
.hero-big-num { margin: 0.5rem 0; }
.big-value { font-size: 2rem; font-weight: 700; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }
.big-unit { font-size: 0.85rem; color: var(--text3); margin-left: 0.15rem; }

.hero-ring { position: relative; width: 120px; height: 120px; margin: 0 auto; }
.ring-svg { width: 120px; height: 120px; transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: rgba(255,255,255,0.05); stroke-width: 6; }
.ring-fill { fill: none; stroke: var(--gold); stroke-width: 6; stroke-linecap: round; transition: stroke-dashoffset 1s ease-out; }
.ring-center { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ring-value { font-size: 1.6rem; font-weight: 700; line-height: 1; letter-spacing: -0.03em; }
.ring-unit { font-size: 0.65rem; color: var(--text3); }

.tech-strip { display: flex; flex-wrap: wrap; gap: 0.25rem; align-items: stretch; }
.tech-item {
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.2rem;
  padding: 0.5rem 0.8rem; border-radius: 6px; min-width: 72px; min-height: 48px;
  background: rgba(255,255,255,0.015); border: 1px solid transparent; transition: all 0.2s;
}
.tech-item:hover { border-color: var(--border); background: rgba(255,255,255,0.03); }
.tech-label { font-size: 0.65rem; color: var(--text3); text-transform: uppercase; letter-spacing: 0.04em; }
.tech-val { font-size: 0.85rem; font-weight: 600; font-variant-numeric: tabular-nums; }

.kv-grid { display: flex; flex-direction: column; gap: 0.25rem; }
.kv { display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0.6rem; border-radius: 6px; }
.kv:nth-child(even) { background: rgba(255,255,255,0.015); }
.kv dt { font-size: 0.72rem; color: var(--text3); }
.kv dd { font-size: 0.85rem; font-weight: 500; font-variant-numeric: tabular-nums; }
.text-pos { color: var(--green) !important; }
.text-neg { color: var(--red) !important; }
</style>
