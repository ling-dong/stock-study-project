<template>
  <div class="kline-chart" ref="chartContainer"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'KLineChart',
  props: {
    bars: { type: Array, default: () => [] },
    height: { type: Number, default: 400 },
  },
  data() {
    return {
      chart: null,
    }
  },
  watch: {
    bars: {
      handler() { this.renderChart() },
      deep: true,
    },
  },
  mounted() {
    this.chart = echarts.init(this.$refs.chartContainer, null, {
      backgroundColor: 'transparent',
    })
    this.renderChart()
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    if (this.chart) this.chart.dispose()
  },
  methods: {
    handleResize() {
      if (this.chart) this.chart.resize()
    },
    renderChart() {
      if (!this.chart || !this.bars.length) return

      const dates = this.bars.map(b => b.date)
      const ohlc = this.bars.map(b => [b.open, b.close, b.low, b.high])
      const volumes = this.bars.map(b => b.volume)

      // 计算 MA
      const calcMA = (period) => {
        const result = []
        for (let i = 0; i < this.bars.length; i++) {
          if (i < period - 1) { result.push(null); continue }
          let sum = 0
          for (let j = 0; j < period; j++) sum += this.bars[i - j].close
          result.push(sum / period)
        }
        return result
      }

      const option = {
        grid: [
          { left: '8%', right: '3%', top: '2%', height: '65%' },
          { left: '8%', right: '3%', top: '75%', height: '20%' },
        ],
        xAxis: [
          {
            type: 'category',
            data: dates,
            axisLine: { lineStyle: { color: '#1A1A1D' } },
            axisLabel: { color: '#6B6B7B', fontSize: 10 },
            gridIndex: 0,
          },
          {
            type: 'category',
            data: dates,
            axisLine: { lineStyle: { color: '#1A1A1D' } },
            axisLabel: { show: false },
            gridIndex: 1,
          },
        ],
        yAxis: [
          {
            type: 'value',
            scale: true,
            axisLine: { lineStyle: { color: '#1A1A1D' } },
            axisLabel: { color: '#6B6B7B', fontSize: 10 },
            splitLine: { lineStyle: { color: '#151518' } },
            gridIndex: 0,
          },
          {
            type: 'value',
            axisLine: { lineStyle: { color: '#1A1A1D' } },
            axisLabel: { color: '#6B6B7B', fontSize: 10 },
            splitLine: { show: false },
            gridIndex: 1,
          },
        ],
        series: [
          {
            type: 'candlestick',
            data: ohlc,
            itemStyle: {
              color: '#26A69A',
              color0: '#EF5350',
              borderColor: '#26A69A',
              borderColor0: '#EF5350',
            },
            gridIndex: 0,
          },
          {
            type: 'line',
            data: calcMA(5),
            smooth: true,
            showSymbol: false,
            lineStyle: { color: '#F0B90B', width: 1, type: 'dashed' },
            gridIndex: 0,
          },
          {
            type: 'line',
            data: calcMA(10),
            smooth: true,
            showSymbol: false,
            lineStyle: { color: '#FF6B6B', width: 1, type: 'dashed' },
            gridIndex: 0,
          },
          {
            type: 'line',
            data: calcMA(20),
            smooth: true,
            showSymbol: false,
            lineStyle: { color: '#4ECDC4', width: 1, type: 'dashed' },
            gridIndex: 0,
          },
          {
            type: 'bar',
            data: volumes,
            itemStyle: {
              color: (params) => {
                const idx = params.dataIndex
                return this.bars[idx].close >= this.bars[idx].open ? '#26A69A44' : '#EF535044'
              },
            },
            gridIndex: 1,
          },
        ],
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
