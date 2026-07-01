<template>
  <div class="kline-chart" ref="chartContainer" :style="{ width: '100%', height: height + 'px' }"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'KLineChart',
  props: {
    bars: { type: Array, default: () => [] },
    height: { type: Number, default: 400 },
    markers: { type: Array, default: () => [] },
  },
  data() {
    return { chart: null }
  },
  watch: {
    bars: {
      handler() { this.renderChart() },
      deep: true,
    },
    markers: {
      handler() { this.renderChart() },
      deep: true,
    },
  },
  mounted() {
    this.$nextTick(() => {
      if (!this.$refs.chartContainer) return
      // 拿到 DOM 实际尺寸初始化
      const w = this.$refs.chartContainer.clientWidth
      const h = this.$refs.chartContainer.clientHeight
      this.chart = echarts.init(this.$refs.chartContainer, null, {
        width: w || undefined,
        height: h || this.height,
        backgroundColor: 'transparent',
      })
      this.renderChart()
      window.addEventListener('resize', this.handleResize)
    })
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    if (this.chart) { this.chart.dispose(); this.chart = null }
  },
  methods: {
    handleResize() {
      if (this.chart) this.chart.resize()
    },
    renderChart() {
      if (!this.chart || !this.bars.length) return

      const dates = this.bars.map(b => b.date)
      // ECharts candlestick: [open, close, lowest, highest]
      const ohlc = this.bars.map(b => [b.open, b.close, b.low, b.high])
      const volumes = this.bars.map(b => b.volume)

      // 均线
      const calcMA = (period) => {
        const result = []
        for (let i = 0; i < this.bars.length; i++) {
          if (i < period - 1) { result.push(null); continue }
          let sum = 0
          for (let j = 0; j < period; j++) sum += +this.bars[i - j].close
          result.push(+(sum / period).toFixed(3))
        }
        return result
      }

      const ma5 = calcMA(5)
      const ma10 = calcMA(10)
      const ma20 = calcMA(20)

      // X 轴标签间隔
      const n = this.bars.length
      const labelInterval = n > 50 ? Math.floor(n / 8) : 0

      const option = {
        animation: false,
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' },
          backgroundColor: '#0D0D10EE',
          borderColor: '#F0B90B44',
          textStyle: { color: '#E8E6E3', fontSize: 11 },
        },
        legend: {
          data: ['MA5', 'MA10', 'MA20'],
          top: 0, left: 'center',
          textStyle: { color: '#999', fontSize: 10 },
          itemWidth: 14, itemHeight: 2,
        },
        grid: [
          { left: '2%', right: '3%', top: 28, height: '58%' },
          { left: '2%', right: '3%', top: '70%', height: '16%' },
        ],
        xAxis: [
          {
            type: 'category', data: dates, gridIndex: 0,
            axisLine: { lineStyle: { color: '#1A1A1D' } },
            axisTick: { show: false },
            axisLabel: { color: '#666', fontSize: 9, interval: labelInterval },
          },
          {
            type: 'category', data: dates, gridIndex: 1,
            axisLine: { lineStyle: { color: '#1A1A1D' } },
            axisTick: { show: false },
            axisLabel: { show: false },
          },
        ],
        yAxis: [
          {
            gridIndex: 0,
            scale: true,
            position: 'right',
            axisLine: { show: false },
            axisTick: { show: false },
            axisLabel: { color: '#888', fontSize: 9 },
            splitLine: { lineStyle: { color: '#151518' } },
          },
          {
            gridIndex: 1,
            axisLine: { show: false },
            axisTick: { show: false },
            axisLabel: { color: '#666', fontSize: 8 },
            splitLine: { show: false },
          },
        ],
        series: [
          // ── K 线蜡烛 ──
          {
            type: 'candlestick',
            data: ohlc,
            xAxisIndex: 0,
            yAxisIndex: 0,
            barMaxWidth: 12,
            barMinWidth: 3,
            itemStyle: {
              color: '#CF2A2A',
              color0: '#1B8E3F',
              borderColor: '#CF2A2A',
              borderColor0: '#1B8E3F',
              borderWidth: 1.5,
            },
          },
          // ── MA5 白 ──
          {
            name: 'MA5', type: 'line',
            data: ma5,
            xAxisIndex: 0, yAxisIndex: 0,
            showSymbol: false, smooth: false,
            lineStyle: { color: '#ECECEC', width: 1 },
          },
          // ── MA10 黄 ──
          {
            name: 'MA10', type: 'line',
            data: ma10,
            xAxisIndex: 0, yAxisIndex: 0,
            showSymbol: false, smooth: false,
            lineStyle: { color: '#F0B90B', width: 1 },
          },
          // ── MA20 紫 ──
          {
            name: 'MA20', type: 'line',
            data: ma20,
            xAxisIndex: 0, yAxisIndex: 0,
            showSymbol: false, smooth: false,
            lineStyle: { color: '#B983FF', width: 1 },
          },
          // ── 成交量柱 ──
          {
            type: 'bar',
            data: volumes,
            xAxisIndex: 1, yAxisIndex: 1,
            barMaxWidth: 12,
            itemStyle: {
              color: (params) => {
                const i = params.dataIndex
                return this.bars[i].close >= this.bars[i].open ? '#CF2A2A55' : '#1B8E3F55'
              },
            },
          },
        ],
      }

      // 买卖标记
      if (this.markers.length) {
        const buys = this.markers.filter(m => m.type === 'buy')
        const sells = this.markers.filter(m => m.type === 'sell')
        if (buys.length) {
          option.series.push({
            type: 'scatter', name: '买入',
            data: buys.map(m => [m.date, m.price]),
            xAxisIndex: 0, yAxisIndex: 0,
            symbol: 'triangle', symbolSize: 10, symbolRotate: 0,
            itemStyle: { color: '#CF2A2A' },
          })
        }
        if (sells.length) {
          option.series.push({
            type: 'scatter', name: '卖出',
            data: sells.map(m => [m.date, m.price]),
            xAxisIndex: 0, yAxisIndex: 0,
            symbol: 'triangle', symbolSize: 10, symbolRotate: 180,
            itemStyle: { color: '#1B8E3F' },
          })
        }
      }

      this.chart.setOption(option, true)
    },
  },
}
</script>

<style scoped>
.kline-chart {
  width: 100%;
}
</style>
