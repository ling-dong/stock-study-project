<template>
  <div class="lab-page ia-page">
    <IAPageHeader
      :title="labTitle"
      subtitle="探索真实的 ETF 市场数据"
      :breadcrumbs="[{ label: '首页', to: '/' }, { label: '实践轨道' }, { label: labTitle }]"
    />

    <IAPanel v-if="labGuide" title="实验指南" icon="book">
      <MarkdownViewer :content="labGuide" />
    </IAPanel>

    <IASectionTitle icon="market" title="可用 ETF 数据总览" />
    <div class="ia-table-wrapper" v-if="etfMeta.length">
      <table class="ia-table">
        <thead>
          <tr><th>代码</th><th>交易所</th><th>名称</th><th>行数</th><th>起止日期</th></tr>
        </thead>
        <tbody>
          <tr v-for="row in etfMeta" :key="row.code">
            <td class="ia-table__code">{{ row.code }}</td>
            <td>{{ row.market }}</td>
            <td>{{ etfNameMap[row.code] || '' }}</td>
            <td>{{ row.rows }}</td>
            <td>{{ row.start_date }} ~ {{ row.end_date }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="ia-empty">未找到 ETF 数据文件</div>

    <IASectionTitle icon="chart" title="ETF 数据浏览器" />
    <IAPanel title="图表控制" icon="tool">
      <div class="browser-controls">
        <div class="ia-form-group">
          <label class="ia-label">选择 ETF</label>
          <select v-model="selectedETF" @change="loadChart" class="ia-select">
            <option v-for="etf in etfList" :key="etf.code" :value="etf.code">{{ formatETFLabel(etf.code) }}</option>
          </select>
        </div>
        <div class="ia-form-group">
          <label class="ia-label">时间框架</label>
          <select v-model="timeframe" @change="loadChart" class="ia-select">
            <option value="day">日线</option>
            <option value="5min">5分钟</option>
          </select>
        </div>
      </div>
    </IAPanel>

    <div v-if="bars.length" class="chart-section">
      <KLineChart :bars="bars" :height="420" />
      <p class="chart-info">共 {{ bars.length }} 条数据 · {{ timeframe === 'day' ? '最近180天' : '最近300条' }}</p>
    </div>
    <div v-else-if="loadingChart" class="ia-loading">加载图表数据…</div>

    <div v-if="rawData.length" class="raw-data-section">
      <IASectionTitle icon="grid" title="原始数据（最近 30 条）" />
      <div class="ia-table-wrapper">
        <table class="ia-table">
          <thead>
            <tr><th>日期</th><th>开盘</th><th>最高</th><th>最低</th><th>收盘</th><th>成交量</th></tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in rawData" :key="i" :class="row.close >= row.open ? 'ia-table__up' : 'ia-table__down'">
              <td class="ia-table__code">{{ row.date }}</td>
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
import { IAPageHeader, IAPanel, IASectionTitle, IAIcon } from '../../components/ui'
import { getETFs, getETFMetadata, getETFOHLCV, getETFName } from '../../api/market'
import { getLab } from '../../api/content'
import MarkdownViewer from '../../components/MarkdownViewer.vue'
import KLineChart from '../../components/KLineChart.vue'

const LAB_TITLES = {
  m1_data_lab: 'M1: 数据勘探实验室',
  m2_feature_lab: 'M2: 特征工程实验室',
}

export default {
  name: 'PracticeLab',
  components: { IAPageHeader, IAPanel, IASectionTitle, IAIcon, MarkdownViewer, KLineChart },
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
  computed: {
    labTitle() { return LAB_TITLES[this.labId] || this.labId },
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
        for (const etf of this.etfList) {
          try {
            const nameRes = await getETFName(etf.code)
            this.$set(this.etfNameMap, etf.code, nameRes.data.display_name)
          } catch (e) {}
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
.browser-controls {
  display: flex;
  gap: var(--ia-space-lg);
  flex-wrap: wrap;
}

.chart-section {
  margin-top: var(--ia-space-md);
}

.chart-info {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
  margin-top: 0.3rem;
  text-align: right;
}

.raw-data-section {
  margin-top: var(--ia-space-xl);
}
</style>
