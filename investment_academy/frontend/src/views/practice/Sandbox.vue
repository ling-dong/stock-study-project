<template>
  <div class="sandbox-page ia-page">
    <IAPageHeader
      title="交易沙盒"
      subtitle="用真实历史数据模拟交易，测试你的策略"
      :breadcrumbs="[{ label: '首页', to: '/' }, { label: '交易沙盒' }]"
    />

    <IAPanel v-if="!sessionId" title="初始化沙盒" icon="tool">
      <div class="init-controls">
        <div class="ia-form-group">
          <label class="ia-label">ETF 选择</label>
          <select v-model="initETF" class="ia-select">
            <option v-for="etf in etfList" :key="etf.code" :value="etf.code">{{ etfNameMap[etf.code] || etf.code }}</option>
          </select>
        </div>
        <div class="ia-form-group">
          <label class="ia-label">时间框架</label>
          <select v-model="initTimeframe" class="ia-select">
            <option value="day">日线</option>
            <option value="5min">5分钟</option>
          </select>
        </div>
        <div class="ia-form-group">
          <label class="ia-label">起始日期</label>
          <select v-model="startDate" class="ia-select">
            <option value="">从头开始</option>
            <option v-for="d in availableDates" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>
        <div class="ia-form-group">
          <label class="ia-label">初始资金</label>
          <input v-model.number="initCash" type="number" class="ia-input" step="10000" min="10000" />
        </div>
        <div class="ia-form-group" style="align-self: flex-end">
          <IAButton variant="primary" :loading="initLoading" @click="doInit">
            开始交易
          </IAButton>
        </div>
      </div>
    </IAPanel>

    <div v-else class="sandbox-main">
      <div class="ia-metric-grid metric-5">
        <IAMetricCard label="现金" :value="state.cash" unit="¥" />
        <IAMetricCard label="持仓" :value="state.shares" unit="股" />
        <IAMetricCard label="总资产" :value="portfolioValue" unit="¥" trend="up" />
        <IAMetricCard label="浮动盈亏" :value="pnlPct" :unit="`% (${pnl >= 0 ? '+' : ''}${pnl.toFixed(0)})`" :trend="pnl >= 0 ? 'up' : 'down'" />
        <IAMetricCard label="累计盈亏" :value="cumulativePct" :unit="`% (${cumulativePnl >= 0 ? '+' : ''}${cumulativePnl.toFixed(0)})`" :trend="cumulativePnl >= 0 ? 'up' : 'down'" />
      </div>

      <IAPanel v-if="bars.length" icon="chart">
        <KLineChart :bars="bars" :height="360" :markers="chartMarkers" :startMarker="tradeStartDate" :drawMode="drawMode" />
      </IAPanel>

      <div class="bar-info" v-if="currentBar">
        <div class="bar-item">
          <span class="bar-label">日期</span>
          <span class="bar-val">{{ currentBar.date }}</span>
        </div>
        <div class="bar-item">
          <span class="bar-label">开盘</span>
          <span class="bar-val">{{ currentBar.open?.toFixed(2) }}</span>
        </div>
        <div class="bar-item">
          <span class="bar-label">最高</span>
          <span class="bar-val ia-text-red">{{ currentBar.high?.toFixed(2) }}</span>
        </div>
        <div class="bar-item">
          <span class="bar-label">最低</span>
          <span class="bar-val ia-text-green">{{ currentBar.low?.toFixed(2) }}</span>
        </div>
        <div class="bar-item">
          <span class="bar-label">收盘</span>
          <span class="bar-val" :class="closeColor">{{ currentBar.close?.toFixed(2) }}</span>
        </div>
        <div class="bar-item">
          <span class="bar-label">成交量</span>
          <span class="bar-val">{{ formatVolume(currentBar.volume) }}</span>
        </div>
      </div>

      <div class="controls-bar" v-if="!state.isDone">
        <IAButton variant="secondary" :loading="actionLoading" @click="doAdvance">
          <IAIcon name="arrow-right" size="sm" />下一天
        </IAButton>
        <IAButton :variant="drawMode ? 'primary' : 'ghost'" @click="drawMode = !drawMode">
          <IAIcon name="analysis" size="sm" />{{ drawMode ? '画线中…' : '画线' }}
        </IAButton>

        <div class="trade-btns">
          <div class="trade-group">
            <IAButton variant="primary" :loading="actionLoading" @click="openBuyModal">
              <IAIcon name="arrow-up" size="sm" />买入
            </IAButton>
            <input v-model.number="buyShares" type="number" class="shares-input" placeholder="股数" min="100" step="100" />
            <IAButton variant="ghost" size="sm" @click="setBuyRatio(0.25)" :disabled="actionLoading">¼</IAButton>
            <IAButton variant="ghost" size="sm" @click="setBuyRatio(0.5)" :disabled="actionLoading">½</IAButton>
            <IAButton variant="ghost" size="sm" @click="setBuyRatio(0.75)" :disabled="actionLoading">¾</IAButton>
            <IAButton variant="ghost" size="sm" @click="setBuyRatio(1)" :disabled="actionLoading">满</IAButton>
          </div>
          <div class="trade-group">
            <IAButton variant="danger" :loading="actionLoading" @click="doSellAll" :disabled="state.shares <= 0">
              <IAIcon name="arrow-down" size="sm" />全卖
            </IAButton>
            <input v-model.number="sellShares" type="number" class="shares-input" placeholder="部分" min="100" step="100" />
            <IAButton variant="danger" size="sm" :loading="actionLoading" @click="doSellPartial" :disabled="state.shares <= 0 || sellShares <= 0">
              部分卖
            </IAButton>
          </div>
        </div>
      </div>

      <IAPanel v-if="trades.length" title="交易记录" icon="journal" :tag="trades.length.toString()">
        <div class="ia-table-wrapper">
          <table class="ia-table trade-table">
            <thead>
              <tr><th>日期</th><th>操作</th><th>价格</th><th>股数</th><th>金额</th><th>成本</th><th>理由</th></tr>
            </thead>
            <tbody>
              <tr v-for="(t, i) in trades" :key="i" :class="t.action === 'buy' ? 'row-buy' : 'row-sell'">
                <td>{{ t.date }}</td>
                <td>{{ t.action === 'buy' ? '买入' : '卖出' }}</td>
                <td>{{ t.price?.toFixed(2) }}</td>
                <td>{{ t.shares }}</td>
                <td>¥{{ t.amount?.toLocaleString() }}</td>
                <td>¥{{ t.cost?.toFixed(1) }}</td>
                <td>{{ t.reason || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </IAPanel>

      <IAPanel v-if="performance" title="绩效报告" icon="chart">
        <div class="perf-grid">
          <IAMetricCard label="总收益率" :value="performance.total_return_pct" unit="%" :trend="performance.total_return_pct >= 0 ? 'up' : 'down'" />
          <IAMetricCard label="胜率" :value="performance.win_rate * 100" unit="%" />
          <IAMetricCard label="最大回撤" :value="-performance.max_drawdown_pct" unit="%" trend="down" />
          <IAMetricCard label="总交易成本" :value="performance.total_costs" unit="¥" />
          <IAMetricCard label="盈利交易" :value="performance.winning_trades" trend="up" />
          <IAMetricCard label="亏损交易" :value="performance.losing_trades" trend="down" />
          <IAMetricCard label="总交易" :value="performance.total_trades" />
          <IAMetricCard label="最终资产" :value="performance.total_value" unit="¥" trend="up" />
        </div>
        <IAButton variant="secondary" @click="resetSandbox" style="margin-top: var(--ia-space-md)">
          <IAIcon name="close" size="sm" />新沙盒
        </IAButton>
      </IAPanel>
    </div>

    <!-- 买入弹窗 -->
    <div v-if="showBuyModal" class="modal-overlay" @click.self="showBuyModal = false">
      <div class="modal ia-card">
        <h3>确认买入</h3>
        <p>以 <strong>{{ currentBar?.close?.toFixed(2) }}</strong> 元买入 <strong>{{ buyShares }}</strong> 股</p>
        <p class="ia-hint">约 ¥{{ (buyShares * (currentBar?.close || 0)).toLocaleString() }}（不含手续费）</p>
        <div class="modal-actions">
          <IAButton variant="ghost" @click="showBuyModal = false">取消</IAButton>
          <IAButton variant="primary" @click="doBuy">确认买入</IAButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  sandboxInit, getSandboxState, getSandboxBar,
  sandboxAdvance, sandboxBuy, sandboxSell,
  getSandboxPortfolio, getSandboxPerformance,
} from '../../api/sandbox'
import { getETFs, getETFName, getETFOHLCV } from '../../api/market'
import { IAPageHeader, IAPanel, IAButton, IAMetricCard, IAIcon } from '../../components/ui'
import KLineChart from '../../components/KLineChart.vue'

export default {
  name: 'Sandbox',
  components: { IAPageHeader, IAPanel, IAButton, IAMetricCard, IAIcon, KLineChart },
  data() {
    return {
      etfList: [],
      etfNameMap: {},
      initETF: '',
      initTimeframe: 'day',
      initCash: 100000,
      startDate: '',
      availableDates: [],
      initLoading: false,
      sessionId: null,
      state: { cash: 0, shares: 0, costBasis: 0, index: 0, totalBars: 0, isDone: false },
      currentBar: null,
      bars: [],
      allBars: [],
      preStartCount: 0,
      tradeStartDate: null,
      drawMode: false,
      trades: [],
      performance: null,
      portfolioValue: 0,
      pnl: 0, pnlPct: 0,
      actionLoading: false,
      showBuyModal: false,
      buyShares: 100,
      sellShares: 100,
    }
  },
  computed: {
    pnlClass() { return this.pnl >= 0 ? 'ia-text-green' : 'ia-text-red' },
    cumulativePnl() { return this.portfolioValue - this.initCash },
    cumulativePct() { return this.initCash > 0 ? (this.cumulativePnl / this.initCash) * 100 : 0 },
    cumulativeClass() { return this.cumulativePnl >= 0 ? 'ia-text-green' : 'ia-text-red' },
    chartMarkers() { return this.trades.map(t => ({ date: t.date, type: t.action, price: t.price })) },
    closeColor() {
      if (!this.currentBar || !this.bars.length) return ''
      const prev = this.bars.length >= 2 ? this.bars[this.bars.length - 2] : null
      if (!prev) return ''
      return this.currentBar.close >= prev.close ? 'ia-text-red' : 'ia-text-green'
    },
  },
  async created() {
    try {
      const res = await getETFs()
      this.etfList = res.data || []
      if (this.etfList.length) {
        this.initETF = this.etfList[0].code
        for (const etf of this.etfList) {
          try {
            const nr = await getETFName(etf.code)
            this.$set(this.etfNameMap, etf.code, nr.data.display_name)
          } catch (e) {}
        }
        await this.loadAvailableDates()
      }
    } catch (e) {
      console.error('加载 ETF 列表失败:', e)
    }
  },
  methods: {
    formatVolume(v) {
      if (!v) return '0'
      if (v >= 1e8) return (v / 1e8).toFixed(2) + '亿'
      if (v >= 1e4) return (v / 1e4).toFixed(1) + '万'
      return v.toString()
    },
    async doInit() {
      this.initLoading = true
      try {
        const res = await sandboxInit(this.initETF, this.initTimeframe, this.initCash, this.startDate || undefined)
        this.sessionId = res.data.session_id
        await this.refreshState()
        const limit = this.initTimeframe === 'day' ? 2000 : 500
        const ohlcvRes = await getETFOHLCV(this.initETF, this.initTimeframe, limit, 0)
        let loaded = ohlcvRes.data.bars || []
        this.preStartCount = 0
        if (this.startDate) {
          const startIdx = loaded.findIndex(b => b.date >= this.startDate)
          if (startIdx >= 0) {
            const historyCount = Math.min(startIdx, 30)
            this.preStartCount = historyCount
            loaded = loaded.slice(startIdx - historyCount)
          }
        }
        this.allBars = loaded
        this.tradeStartDate = this.allBars[this.preStartCount]?.date || null
        this.updateBars()
      } catch (e) {
        alert('初始化失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        this.initLoading = false
      }
    },
    async refreshState() {
      const [stateRes, barRes, portRes] = await Promise.all([
        getSandboxState(this.sessionId),
        getSandboxBar(this.sessionId).catch(() => ({ data: null })),
        getSandboxPortfolio(this.sessionId).catch(() => ({ data: {} })),
      ])
      this.state = stateRes.data
      this.currentBar = barRes.data
      this.portfolioValue = portRes.data.value || this.state.cash
      this.pnl = portRes.data.unrealized_pnl || 0
      this.pnlPct = portRes.data.unrealized_pnl_pct || 0
      this.updateBars()
    },
    updateBars() {
      if (!this.allBars.length) { this.bars = []; return }
      const chartEnd = this.preStartCount + this.state.index + 1
      const end = Math.min(chartEnd, this.allBars.length)
      this.bars = this.allBars.slice(0, end)
    },
    async loadAvailableDates() {
      if (!this.initETF) return
      try {
        const res = await getETFOHLCV(this.initETF, this.initTimeframe, 500, 0)
        const allBars = res.data.bars || []
        this.availableDates = allBars.filter((_, i) => i % 20 === 0 || i === 0).map(b => b.date)
      } catch (e) { console.error('加载可用日期失败:', e) }
    },
    async doAdvance() {
      this.actionLoading = true
      try {
        const res = await sandboxAdvance(this.sessionId)
        await this.refreshState()
        if (res.data.is_done) { await this.loadPerformance() }
      } catch (e) { alert('操作失败: ' + (e.response?.data?.detail || e.message)) }
      finally { this.actionLoading = false }
    },
    setBuyRatio(ratio) {
      if (!this.currentBar) return
      const price = this.currentBar.close * 1.001
      const cash = this.state.cash * ratio
      const shares = Math.floor(cash / price / 100) * 100
      this.buyShares = Math.max(shares, 0)
    },
    openBuyModal() {
      if (this.buyShares <= 0 || this.buyShares % 100 !== 0) {
        alert('A股以手为单位，买入必须是 100 的整数倍')
        return
      }
      if (this.buyShares * (this.currentBar?.close || 0) > this.state.cash) {
        alert(`资金不足，可用 ${this.state.cash.toLocaleString()} 元`)
        return
      }
      this.showBuyModal = true
    },
    async doBuy() {
      this.showBuyModal = false
      this.actionLoading = true
      try {
        const res = await sandboxBuy(this.sessionId, this.buyShares)
        this.trades.push(res.data.trade)
        await this.refreshState()
      } catch (e) { alert('买入失败: ' + (e.response?.data?.detail || e.message)) }
      finally { this.actionLoading = false }
    },
    async doSellAll() {
      this.actionLoading = true
      try {
        const res = await sandboxSell(this.sessionId, 0)
        this.trades.push(res.data.trade)
        await this.refreshState()
        if (this.state.isDone) { await this.loadPerformance() }
      } catch (e) { alert('卖出失败: ' + (e.response?.data?.detail || e.message)) }
      finally { this.actionLoading = false }
    },
    async doSellPartial() {
      if (this.sellShares <= 0) { alert('请输入要卖出的股数'); return }
      if (this.sellShares > this.state.shares) { alert(`持仓不足，最多卖出 ${this.state.shares} 股`); return }
      this.actionLoading = true
      try {
        const res = await sandboxSell(this.sessionId, this.sellShares)
        this.trades.push(res.data.trade)
        await this.refreshState()
        if (this.state.isDone) { await this.loadPerformance() }
      } catch (e) { alert('卖出失败: ' + (e.response?.data?.detail || e.message)) }
      finally { this.actionLoading = false }
    },
    async loadPerformance() {
      try {
        const res = await getSandboxPerformance(this.sessionId)
        this.performance = res.data
      } catch (e) { console.error('加载绩效失败:', e) }
    },
    resetSandbox() {
      this.sessionId = null
      this.state = { cash: 0, shares: 0, costBasis: 0, index: 0, totalBars: 0, isDone: false }
      this.currentBar = null
      this.bars = []
      this.allBars = []
      this.preStartCount = 0
      this.tradeStartDate = null
      this.drawMode = false
      this.trades = []
      this.performance = null
      this.portfolioValue = 0
      this.pnl = 0
      this.pnlPct = 0
    },
  },
}
</script>

<style scoped>
.metric-5 {
  grid-template-columns: repeat(5, 1fr);
}

.init-controls {
  display: flex;
  gap: var(--ia-space-lg);
  align-items: flex-end;
  flex-wrap: wrap;
}

.bar-info {
  display: flex;
  gap: var(--ia-space-md);
  margin: var(--ia-space-md) 0;
  flex-wrap: wrap;
}

.bar-item {
  display: flex;
  flex-direction: column;
  min-width: 80px;
}

.bar-label {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.bar-val {
  font-size: var(--ia-font-size-md);
  color: var(--ia-text);
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.controls-bar {
  display: flex;
  gap: var(--ia-space-md);
  align-items: center;
  margin: var(--ia-space-md) 0;
  flex-wrap: wrap;
}

.trade-btns {
  display: flex;
  gap: var(--ia-space-md);
  align-items: center;
  flex-wrap: wrap;
}

.trade-group {
  display: flex;
  gap: 0.4rem;
  align-items: center;
}

.shares-input {
  width: 80px;
  padding: 0.4rem;
  background: var(--ia-bg);
  border: 1px solid var(--ia-border);
  border-radius: var(--ia-radius-xs);
  color: var(--ia-text);
  font-size: 0.82rem;
  outline: none;
}

.trade-table .row-buy td { color: var(--ia-red); }
.trade-table .row-sell td { color: var(--ia-green); }

.perf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--ia-space-md);
  margin-bottom: var(--ia-space-md);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  max-width: 420px;
  width: 90%;
  padding: var(--ia-space-lg);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--ia-space-sm);
  margin-top: var(--ia-space-md);
}

@media (max-width: 1100px) {
  .metric-5 { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 640px) {
  .metric-5 { grid-template-columns: repeat(2, 1fr); }
  .controls-bar, .trade-btns, .trade-group { flex-direction: column; align-items: stretch; }
}
</style>
