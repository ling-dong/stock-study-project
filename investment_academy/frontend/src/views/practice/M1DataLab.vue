<template>
  <div class="lab-page">
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <router-link to="/">首页</router-link>
      <span> / </span>
      <span><strong>M1: 数据勘探实验室</strong></span>
    </div>

    <h1>🔬 M1: 数据勘探实验室</h1>
    <p class="lab-desc">探索真实的 ETF 市场数据</p>

    <!-- 实验指南 -->
    <div v-if="labGuide" class="lab-guide card">
      <h3>📖 实验指南</h3>
      <MarkdownViewer :content="labGuide" />
    </div>

    <!-- ETF 数据总览 -->
    <h2>📊 可用 ETF 数据总览</h2>
    <div v-if="etfMeta.length" class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>代码</th>
            <th>交易所</th>
            <th>名称</th>
            <th>行数</th>
            <th>起止日期</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in etfMeta" :key="row.code">
            <td class="code-cell">{{ row.code }}</td>
            <td>{{ row.market }}</td>
            <td>{{ etfNameMap[row.code] || '' }}</td>
            <td>{{ row.rows }}</td>
            <td>{{ row.start_date }} ~ {{ row.end_date }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="empty-state">
      <p>未找到 ETF 数据文件</p>
    </div>

    <!-- ETF 数据浏览器 -->
    <h2>🔍 ETF 数据浏览器</h2>
    <div class="browser-controls">
      <div class="control-group">
        <label>选择 ETF</label>
        <select v-model="selectedETF" @change="loadChart" class="styled-select">
          <option v-for="etf in etfList" :key="etf.code" :value="etf.code">
            {{ formatETFLabel(etf.code) }}
          </option>
        </select>
      </div>
      <div class="control-group">
        <label>时间框架</label>
        <select v-model="timeframe" @change="loadChart" class="styled-select">
          <option value="day">日线</option>
          <option value="5min">5分钟</option>
        </select>
      </div>
    </div>

    <!-- K 线图 -->
    <div v-if="bars.length" class="chart-section">
      <KLineChart :bars="bars" :height="420" />
      <p class="chart-info">共 {{ bars.length }} 条数据 · {{ timeframe === 'day' ? '最近180天' : '最近300条' }}</p>
    </div>
    <div v-else-if="loadingChart" class="loading">加载图表数据…</div>

    <!-- 原始数据表格 -->
    <div v-if="rawData.length" class="raw-data-section">
      <h3>📋 原始数据（最近 30 条）</h3>
      <div class="data-table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>日期</th>
              <th>开盘</th>
              <th>最高</th>
              <th>最低</th>
              <th>收盘</th>
              <th>成交量</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in rawData" :key="i"
                :class="{ 'row-up': row.close >= row.open, 'row-down': row.close < row.open }">
              <td>{{ row.date }}</td>
              <td>{{ row.open?.toFixed(2) }}</td>
              <td>{{ row.high?.toFixed(2) }}</td>
              <td>{{ row.low?.toFixed(2) }}</td>
              <td>{{ row.close?.toFixed(2) }}</td>
              <td>{{ formatVolume(row.volume) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { getETFs, getETFMetadata, getETFOHLCV, getETFName } from '../../api/market'
import { getLab } from '../../api/content'
import MarkdownViewer from '../../components/MarkdownViewer.vue'
import KLineChart from '../../components/KLineChart.vue'

export default {
  name: 'M1DataLab',
  components: { MarkdownViewer, KLineChart },
  props: {
    labId: { type: String, default: 'm1_data_lab' },
  },
  data() {
    return {
      labGuide: null,
      etfList: [],
      etfMeta: [],
      etfNameMap: {},
      selectedETF: '',
      timeframe: 'day',
      bars: [],
      rawData: [],
      loadingChart: false,
    }
  },
  async created() {
    try {
      const [labRes, etfsRes, metaRes] = await Promise.all([
        getLab(this.labId),
        getETFs(),
        getETFMetadata(),
      ])

      this.labGuide = labRes.data?.guide || null
      this.etfList = etfsRes.data || []
      this.etfMeta = metaRes.data || []

      if (this.etfList.length) {
        this.selectedETF = this.etfList[0].code
        // 加载所有 ETF 名称
        for (const etf of this.etfList) {
          try {
            const nameRes = await getETFName(etf.code)
            this.$set(this.etfNameMap, etf.code, nameRes.data.display_name)
          } catch (e) { /* ignore */ }
        }
        this.loadChart()
      }
    } catch (e) {
      console.error('加载实验室失败:', e)
    }
  },
  methods: {
    formatETFLabel(code) {
      const name = this.etfNameMap[code]
      if (name && name !== code) return name
      return code
    },
    async loadChart() {
      if (!this.selectedETF) return
      this.loadingChart = true
      this.bars = []
      this.rawData = []
      try {
        const limit = this.timeframe === 'day' ? 180 : 300
        const res = await getETFOHLCV(this.selectedETF, this.timeframe, limit)
        const allBars = res.data.bars || []
        this.bars = allBars
        // 取最后 30 条作为原始数据展示
        this.rawData = allBars.slice(-30).reverse()
      } catch (e) {
        console.error('加载图表数据失败:', e)
      } finally {
        this.loadingChart = false
      }
    },
    formatVolume(v) {
      if (!v) return '0'
      if (v >= 1e8) return (v / 1e8).toFixed(2) + '亿'
      if (v >= 1e4) return (v / 1e4).toFixed(1) + '万'
      return v.toLocaleString()
    },
  },
}
</script>

<style scoped>
.lab-desc {
  font-size: 0.9rem;
  color: #6B6B7B;
  margin-bottom: 1.5rem;
}

.breadcrumb {
  font-size: 0.78rem;
  color: #6B6B7B;
  margin-bottom: 1.2rem;
  letter-spacing: 0.05em;
}

.breadcrumb span {
  color: #F0B90B;
}

.breadcrumb a {
  color: #6B6B7B;
  text-decoration: none;
}

.breadcrumb strong {
  color: #F5F0E0;
}

.lab-guide {
  margin-bottom: 2rem;
}

.data-table-wrapper {
  overflow-x: auto;
  margin-bottom: 2rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}

.data-table th {
  background: #141417;
  color: #F0B90B;
  padding: 0.55rem 0.7rem;
  text-align: left;
  font-weight: 400;
  border: 1px solid #1A1A1D;
}

.data-table td {
  padding: 0.45rem 0.7rem;
  border: 1px solid #1A1A1D;
  color: #C8C6C3;
}

.code-cell {
  font-family: 'SF Mono', 'Consolas', monospace;
  color: #F0B90B;
}

.browser-controls {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.2rem;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.control-group label {
  font-size: 0.75rem;
  color: #6B6B7B;
  letter-spacing: 0.05em;
}

.styled-select {
  padding: 0.45rem 0.7rem;
  background: #0D0D10;
  border: 1px solid #151518;
  border-radius: 6px;
  color: #E8E6E3;
  font-size: 0.85rem;
  min-width: 220px;
  cursor: pointer;
  outline: none;
}

.styled-select:focus {
  border-color: #F0B90B44;
}

.styled-select option {
  background: #0D0D10;
  color: #E8E6E3;
}

.chart-section {
  margin-top: 1rem;
}

.chart-info {
  font-size: 0.72rem;
  color: #6B6B7B;
  margin-top: 0.3rem;
  text-align: right;
}

.loading {
  padding: 3rem;
  text-align: center;
  color: #6B6B7B;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: #6B6B7B;
}

.raw-data-section {
  margin-top: 1.5rem;
}

.raw-data-section h3 {
  font-size: 1rem;
  margin-bottom: 0.6rem;
}

.row-up {
  background: #0A2E0A11;
}

.row-down {
  background: #2E0A0A11;
}
</style>
