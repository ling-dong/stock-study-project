<template>
  <div class="sandbox-page">
    <div class="breadcrumb">
      <router-link to="/">首页</router-link>
      <span> / </span>
      <span><strong>交易沙盒</strong></span>
    </div>

    <h1>🎮 交易沙盒</h1>
    <p class="page-desc">用真实历史数据模拟交易，测试你的策略</p>

    <!-- 初始化面板 -->
    <div v-if="!sessionId" class="init-panel card">
      <h3>初始化沙盒</h3>
      <div class="init-controls">
        <div class="control-group">
          <label>ETF 选择</label>
          <select v-model="initETF" class="styled-select">
            <option v-for="etf in etfList" :key="etf.code" :value="etf.code">
              {{ etfNameMap[etf.code] || etf.code }}
            </option>
          </select>
        </div>
        <div class="control-group">
          <label>时间框架</label>
          <select v-model="initTimeframe" class="styled-select">
            <option value="day">日线</option>
            <option value="5min">5分钟</option>
          </select>
        </div>
        <div class="control-group">
          <label>起始日期</label>
          <select v-model="startDate" class="styled-select" @change="onStartDateChanged">
            <option value="">从头开始</option>
            <option v-for="d in availableDates" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>
        <div class="control-group">
          <label>初始资金</label>
          <input v-model.number="initCash" type="number" class="styled-input" step="10000" min="10000" />
        </div>
        <div class="control-group" style="align-self: flex-end">
          <button class="btn-primary" @click="doInit" :disabled="initLoading">
            {{ initLoading ? '加载中…' : '开始交易' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 沙盒主界面 -->
    <div v-else class="sandbox-main">
      <!-- 状态栏 -->
      <div class="sb-status-bar">
        <div class="sb-stat">
          <span class="sb-stat-label">现金</span>
          <span class="sb-stat-value cash">¥{{ state.cash.toLocaleString() }}</span>
        </div>
        <div class="sb-stat">
          <span class="sb-stat-label">持仓</span>
          <span class="sb-stat-value">{{ state.shares }} 股</span>
        </div>
        <div class="sb-stat">
          <span class="sb-stat-label">总资产</span>
          <span class="sb-stat-value total">¥{{ portfolioValue.toLocaleString() }}</span>
        </div>
        <div class="sb-stat">
          <span class="sb-stat-label">浮动盈亏</span>
          <span class="sb-stat-value" :class="pnlClass">
            {{ pnl >= 0 ? '+' : '' }}{{ pnl.toFixed(2) }} ({{ pnlPct >= 0 ? '+' : '' }}{{ pnlPct.toFixed(2) }}%)
          </span>
        </div>
        <div class="sb-stat">
          <span class="sb-stat-label">累计盈亏</span>
          <span class="sb-stat-value" :class="cumulativeClass">
            {{ cumulativePnl >= 0 ? '+' : '' }}{{ cumulativePnl.toFixed(2) }} ({{ cumulativePct >= 0 ? '+' : '' }}{{ cumulativePct.toFixed(2) }}%)
          </span>
        </div>
        <div class="sb-stat">
          <span class="sb-stat-label">进度</span>
          <span class="sb-stat-value">{{ state.index + 1 }} / {{ state.totalBars }}</span>
        </div>
      </div>

      <!-- K线图 -->
      <div class="chart-section card" v-if="bars.length">
        <KLineChart :bars="bars" :height="360" :markers="chartMarkers" :startMarker="tradeStartDate" :drawMode="drawMode" />
      </div>

      <!-- 当前 Bar 信息 -->
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
          <span class="bar-val high">{{ currentBar.high?.toFixed(2) }}</span>
        </div>
        <div class="bar-item">
          <span class="bar-label">最低</span>
          <span class="bar-val low">{{ currentBar.low?.toFixed(2) }}</span>
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

      <!-- 控制区 -->
      <div class="controls-bar" v-if="!state.isDone">
        <button class="btn-advance" @click="doAdvance" :disabled="actionLoading">
          ⏭ 下一天
        </button>
        <button class="btn-draw" :class="{ active: drawMode }" @click="drawMode = !drawMode">
          📏 {{ drawMode ? '画线中…' : '画线' }}
        </button>

        <div class="trade-btns">
          <div class="trade-group">
            <button class="btn-buy" @click="openBuyModal" :disabled="actionLoading">
              🟢 买入
            </button>
            <input v-model.number="buyShares" type="number" class="shares-input" placeholder="股数" min="100" step="100" />
            <button class="btn-preset" @click="setBuyRatio(0.25)" :disabled="actionLoading">¼仓</button>
            <button class="btn-preset" @click="setBuyRatio(0.5)" :disabled="actionLoading">½仓</button>
            <button class="btn-preset" @click="setBuyRatio(0.75)" :disabled="actionLoading">¾仓</button>
            <button class="btn-preset" @click="setBuyRatio(1)" :disabled="actionLoading">满仓</button>
          </div>
          <div class="trade-group">
            <button class="btn-sell" @click="doSellAll" :disabled="actionLoading || state.shares <= 0">
              🔴 全卖
            </button>
            <input v-model.number="sellShares" type="number" class="shares-input" placeholder="部分" min="100" step="100" />
            <button class="btn-sell" @click="doSellPartial" :disabled="actionLoading || state.shares <= 0 || sellShares <= 0">
              部分卖
            </button>
          </div>
        </div>
      </div>

      <!-- 交易历史 -->
      <div class="trade-history card" v-if="trades.length">
        <h3>📋 交易记录 ({{ trades.length }})</h3>
        <div class="trade-table-wrap">
          <table class="trade-table">
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
      </div>

      <!-- 绩效报告 -->
      <div v-if="performance" class="performance card">
        <h3>📊 绩效报告</h3>
        <div class="perf-grid">
          <div class="perf-item">
            <span class="perf-label">总收益率</span>
            <span class="perf-value" :class="performance.total_return_pct >= 0 ? 'green' : 'red'">
              {{ performance.total_return_pct >= 0 ? '+' : '' }}{{ performance.total_return_pct.toFixed(2) }}%
            </span>
          </div>
          <div class="perf-item">
            <span class="perf-label">胜率</span>
            <span class="perf-value">{{ (performance.win_rate * 100).toFixed(0) }}%</span>
          </div>
          <div class="perf-item">
            <span class="perf-label">最大回撤</span>
            <span class="perf-value red">-{{ performance.max_drawdown_pct.toFixed(2) }}%</span>
          </div>
          <div class="perf-item">
            <span class="perf-label">总交易成本</span>
            <span class="perf-value">¥{{ performance.total_costs.toFixed(0) }}</span>
          </div>
          <div class="perf-item">
            <span class="perf-label">盈利交易</span>
            <span class="perf-value green">{{ performance.winning_trades }}</span>
          </div>
          <div class="perf-item">
            <span class="perf-label">亏损交易</span>
            <span class="perf-value red">{{ performance.losing_trades }}</span>
          </div>
          <div class="perf-item">
            <span class="perf-label">总交易</span>
            <span class="perf-value">{{ performance.total_trades }}</span>
          </div>
          <div class="perf-item">
            <span class="perf-label">最终资产</span>
            <span class="perf-value">¥{{ performance.total_value.toFixed(0) }}</span>
          </div>
        </div>
        <button class="btn-reset" @click="resetSandbox">🔄 新沙盒</button>
      </div>

      <!-- 买入弹窗 -->
      <div v-if="showBuyModal" class="modal-overlay" @click.self="showBuyModal = false">
        <div class="modal card">
          <h3>确认买入</h3>
          <p>以 <strong>{{ currentBar?.close?.toFixed(2) }}</strong> 元买入 <strong>{{ buyShares }}</strong> 股</p>
          <p class="modal-note">约 ¥{{ (buyShares * (currentBar?.close || 0)).toLocaleString() }}（不含手续费）</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showBuyModal = false">取消</button>
            <button class="btn-buy" @click="doBuy">确认买入</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  sandboxInit, getSandboxState, getSandboxBar,
  sandboxAdvance, sandboxBuy, sandboxSell,
  getSandboxPortfolio, getSandboxPerformance, getSandboxEquityCurve,
} from '../../api/sandbox'
import { getETFs, getETFName, getETFOHLCV } from '../../api/market'
import KLineChart from '../../components/KLineChart.vue'

export default {
  name: 'Sandbox',
  components: { KLineChart },
  data() {
    return {
      // Init
      etfList: [],
      etfNameMap: {},
      initETF: '',
      initTimeframe: 'day',
      initCash: 100000,
      startDate: '',
      availableDates: [],
      initLoading: false,

      // Session
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

      // UI
      actionLoading: false,
      showBuyModal: false,
      buyShares: 100,
      sellShares: 100,
    }
  },
  computed: {
    pnlClass() { return this.pnl >= 0 ? 'green' : 'red' },
    cumulativePnl() { return this.portfolioValue - this.initCash },
    cumulativePct() { return this.initCash > 0 ? (this.cumulativePnl / this.initCash) * 100 : 0 },
    cumulativeClass() { return this.cumulativePnl >= 0 ? 'green' : 'red' },
    chartMarkers() {
      return this.trades.map(t => ({ date: t.date, type: t.action, price: t.price }))
    },
    closeColor() {
      if (!this.currentBar || !this.bars.length) return ''
      const prev = this.bars.length >= 2 ? this.bars[this.bars.length - 2] : null
      if (!prev) return ''
      return this.currentBar.close >= prev.close ? 'green' : 'red'
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
          } catch (e) { /* ignore */ }
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
        // 加载 K 线数据：含起始日期前 30 根历史 K 线作为分析依据
        const limit = this.initTimeframe === 'day' ? 2000 : 500
        const ohlcvRes = await getETFOHLCV(this.initETF, this.initTimeframe, limit, 0)
        let loaded = ohlcvRes.data.bars || []
        this.preStartCount = 0
        if (this.startDate) {
          const startIdx = loaded.findIndex(b => b.date >= this.startDate)
          if (startIdx >= 0) {
            const historyCount = Math.min(startIdx, 30)  // 最多 30 根历史 K 线
            this.preStartCount = historyCount
            loaded = loaded.slice(startIdx - historyCount)  // 从历史起点开始
          }
        }
        this.allBars = loaded
        // 标记沙盒交易起点的日期
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
      if (!this.allBars.length) {
        this.bars = []
        return
      }
      // 图表显示：历史 K 线 + 当前沙盒进度
      const chartEnd = this.preStartCount + this.state.index + 1
      const end = Math.min(chartEnd, this.allBars.length)
      this.bars = this.allBars.slice(0, end)
    },
    async onStartDateChanged() {
      // 日期变更时预加载，留空即可从头开始
    },
    async loadAvailableDates() {
      if (!this.initETF) return
      try {
        // 只加载日期列表，limit=500 足够覆盖全部历史
        const res = await getETFOHLCV(this.initETF, this.initTimeframe, 500, 0)
        const allBars = res.data.bars || []
        this.availableDates = allBars
          .filter((_, i) => i % 20 === 0 || i === 0)
          .map(b => b.date)
      } catch (e) {
        console.error('加载可用日期失败:', e)
      }
    },
    async doAdvance() {
      this.actionLoading = true
      try {
        const res = await sandboxAdvance(this.sessionId)
        await this.refreshState()
        if (res.data.is_done) {
          await this.loadPerformance()
        }
      } catch (e) {
        alert('操作失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        this.actionLoading = false
      }
    },
    setBuyRatio(ratio) {
      // 快捷填入仓位：¼=25%资金, ½=50%, ¾=75%, 满仓=100%
      if (!this.currentBar) return
      const price = this.currentBar.close * 1.001  // 含滑点估算
      const cash = this.state.cash * ratio
      const shares = Math.floor(cash / price / 100) * 100
      this.buyShares = Math.max(shares, 0)
    },
    openBuyModal() {
      // 买入前校验
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
      } catch (e) {
        alert('买入失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        this.actionLoading = false
      }
    },
    async doSellAll() {
      this.actionLoading = true
      try {
        const res = await sandboxSell(this.sessionId, 0)  // 0 = 全部
        this.trades.push(res.data.trade)
        await this.refreshState()
        if (this.state.isDone) {
          await this.loadPerformance()
        }
      } catch (e) {
        alert('卖出失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        this.actionLoading = false
      }
    },
    async doSellPartial() {
      if (this.sellShares <= 0) {
        alert('请输入要卖出的股数')
        return
      }
      if (this.sellShares > this.state.shares) {
        alert(`持仓不足，最多卖出 ${this.state.shares} 股`)
        return
      }
      this.actionLoading = true
      try {
        const res = await sandboxSell(this.sessionId, this.sellShares)
        this.trades.push(res.data.trade)
        await this.refreshState()
        if (this.state.isDone) {
          await this.loadPerformance()
        }
      } catch (e) {
        alert('卖出失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        this.actionLoading = false
      }
    },
    async loadPerformance() {
      try {
        const res = await getSandboxPerformance(this.sessionId)
        this.performance = res.data
      } catch (e) {
        console.error('加载绩效失败:', e)
      }
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
.page-desc { font-size: 0.9rem; color: #6B6B7B; margin-bottom: 1.5rem; }
.breadcrumb { font-size: 0.78rem; color: #6B6B7B; margin-bottom: 1.2rem; }
.breadcrumb span { color: #F0B90B; }
.breadcrumb a { color: #6B6B7B; text-decoration: none; }
.breadcrumb strong { color: #F5F0E0; }

.card { background: #0D0D10; border: 1px solid #151518; border-radius: 10px; padding: 1.3rem; margin-bottom: 1rem; }

/* Init Panel */
.init-controls { display: flex; gap: 1.2rem; align-items: flex-end; flex-wrap: wrap; }
.control-group { display: flex; flex-direction: column; gap: 0.3rem; }
.control-group label { font-size: 0.72rem; color: #6B6B7B; letter-spacing: 0.05em; }
.styled-select, .styled-input {
  padding: 0.45rem 0.7rem; background: #0D0D10; border: 1px solid #151518;
  border-radius: 6px; color: #E8E6E3; font-size: 0.85rem; outline: none;
}
.styled-select:focus, .styled-input:focus { border-color: #F0B90B44; }
.styled-input { width: 120px; }

.btn-primary {
  padding: 0.5rem 1.5rem; background: #F0B90B; color: #0A0A0B;
  border: none; border-radius: 6px; font-size: 0.9rem; font-weight: 500; cursor: pointer;
}
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

/* Status Bar */
.sb-status-bar { display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
.sb-stat {
  flex: 1; min-width: 100px; background: #0D0D10; border: 1px solid #151518;
  border-radius: 8px; padding: 0.7rem 0.9rem;
}
.sb-stat-label { display: block; font-size: 0.65rem; color: #6B6B7B; letter-spacing: 0.08em; margin-bottom: 0.2rem; }
.sb-stat-value { font-size: 1.1rem; font-weight: 400; color: #E8E6E3; }
.sb-stat-value.cash { color: #4ADE80; }
.sb-stat-value.total { color: #F0B90B; }

/* Bar Info */
.bar-info { display: flex; gap: 1rem; margin: 0.8rem 0; flex-wrap: wrap; }
.bar-item { display: flex; flex-direction: column; min-width: 80px; }
.bar-label { font-size: 0.65rem; color: #6B6B7B; letter-spacing: 0.05em; }
.bar-val { font-size: 0.95rem; color: #E8E6E3; }
.bar-val.high { color: #EF5350; }
.bar-val.low { color: #4ADE80; }

/* Controls */
.controls-bar { display: flex; gap: 1rem; align-items: center; margin: 1rem 0; flex-wrap: wrap; }
.trade-btns { display: flex; gap: 0.8rem; align-items: center; }
.trade-group { display: flex; gap: 0.4rem; align-items: center; }
.shares-input {
  width: 80px; padding: 0.4rem; background: #0D0D10; border: 1px solid #151518;
  border-radius: 6px; color: #E8E6E3; font-size: 0.82rem; outline: none;
}
.btn-preset {
  padding: 0.3rem 0.45rem; border: 1px solid #2A2A2D; border-radius: 4px;
  background: transparent; color: #999; font-size: 0.7rem; cursor: pointer; transition: all 0.15s;
}
.btn-preset:hover { background: #F0B90B15; border-color: #F0B90B44; color: #F0B90B; }
.btn-draw { padding: 0.45rem 0.8rem; border-radius: 6px; font-size: 0.82rem; cursor: pointer; border: 1px solid #F0B90B44; background: transparent; color: #F0B90B; transition: all 0.2s; }
.btn-draw:hover { background: #F0B90B22; }
.btn-draw.active { background: #F0B90B33; border-color: #F0B90B; }
.btn-advance, .btn-buy, .btn-sell, .btn-reset, .btn-cancel {
  padding: 0.45rem 1rem; border-radius: 6px; font-size: 0.85rem; cursor: pointer; border: none; transition: opacity 0.2s;
}
.btn-advance { background: #F0B90B; color: #0A0A0B; }
.btn-buy { background: #166534; color: #4ADE80; }
.btn-sell { background: #7F1D1D; color: #FCA5A5; }
.btn-reset { background: transparent; color: #F0B90B; border: 1px solid #F0B90B44; margin-top: 1rem; }
.btn-cancel { background: #1A1A1D; color: #A0A0A8; margin-right: 0.5rem; }
.btn-advance:disabled, .btn-buy:disabled, .btn-sell:disabled { opacity: 0.4; cursor: not-allowed; }

/* Trade Table */
.trade-table-wrap { overflow-x: auto; }
.trade-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.trade-table th { background: #141417; color: #6B6B7B; padding: 0.4rem 0.5rem; text-align: left; font-weight: 400; border: 1px solid #1A1A1D; }
.trade-table td { padding: 0.35rem 0.5rem; color: #C8C6C3; border: 1px solid #1A1A1D; }
.row-buy td { color: #4ADE80; }
.row-sell td { color: #FCA5A5; }

/* Performance */
.perf-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 0.6rem; margin-bottom: 1rem; }
.perf-item { background: #0A0A0B; border: 1px solid #151518; border-radius: 6px; padding: 0.6rem 0.8rem; }
.perf-label { display: block; font-size: 0.65rem; color: #6B6B7B; margin-bottom: 0.2rem; }
.perf-value { font-size: 1.05rem; color: #E8E6E3; font-weight: 400; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: #00000088; display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { max-width: 420px; width: 90%; }
.modal-note { font-size: 0.78rem; color: #6B6B7B; margin-top: 0.3rem; }
.modal-actions { display: flex; justify-content: flex-end; margin-top: 1rem; }

.green { color: #4ADE80 !important; }
.red { color: #EF5350 !important; }

.empty-state { padding: 3rem; text-align: center; color: #6B6B7B; }
</style>
