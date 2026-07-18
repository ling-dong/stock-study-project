<template>
  <div>
    <div class="kline-chart" ref="chartContainer" :style="{ width: '100%', height: height + 'px' }"></div>
    <div v-if="drawnLines.length" class="draw-legend">
      <span class="legend-hint">📏 已画线: {{ drawnLines.length }} 条</span>
      <button class="btn-clear-lines" @click="clearLines">清空</button>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'KLineChart',
  props: {
    bars: { type: Array, default: () => [] },
    height: { type: Number, default: 400 },
    markers: { type: Array, default: () => [] },
    startMarker: { type: String, default: null },   // 交易起点日期，画红色竖线标记
    drawMode: { type: Boolean, default: false },     // 画线模式
  },
  data() {
    return {
      chart: null,
      drawnLines: [],      // [{id, date1, price1, date2, price2}]
      pendingPoint: null,  // 画线模式中第一个点
    }
  },
  watch: {
    bars: { handler() { this.renderChart() }, deep: true },
    markers: { handler() { this.renderChart() }, deep: true },
    startMarker() { this.renderChart() },
    drawMode(val) {
      if (!val) this.pendingPoint = null   // 关闭画线时清除半成品
    },
  },
  mounted() {
    this.$nextTick(() => {
      if (!this.$refs.chartContainer) return
      const w = this.$refs.chartContainer.clientWidth
      const h = this.$refs.chartContainer.clientHeight
      this.chart = echarts.init(this.$refs.chartContainer, null, {
        width: w || undefined, height: h || this.height, backgroundColor: 'transparent',
      })
      this._bindDrawEvents()
      this.renderChart()
      window.addEventListener('resize', this.handleResize)
    })
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    if (this.chart) { this.chart.dispose(); this.chart = null }
  },
  methods: {
    handleResize() { if (this.chart) this.chart.resize() },

    // ── 画线事件绑定 ──
    _bindDrawEvents() {
      this.chart.off('click')
      this.chart.on('click', (params) => {
        if (!this.drawMode) return
        // 只响应价格图区域（gridIndex:0），忽略成交量子图
        if (params.seriesIndex !== undefined && this.chart.getOption().series[params.seriesIndex]?.xAxisIndex !== 0) return
        if (params.dataIndex === undefined && params.xAxisIndex !== 0) return
        let date, price
        if (params.dataIndex !== undefined && this.bars[params.dataIndex]) {
          date = this.bars[params.dataIndex].date
          price = params.value
          if (Array.isArray(price)) price = price[1]  // candlestick returns [open,close,low,high]
          if (price === undefined || price === null) price = this.bars[params.dataIndex].close
        }
        if (!date) return
        this._addDrawPoint(date, price || this.bars[0].close)
      })
    },
    _addDrawPoint(date, price) {
      if (!this.pendingPoint) {
        this.pendingPoint = { date, price }
        this.renderChart()  // 立即显示锚点
      } else {
        // 防止画点到同一个位置（无意义的线）
        if (this.pendingPoint.date === date && Math.abs(this.pendingPoint.price - price) < 0.001) {
          this.pendingPoint = null
          this.renderChart()
          return
        }
        const line = {
          id: Date.now(),
          date1: this.pendingPoint.date, price1: this.pendingPoint.price,
          date2: date, price2: price,
        }
        this.drawnLines.push(line)
        this.pendingPoint = null
        this.renderChart()
      }
    },
    clearLines() {
      this.drawnLines = []
      this.pendingPoint = null
      this.renderChart()
    },

    // ── 图表渲染 ──
    renderChart() {
      if (!this.chart || !this.bars.length) return

      const dates = this.bars.map(b => b.date)
      const ohlc = this.bars.map(b => [b.open, b.close, b.low, b.high])
      const volumes = this.bars.map(b => b.volume)

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

      const n = this.bars.length
      const labelInterval = n > 50 ? Math.floor(n / 8) : 0
      // 数据少时显示全部，数据多时默认显示最近 60 根
      const dataZoomEnd = n <= 60 ? 100 : 100
      const dataZoomStart = n <= 60 ? 0 : Math.max(0, 100 - (60 / n) * 100)

      const option = {
        animation: false,
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' },
          backgroundColor: '#0D0D10EE', borderColor: '#F0B90B44',
          textStyle: { color: '#E8E6E3', fontSize: 11 },
        },
        legend: {
          data: ['MA5', 'MA10', 'MA20'],
          top: 0, left: 'center',
          textStyle: { color: '#999', fontSize: 10 },
          itemWidth: 14, itemHeight: 2,
        },
        grid: [
          { left: '2%', right: '3%', top: 28, height: '55%' },
          { left: '2%', right: '3%', top: '68%', height: '14%' },
        ],
        dataZoom: [
          {
            type: 'inside',
            xAxisIndex: [0, 1],
            start: dataZoomStart,
            end: dataZoomEnd,
            zoomOnMouseWheel: true,
            moveOnMouseMove: true,
            moveOnMouseWheel: false,
          },
          {
            type: 'slider',
            xAxisIndex: [0, 1],
            start: dataZoomStart,
            end: dataZoomEnd,
            height: 22,
            bottom: 2,
            borderColor: '#1A1A1D',
            backgroundColor: '#0D0D10',
            fillerColor: '#F0B90B22',
            handleStyle: { color: '#F0B90B', width: 6 },
            textStyle: { color: '#6B6B7B', fontSize: 9 },
            showDetail: false,
          },
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
            axisTick: { show: false }, axisLabel: { show: false },
          },
        ],
        yAxis: [
          {
            gridIndex: 0, scale: true, position: 'right',
            axisLine: { show: false }, axisTick: { show: false },
            axisLabel: { color: '#888', fontSize: 9 },
            splitLine: { lineStyle: { color: '#151518' } },
          },
          {
            gridIndex: 1,
            axisLine: { show: false }, axisTick: { show: false },
            axisLabel: { color: '#666', fontSize: 8 },
            splitLine: { show: false },
          },
        ],
        series: [
          { type: 'candlestick', data: ohlc, xAxisIndex: 0, yAxisIndex: 0,
            barMaxWidth: 12, barMinWidth: 3,
            itemStyle: {
              color: '#CF2A2A', color0: '#1B8E3F',
              borderColor: '#CF2A2A', borderColor0: '#1B8E3F',
              borderWidth: 1.5,
            },
          },
          { name: 'MA5', type: 'line', data: calcMA(5), xAxisIndex: 0, yAxisIndex: 0,
            showSymbol: false, smooth: false, lineStyle: { color: '#ECECEC', width: 1 },
          },
          { name: 'MA10', type: 'line', data: calcMA(10), xAxisIndex: 0, yAxisIndex: 0,
            showSymbol: false, smooth: false, lineStyle: { color: '#F0B90B', width: 1 },
          },
          { name: 'MA20', type: 'line', data: calcMA(20), xAxisIndex: 0, yAxisIndex: 0,
            showSymbol: false, smooth: false, lineStyle: { color: '#B983FF', width: 1 },
          },
          { type: 'bar', data: volumes, xAxisIndex: 1, yAxisIndex: 1, barMaxWidth: 12,
            itemStyle: { color: (p) => {
              const i = p.dataIndex
              return this.bars[i].close >= this.bars[i].open ? '#CF2A2A55' : '#1B8E3F55'
            }},
          },
        ],
      }

      // 交易起点红色竖虚线
      if (this.startMarker) {
        const smIdx = dates.indexOf(this.startMarker)
        if (smIdx >= 0) {
          option.series[0].markLine = {
            silent: true, symbol: 'none',
            lineStyle: { color: '#F0B90B', type: 'dashed', width: 1.5 },
            label: { show: true, formatter: '交易起点', position: 'start',
                     color: '#F0B90B', fontSize: 10 },
            data: [{ xAxis: this.startMarker }],
          }
        }
      }

      // 用户画的线
      if (this.drawnLines.length) {
        this.drawnLines.forEach(line => {
          option.series.push({
            type: 'line', name: '画线',
            data: [
              [line.date1, line.price1],
              [line.date2, line.price2],
            ],
            xAxisIndex: 0, yAxisIndex: 0,
            showSymbol: true, symbol: 'circle', symbolSize: 6,
            lineStyle: { color: '#FF9800', width: 1.5, type: 'solid' },
            itemStyle: { color: '#FF9800' },
            silent: true,
            z: 10,
          })
        })
      }

      // 画笔等待中的第一个点
      if (this.pendingPoint) {
        option.series.push({
          type: 'scatter', name: '画笔',
          data: [[this.pendingPoint.date, this.pendingPoint.price]],
          xAxisIndex: 0, yAxisIndex: 0,
          symbol: 'pin', symbolSize: 30,
          itemStyle: { color: '#FF9800' },
          silent: true, z: 11,
        })
      }

      // 买卖标记
      if (this.markers.length) {
        const buys = this.markers.filter(m => m.type === 'buy')
        const sells = this.markers.filter(m => m.type === 'sell')
        if (buys.length) {
          option.series.push({
            type: 'scatter', name: '买入', xAxisIndex: 0, yAxisIndex: 0,
            data: buys.map(m => [m.date, m.price]),
            symbol: 'triangle', symbolSize: 10, symbolRotate: 0,
            itemStyle: { color: '#CF2A2A' }, z: 9,
          })
        }
        if (sells.length) {
          option.series.push({
            type: 'scatter', name: '卖出', xAxisIndex: 0, yAxisIndex: 0,
            data: sells.map(m => [m.date, m.price]),
            symbol: 'triangle', symbolSize: 10, symbolRotate: 180,
            itemStyle: { color: '#1B8E3F' }, z: 9,
          })
        }
      }

      // 保存当前缩放位置，setOption 后恢复（防止点击"下一天"时缩放被重置）
      let savedZoom = null
      if (this._dataZoomSet) {
        try {
          const opt = this.chart.getOption()
          if (opt.dataZoom && opt.dataZoom.length) {
            savedZoom = opt.dataZoom.map(d => ({ start: d.start, end: d.end }))
          }
        } catch (e) { /* ignore */ }
      }

      this.chart.setOption(option, true)

      if (savedZoom) {
        savedZoom.forEach((z, i) => {
          try {
            this.chart.dispatchAction({ type: 'dataZoom', start: z.start, end: z.end })
          } catch (e) { /* ignore */ }
        })
      }
      this._dataZoomSet = true
    },
  },
}
</script>

<style scoped>
.kline-chart { width: 100%; }
.draw-legend {
  display: flex; align-items: center; justify-content: flex-end; gap: 0.5rem;
  padding: 0.3rem 0.5rem; font-size: 0.72rem;
}
.legend-hint { color: #FF9800; }
.btn-clear-lines {
  background: transparent; color: #EF5350; border: 1px solid #EF535044;
  border-radius: 4px; padding: 0.15rem 0.5rem; font-size: 0.7rem; cursor: pointer;
}
.btn-clear-lines:hover { background: #EF535022; }
</style>
