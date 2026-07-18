<template>
  <div class="spas ia-page">
    <IAPageHeader
      title="SPAS"
      title-highlight="交易分析"
      subtitle="用户输入指标 + 系统合成决策"
      :breadcrumbs="[{ label: '首页', to: '/' }, { label: '手动指标分析' }]"
    >
      <template #actions>
        <div class="data-badge" :class="dataAgeClass">
          <IAIcon name="calendar" size="sm" />
          <span>{{ sysInfo.data_latest_date || '数据日期未知' }}</span>
        </div>
        <IAButton variant="ghost" size="sm" :loading="updating" @click="doUpdateData">
          <IAIcon name="spinner" v-if="updating" size="sm" />
          <IAIcon v-else name="arrow-down" size="sm" />
          更新数据
        </IAButton>
      </template>
    </IAPageHeader>

    <!-- Stepper -->
    <div class="stepper">
      <div class="stepper-track">
        <div class="stepper-fill" :style="{ width: stepperPercent + '%' }"></div>
      </div>
      <div class="stepper-stops">
        <div class="stepper-stop" :class="{ done: selectedETF, current: selectedETF }">
          <div class="stop-node"><IAIcon v-if="selectedETF" name="check" size="xs" /><span v-else>1</span></div>
          <span class="stop-label">ETF</span>
        </div>
        <div class="stepper-stop" :class="{ done: selectedETF, current: selectedETF && !psychAllAnswered }">
          <div class="stop-node"><span>2</span></div>
          <span class="stop-label">指标</span>
        </div>
        <div class="stepper-stop" :class="{ done: psychAllAnswered, current: psychAllAnswered && !result }">
          <div class="stop-node"><IAIcon v-if="psychAllAnswered" name="check" size="xs" /><span v-else>3</span></div>
          <span class="stop-label">心理</span>
        </div>
        <div class="stepper-stop" :class="{ done: result, current: result }">
          <div class="stop-node"><span>4</span></div>
          <span class="stop-label">结果</span>
        </div>
      </div>
    </div>

    <!-- Step 1: ETF -->
    <IAPanel title="选择标的" subtitle="从数据池中选择 ETF，填入实时价格" icon="market">
      <div class="form-row">
        <select v-model="selectedETF" class="ia-select">
          <option value="" disabled>— 选择 ETF —</option>
          <option v-for="etf in etfList" :key="etf.code" :value="etf.code">
            {{ etfNameMap[etf.code] || etf.code }}
          </option>
        </select>
        <IABadge v-if="selectedETF" variant="green">已确认</IABadge>
      </div>
      <div class="form-row price-row">
        <label class="ia-label">实时价格</label>
        <input type="number" v-model.number="form.current_price" step="0.001" min="0" placeholder="同花顺最新价" class="ia-input" />
        <span class="ia-hint" v-if="!form.current_price">不填则用数据最新收盘价</span>
        <span class="ia-text-green" v-else>已填入实时价 ¥{{ form.current_price.toFixed(3) }}</span>
      </div>
    </IAPanel>

    <!-- Step 2: Indicators -->
    <IAPanel v-if="selectedETF" title="技术指标" :subtitle="`从同花顺 / 东方财富对应面板抄入数值 — 已填 ${filledCount}/16`" icon="analysis">
      <div class="indicator-grid">
        <fieldset class="field-group">
          <legend><span class="legend-dot dmi"></span>DMI 趋势</legend>
          <div class="field"><label>ADX</label><input type="number" v-model.number="form.adx" step="0.1" min="0" max="100" class="ia-input" /></div>
          <div class="field"><label>+DI</label><input type="number" v-model.number="form.plus_di" step="0.1" class="ia-input" /></div>
          <div class="field"><label>−DI</label><input type="number" v-model.number="form.minus_di" step="0.1" class="ia-input" /></div>
        </fieldset>

        <fieldset class="field-group">
          <legend><span class="legend-dot atr"></span>ATR 波幅</legend>
          <div class="field"><label>ATR(14)</label><input type="number" v-model.number="form.atr" step="0.001" min="0" class="ia-input" /></div>
        </fieldset>

        <fieldset class="field-group">
          <legend><span class="legend-dot asi"></span>ASI 振动</legend>
          <div class="field"><label>ASI 值</label><input type="number" v-model.number="form.asi_value" step="0.1" class="ia-input" /></div>
          <div class="field"><label>方向</label>
            <select v-model="form.asi_direction" class="ia-select">
              <option value="">—</option><option value="up">上升</option><option value="down">下降</option><option value="flat">持平</option>
            </select>
          </div>
        </fieldset>

        <fieldset class="field-group">
          <legend><span class="legend-dot macd"></span>MACD 动量</legend>
          <div class="field"><label>DIF</label><input type="number" v-model.number="form.dif" step="0.001" class="ia-input" /></div>
          <div class="field"><label>DEA</label><input type="number" v-model.number="form.dea" step="0.001" class="ia-input" /></div>
          <div class="field"><label>柱状态</label>
            <select v-model="form.macd_bar" class="ia-select">
              <option value="">—</option><option value="red_increasing">红柱增长</option><option value="red_decreasing">红柱缩短</option><option value="green_increasing">绿柱增长</option><option value="green_decreasing">绿柱缩短</option>
            </select>
          </div>
        </fieldset>

        <fieldset class="field-group">
          <legend><span class="legend-dot heat"></span>超买超卖</legend>
          <div class="field"><label>RSI(14)</label><input type="number" v-model.number="form.rsi" step="0.1" min="0" max="100" class="ia-input" /></div>
          <div class="field"><label>WR(14)</label><input type="number" v-model.number="form.wr" step="0.1" min="0" max="100" class="ia-input" /></div>
        </fieldset>

        <fieldset class="field-group">
          <legend><span class="legend-dot vol"></span>量价</legend>
          <div class="field"><label>量比</label><input type="number" v-model.number="form.volume_ratio" step="0.01" min="0" class="ia-input" /></div>
          <div class="field"><label>换手率 %</label><input type="number" v-model.number="form.turnover_rate" step="0.01" min="0" class="ia-input" /></div>
        </fieldset>

        <fieldset class="field-group">
          <legend><span class="legend-dot obv"></span>OBV 能量潮</legend>
          <div class="field"><label>方向</label>
            <select v-model="form.obv_direction" class="ia-select">
              <option value="">—</option><option value="up">上升</option><option value="down">下降</option><option value="flat">持平</option>
            </select>
          </div>
        </fieldset>

        <fieldset class="field-group">
          <legend><span class="legend-dot market"></span>大盘环境</legend>
          <div class="field"><label>趋势</label>
            <select v-model="form.market_trend" class="ia-select">
              <option value="">—</option><option value="bull">多头</option><option value="range">震荡</option><option value="bear">空头</option>
            </select>
          </div>
          <div class="field"><label>ADX</label><input type="number" v-model.number="form.market_adx" step="0.1" min="0" max="100" class="ia-input" /></div>
        </fieldset>

        <fieldset class="field-group prefs">
          <legend><span class="legend-dot prefs"></span>偏好</legend>
          <div class="field"><label>R:R 比</label><input type="number" v-model.number="form.rr_ratio" step="0.1" min="1" max="5" class="ia-input" /></div>
          <div class="field"><label>最大亏损 %</label><input type="number" v-model.number="form.max_loss_pct" step="0.1" min="1" max="15" class="ia-input" /></div>
        </fieldset>
      </div>
    </IAPanel>

    <!-- Step 3: Psychology -->
    <IAPanel v-if="selectedETF" title="交易心理测评" :subtitle="`每题选择最符合你当前状态的选项 — ${answeredCount}/10`" icon="brain">
      <div class="psych-list">
        <div v-for="(q, idx) in psychQuestions" :key="idx" :class="['psych-card', { done: psychAnswers[idx] !== null }]">
          <div class="psych-num">{{ String(idx + 1).padStart(2, '0') }}</div>
          <div class="psych-content">
            <p class="psych-question">{{ q.text }}</p>
            <div class="psych-options">
              <button
                v-for="(opt, oi) in q.options" :key="oi"
                :class="['opt-chip', { picked: psychAnswers[idx] === oi }]"
                @click="pickAnswer(idx, oi)"
              >
                <span class="chip-key">{{ ['A','B','C','D'][oi] }}</span>
                <span class="chip-text">{{ opt }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </IAPanel>

    <!-- Action Bar -->
    <div class="action-bar" v-if="selectedETF && psychAllAnswered">
      <div class="action-status">
        <span class="status-dot active"></span>
        所有数据已就绪，可以进行 SPAS 分析
      </div>
      <IAButton variant="primary" :loading="analyzing" @click="runAnalysis">
        <IAIcon name="activity" size="sm" />
        运行 SPAS 分析
      </IAButton>
    </div>

    <!-- Results -->
    <div v-if="result" class="results ia-anim-fade-in">
      <div class="ia-grid-4 hero-grid">
        <div class="hero-card" :class="result.probability.direction">
          <ProbabilityRing :value="result.probability.probability" :size="120" />
          <div class="hero-label">涨跌概率</div>
          <IABadge :variant="result.probability.direction === 'bullish' ? 'green' : result.probability.direction === 'bearish' ? 'red' : 'neutral'">
            {{ directionLabel(result.probability.direction) }}
          </IABadge>
        </div>

        <div class="hero-card position">
          <div class="hero-big-num">
            <span class="big-value">{{ result.position.suggested_position_pct.toFixed(1) }}</span>
            <span class="big-unit">%</span>
          </div>
          <div class="hero-label">建议仓位</div>
          <IABadge :variant="result.position.suggested_position_pct > 0 ? 'green' : 'neutral'">
            {{ result.position.suggested_position_pct > 0 ? 'Kelly · Fractional' : '不建议交易' }}
          </IABadge>
        </div>

        <div class="hero-card danger">
          <div class="hero-big-num">
            <span class="big-value">{{ result.risk.stop_loss_price.toFixed(2) }}</span>
          </div>
          <div class="hero-label">止损</div>
          <IABadge variant="red">{{ result.risk.stop_loss_pct.toFixed(1) }}%</IABadge>
        </div>

        <div class="hero-card success">
          <div class="hero-big-num">
            <span class="big-value">{{ result.risk.take_profit_price.toFixed(2) }}</span>
          </div>
          <div class="hero-label">止盈</div>
          <IABadge variant="green">+{{ result.risk.take_profit_pct.toFixed(1) }}%</IABadge>
        </div>
      </div>

      <IAPanel title="概率因子分解" icon="chart">
        <div class="factor-list">
          <FactorBar
            v-for="f in result.probability.factors" :key="f.factor"
            :factor="f.factor" :detail="f.detail" :contribution="f.contribution"
          />
        </div>
      </IAPanel>

      <div class="ia-grid-2">
        <IAPanel title="仓位计算" icon="analysis">
          <dl class="kv-grid">
            <div class="kv"><dt>Kelly f*</dt><dd>{{ (result.position.kelly_f_star * 100).toFixed(1) }}%</dd></div>
            <div class="kv"><dt>¼ Kelly</dt><dd>{{ (result.position.kelly_fractional * 100).toFixed(2) }}%</dd></div>
            <div class="kv"><dt>心理评分</dt><dd>{{ result.position.psychology_score }}<span>/30</span></dd></div>
            <div class="kv"><dt>心理因子</dt><dd>×{{ result.position.psychology_factor.toFixed(2) }}</dd></div>
            <div class="kv"><dt>心理等级</dt><dd :class="psychLevelClass(result.position.psychology_level)">{{ result.position.psychology_level }}</dd></div>
            <div class="kv highlight"><dt>最终仓位</dt><dd class="ia-text-green">{{ result.position.suggested_position_pct.toFixed(1) }}%</dd></div>
          </dl>
          <div v-if="result.position.psychology_warnings.length" class="alerts">
            <div v-for="w in result.position.psychology_warnings" :key="w" class="ia-alert ia-alert--warning">
              <IAIcon name="warning" size="sm" />{{ w }}
            </div>
          </div>
        </IAPanel>

        <IAPanel title="风险控制" icon="warning">
          <dl class="kv-grid">
            <div class="kv"><dt>当前价格</dt><dd>¥{{ result.risk.current_price.toFixed(2) }}</dd></div>
            <div class="kv"><dt>ATR(14)</dt><dd>{{ result.risk.atr.toFixed(4) }}</dd></div>
            <div class="kv"><dt>2×ATR 止损带</dt><dd>{{ (result.risk.atr * 2).toFixed(4) }}</dd></div>
            <div class="kv"><dt>止损价</dt><dd class="ia-text-red">¥{{ result.risk.stop_loss_price.toFixed(2) }}</dd></div>
            <div class="kv"><dt>止盈价</dt><dd class="ia-text-green">¥{{ result.risk.take_profit_price.toFixed(2) }}</dd></div>
            <div class="kv"><dt>R:R</dt><dd>{{ result.risk.rr_ratio.toFixed(1) }}:1</dd></div>
          </dl>
          <div v-if="result.risk.atr_warning" class="ia-alert ia-alert--danger">
            <IAIcon name="warning" size="sm" />
            ATR 值异常 ({{ result.risk.atr }})，ETF 正常 ATR 应为 0.01~0.50，请检查是否填错
          </div>
          <div v-if="result.risk.tp_capped" class="ia-alert ia-alert--warning">
            <IAIcon name="warning" size="sm" />止盈已被安全上限限制，请检查 ATR 值是否正确
          </div>
          <div v-if="result.risk.stop_capped_by_max_loss" class="ia-alert ia-alert--warning">
            <IAIcon name="warning" size="sm" />止损已被最大亏损 ({{ form.max_loss_pct }}%) 限制
          </div>
        </IAPanel>
      </div>

      <IAPanel title="系统自动计算" icon="chart" tag="EMA · K-line · MA">
        <div class="tech-strip">
          <div class="tech-item">
            <span class="tech-label">均线</span>
            <span :class="['tech-val', maClass]">{{ result.technical.ma_alignment }}</span>
          </div>
          <div class="tech-item" v-for="(val, key) in result.technical.ema" :key="key">
            <span class="tech-label">{{ key.toUpperCase() }}</span>
            <span class="tech-val">{{ val.toFixed(3) }}</span>
          </div>
          <div class="tech-sep"></div>
          <div class="tech-item" v-for="(val, key) in result.technical.kline_features" :key="key">
            <span class="tech-label">{{ key }}</span>
            <span class="tech-val">{{ val.toFixed(3) }}</span>
          </div>
          <div class="tech-sep"></div>
          <div class="tech-item">
            <span class="tech-label">K线形态</span>
            <span :class="['tech-val', klineClass]">{{ klineLabel }}</span>
          </div>
        </div>
      </IAPanel>
    </div>

    <!-- History -->
    <IAPanel v-if="history.length" title="历史记录" icon="clock" :tag="history.length.toString()">
      <div class="history-list">
        <div v-for="h in history" :key="h.id" class="history-row" @click="loadHistoryItem(h)">
          <div class="h-date">{{ h.created_at }}</div>
          <div class="h-etf">{{ h.etf_name || h.etf_code }}</div>
          <IABadge :variant="h.direction === 'bullish' ? 'green' : h.direction === 'bearish' ? 'red' : 'neutral'">
            {{ h.direction === 'bullish' ? '看多' : h.direction === 'bearish' ? '看空' : '中性' }}
          </IABadge>
          <span class="h-prob">{{ (h.probability * 100).toFixed(0) }}%</span>
          <span class="h-pos">{{ h.position_pct.toFixed(1) }}%</span>
          <button class="h-del" @click.stop="doDeleteHistory(h.id)"><IAIcon name="trash" size="xs" /></button>
        </div>
      </div>
    </IAPanel>
  </div>
</template>

<script>
import { IAPageHeader, IAPanel, IABadge, IAButton, IAIcon, ProbabilityRing, FactorBar } from '../components/ui'
import { analyzeETF, getSystemInfo, triggerDataUpdate, getHistory, getHistoryDetail, deleteHistory } from '../api/manualAnalysis'
import { getETFs, getETFName } from '../api/market'

const DEFAULT_FORM = {
  current_price: null,
  adx: null, plus_di: null, minus_di: null, atr: null,
  asi_value: null, asi_direction: '',
  dif: null, dea: null, macd_bar: '',
  rsi: null, wr: null,
  volume_ratio: null, turnover_rate: null,
  obv_direction: '',
  market_trend: '', market_adx: null,
  rr_ratio: 2.0, max_loss_pct: 5.0,
}

export default {
  name: 'SPASPrediction',
  components: { IAPageHeader, IAPanel, IABadge, IAButton, IAIcon, ProbabilityRing, FactorBar },
  data() {
    return {
      sysInfo: {},
      etfList: [],
      etfNameMap: {},
      selectedETF: '',
      form: { ...DEFAULT_FORM },
      psychQuestions: [
        { text: '你进行这笔交易的主要动机是什么？', options: ['执行交易计划中已设定的策略', '看到别人在讨论/推荐这只ETF', '担心错过这波行情', '近期亏损想尽快回本'] },
        { text: '你对这只ETF的了解程度？', options: ['深入研究过，了解其持仓和行业定位', '看过一些相关报告和新闻', '听说过这只ETF，知道大概方向', '不熟悉，凭感觉选的'] },
        { text: '最近一周你的情绪状态如何？', options: ['平稳冷静，正常生活不受影响', '略有焦虑，会时不时看盘', '比较焦虑，频繁查看账户', '非常焦虑，影响睡眠或日常'] },
        { text: '如果买入后立即亏损5%，你会怎么做？', options: ['按原定止损计划执行，果断离场', '重新分析基本面再决定去留', '加仓摊平成本等待反弹', '死扛不卖，相信总会涨回来'] },
        { text: '你对这笔交易盈利的信心有多大？', options: ['基于数据约60%，有量化依据支撑', '约75%，感觉各方面信号都挺好', '超过90%，这次一定稳赚', '不太确定能不能赚钱'] },
        { text: '你上一次交易的结果怎样？', options: ['盈利了，按计划止盈出场', '亏损了，但按计划止损了', '盈利了，但没按计划提前卖了', '亏损了，而且没有按计划止损'] },
        { text: '你有明确的交易计划吗（入场理由/仓位/止损/止盈）？', options: ['有完整的书面计划，每次交易前都写好', '心里有计划，但没有写下来', '大概想了一下，没有详细规划', '没有计划，看行情临时决定'] },
        { text: '过去一个月你遵守交易计划了吗？', options: ['完全遵守，每笔交易都按计划执行', '大部分遵守，偶尔小偏差', '偶尔遵守，常有临时冲动交易', '经常偏离计划，随心所欲交易'] },
        { text: '你对当前大盘环境的判断？', options: ['有清晰依据（技术面/基本面），方向明确', '跟主流观点一致，比较有信心', '不太确定，感觉市场方向不明', '没有分析，凭感觉判断'] },
        { text: '你当前的仓位情况？', options: ['空仓或轻仓（< 总资金20%）', '中等仓位（总资金20%-50%）', '较重仓位（总资金50%-80%）', '满仓或接近满仓（> 80%）'] },
      ],
      psychAnswers: [null, null, null, null, null, null, null, null, null, null],
      analyzing: false,
      updating: false,
      result: null,
      history: [],
      historyLoadedId: null,
    }
  },
  computed: {
    dataAgeClass() {
      const d = this.sysInfo.data_latest_date
      if (!d || d === '未知') return 'stale'
      const clean = String(d).replace(/-/g, '')
      const y = parseInt(clean.slice(0, 4)), m = parseInt(clean.slice(4, 6)) - 1, day = parseInt(clean.slice(6, 8))
      if (isNaN(y) || isNaN(m) || isNaN(day)) return 'stale'
      const diff = (Date.now() - new Date(y, m, day).getTime()) / 86400000
      if (diff < 0) return 'stale'
      return diff <= 1 ? 'fresh' : diff <= 3 ? 'warn' : 'stale'
    },
    psychAllAnswered() { return this.psychAnswers.every(a => a !== null) },
    answeredCount() { return this.psychAnswers.filter(a => a !== null).length },
    stepperPercent() {
      if (this.result) return 100
      if (this.psychAllAnswered) return 75
      if (this.selectedETF) return 38
      return 12
    },
    filledCount() {
      let c = 0
      const keys = ['adx','plus_di','minus_di','atr','asi_value','asi_direction','dif','dea','macd_bar','rsi','wr','volume_ratio','turnover_rate','obv_direction','market_trend','market_adx']
      for (const k of keys) {
        const v = this.form[k]
        if (v !== null && v !== '') c++
      }
      return c
    },
    maClass() {
      if (!this.result) return ''
      const a = this.result.technical.ma_alignment
      return a === 'BULL' ? 'ia-text-green' : a === 'BEAR' ? 'ia-text-red' : ''
    },
    klineClass() {
      if (!this.result) return ''
      const p = this.result.technical.kline_pattern
      return p === 'bullish' ? 'ia-text-green' : p === 'bearish' ? 'ia-text-red' : ''
    },
    klineLabel() {
      if (!this.result) return ''
      const p = this.result.technical.kline_pattern
      return p === 'bullish' ? '看涨' : p === 'bearish' ? '看跌' : '中性'
    },
  },
  async created() {
    try {
      const [etfsRes, infoRes] = await Promise.all([getETFs(), getSystemInfo().catch(() => ({ data: {} }))])
      this.etfList = etfsRes.data || []
      this.sysInfo = infoRes.data || {}
      if (this.etfList.length) {
        this.selectedETF = this.etfList[0].code
        for (const etf of this.etfList) {
          try { const nr = await getETFName(etf.code); this.$set(this.etfNameMap, etf.code, nr.data.display_name) } catch (e) {}
        }
      }
    } catch (e) { console.error(e) }
    this.loadHistory()
  },
  methods: {
    async doUpdateData() {
      this.updating = true
      try {
        const res = await triggerDataUpdate()
        if (res.data.success) { const infoRes = await getSystemInfo(); this.sysInfo = infoRes.data || {} }
        else { alert('更新失败') }
      } catch (e) { alert('更新失败: ' + (e.response?.data?.detail || e.message)) }
      finally { this.updating = false }
    },
    async runAnalysis() {
      this.analyzing = true; this.result = null
      try {
        const payload = { ...this.form, psychology_answers: this.psychAnswers.map(a => 3 - a) }
        const res = await analyzeETF(this.selectedETF, payload)
        this.result = res.data
        this.loadHistory()
        this.$nextTick(() => { const el = document.querySelector('.results'); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' }) })
      } catch (e) { alert('分析失败: ' + (e.response?.data?.detail || e.message)) }
      finally { this.analyzing = false }
    },
    directionLabel(d) { return d === 'bullish' ? '看多' : d === 'bearish' ? '看空' : '中性' },
    psychLevelClass(l) { return l === '优秀' || l === '良好' ? 'ia-text-green' : l === '一般' ? '' : 'ia-text-red' },
    pickAnswer(idx, oi) { this.$set(this.psychAnswers, idx, oi) },
    async loadHistory() {
      try { const res = await getHistory(); this.history = res.data || [] } catch (e) {}
    },
    async loadHistoryItem(h) {
      try {
        const res = await getHistoryDetail(h.id)
        const detail = res.data
        if (detail && detail.result) {
          this.result = detail.result
          this.historyLoadedId = h.id
          if (detail.inputs) {
            const keep = ['rr_ratio','max_loss_pct','psychology_answers']
            Object.keys(this.form).forEach(k => {
              if (detail.inputs[k] !== undefined && !keep.includes(k)) {
                this.form[k] = detail.inputs[k]
              }
            })
          }
          this.$nextTick(() => { const el = document.querySelector('.results'); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' }) })
        }
      } catch (e) { alert('加载历史失败: ' + (e.response?.data?.detail || e.message)) }
    },
    async doDeleteHistory(id) {
      if (!confirm('删除这条记录？')) return
      try { await deleteHistory(id); this.history = this.history.filter(h => h.id !== id) } catch (e) { alert('删除失败') }
    },
  },
}
</script>

<style scoped>
.spas {
  padding-bottom: var(--ia-space-xl);
}

.data-badge {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.7rem;
  border-radius: 20px;
  font-size: var(--ia-font-size-xs);
  font-weight: 500;
  background: var(--ia-surface);
  border: 1px solid var(--ia-border);
  color: var(--ia-text-secondary);
}

.data-badge.fresh { color: var(--ia-green); border-color: rgba(14, 203, 129, 0.2); }
.data-badge.warn { color: var(--ia-gold); border-color: rgba(240, 185, 11, 0.2); }
.data-badge.stale { color: var(--ia-red); border-color: rgba(246, 70, 93, 0.2); }

.form-row {
  display: flex;
  align-items: center;
  gap: var(--ia-space-md);
  flex-wrap: wrap;
}

.price-row {
  margin-top: var(--ia-space-md);
  padding-top: var(--ia-space-md);
  border-top: 1px solid var(--ia-border);
}

.price-row .ia-input {
  width: 160px;
}

/* Stepper */
.stepper {
  margin-bottom: var(--ia-space-xl);
  padding: 0 0.5rem;
}
.stepper-track {
  position: relative;
  height: 2px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 1px;
  margin: 0 22px 0.8rem;
}
.stepper-fill {
  height: 100%;
  border-radius: 1px;
  background: linear-gradient(90deg, var(--ia-gold), var(--ia-yellow));
  box-shadow: 0 0 6px rgba(240, 185, 11, 0.3);
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.stepper-stops {
  display: flex;
  justify-content: space-between;
}
.stepper-stop {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  opacity: 0.35;
  transition: opacity 0.35s;
}
.stepper-stop.done, .stepper-stop.current { opacity: 1; }
.stop-node {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.68rem;
  font-weight: 700;
  background: var(--ia-surface);
  border: 2px solid rgba(255, 255, 255, 0.10);
  color: var(--ia-text-tertiary);
  transition: all 0.3s;
}
.stepper-stop.current .stop-node {
  border-color: var(--ia-gold);
  color: var(--ia-gold);
  background: var(--ia-gold-soft);
  box-shadow: 0 0 10px rgba(240, 185, 11, 0.15);
}
.stepper-stop.done .stop-node {
  border-color: var(--ia-green);
  background: var(--ia-green-soft);
  color: var(--ia-green);
}
.stop-label {
  font-size: var(--ia-font-size-xs);
  font-weight: 500;
  color: var(--ia-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.stepper-stop.current .stop-label { color: var(--ia-gold); }
.stepper-stop.done .stop-label { color: var(--ia-green); }

/* Indicator grid */
.indicator-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--ia-space-md);
}
.field-group {
  border: 1px solid var(--ia-border);
  border-radius: var(--ia-radius-sm);
  padding: 0.8rem 1rem;
  margin: 0;
  background: rgba(255, 255, 255, 0.015);
  transition: border-color 0.25s;
  display: flex;
  flex-direction: column;
}
.field-group:hover { border-color: var(--ia-border-strong); }
.field-group.prefs { border-color: rgba(240, 185, 11, 0.12); background: rgba(240, 185, 11, 0.02); }
.field-group legend {
  font-size: var(--ia-font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--ia-text-tertiary);
  padding: 0 0.4rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.legend-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
.legend-dot.dmi { background: var(--ia-blue); }
.legend-dot.atr { background: #06B6D4; }
.legend-dot.asi { background: #A855F7; }
.legend-dot.macd { background: #F59E0B; }
.legend-dot.heat { background: #EF4444; }
.legend-dot.vol { background: #10B981; }
.legend-dot.obv { background: #EC4899; }
.legend-dot.market { background: #6366F1; }
.legend-dot.prefs { background: var(--ia-gold); }

.field {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.35rem 0;
  gap: 0.5rem;
  min-height: 2rem;
}
.field label {
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text-secondary);
  white-space: nowrap;
  min-width: 70px;
  font-variant-numeric: tabular-nums;
}
.field .ia-input, .field .ia-select {
  width: 130px;
  text-align: right;
  font-family: var(--ia-font-mono);
  font-size: 0.8rem;
}
.field .ia-select { text-align: left; }

/* Psychology */
.psych-list { display: flex; flex-direction: column; gap: 0.6rem; }
.psych-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.015);
  border: 1px solid var(--ia-border);
  border-radius: var(--ia-radius-sm);
  transition: all 0.3s;
}
.psych-card.done { border-color: rgba(14, 203, 129, 0.2); background: rgba(14, 203, 129, 0.03); }
.psych-num {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--ia-text-tertiary);
  font-variant-numeric: tabular-nums;
  min-width: 28px;
  font-family: var(--ia-font-mono);
}
.psych-card.done .psych-num { color: var(--ia-green); }
.psych-content { flex: 1; }
.psych-question { font-size: var(--ia-font-size-md); color: var(--ia-text); margin: 0 0 0.5rem; line-height: 1.5; }
.psych-options { display: grid; grid-template-columns: 1fr 1fr; gap: 0.35rem; }
.opt-chip {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.55rem 0.7rem;
  text-align: left;
  background: var(--ia-bg);
  border: 1px solid var(--ia-border);
  border-radius: var(--ia-radius-xs);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.73rem;
  color: var(--ia-text-secondary);
  line-height: 1.35;
  font-family: inherit;
}
.opt-chip:hover { border-color: var(--ia-border-strong); background: var(--ia-surface-hover); }
.opt-chip.picked { border-color: var(--ia-gold); background: var(--ia-gold-soft); color: var(--ia-gold); }
.chip-key {
  font-size: 0.62rem;
  font-weight: 700;
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--ia-text-tertiary);
  flex-shrink: 0;
  margin-top: 0.1rem;
}
.opt-chip.picked .chip-key { background: rgba(240, 185, 11, 0.2); color: var(--ia-gold); }
.chip-text { flex: 1; }

/* Action Bar */
.action-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.2rem 1.5rem;
  margin-bottom: var(--ia-space-xl);
  background: linear-gradient(135deg, rgba(240, 185, 11, 0.03), rgba(240, 185, 11, 0.06));
  border: 1px solid rgba(240, 185, 11, 0.15);
  border-radius: var(--ia-radius);
}
.action-status { display: flex; align-items: center; gap: 0.6rem; font-size: var(--ia-font-size-md); color: var(--ia-text-secondary); }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.active { background: var(--ia-green); box-shadow: 0 0 8px rgba(14, 203, 129, 0.5); animation: ia-pulse 2s infinite; }

/* Results Hero */
.hero-grid { margin-bottom: var(--ia-space-md); }
.hero-card {
  background: var(--ia-surface);
  border: 1px solid var(--ia-border);
  border-radius: var(--ia-radius);
  padding: var(--ia-space-lg);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}
.hero-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: transparent;
  transition: background 0.3s;
}
.hero-card.bullish::before { background: var(--ia-green); }
.hero-card.bearish::before { background: var(--ia-red); }
.hero-card.position::before { background: var(--ia-blue); }
.hero-card.danger::before { background: var(--ia-red); }
.hero-card.success::before { background: var(--ia-green); }
.hero-card:hover { border-color: var(--ia-border-strong); }
.hero-label { font-size: var(--ia-font-size-xs); color: var(--ia-text-tertiary); text-transform: uppercase; letter-spacing: 0.08em; margin: var(--ia-space-sm) 0 var(--ia-space-xs); }
.hero-big-num { margin: var(--ia-space-sm) 0; }
.big-value { font-size: 2rem; font-weight: 700; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; color: var(--ia-text); }
.big-unit { font-size: 0.85rem; color: var(--ia-text-tertiary); margin-left: 0.15rem; }

/* KV Grid */
.kv-grid { display: flex; flex-direction: column; gap: 0.25rem; }
.kv { display: flex; justify-content: space-between; align-items: center; padding: 0.45rem 0.6rem; border-radius: var(--ia-radius-xs); }
.kv:nth-child(even) { background: rgba(255, 255, 255, 0.015); }
.kv.highlight { background: rgba(240, 185, 11, 0.05); border: 1px solid rgba(240, 185, 11, 0.12); border-radius: var(--ia-radius-xs); }
.kv dt { font-size: var(--ia-font-size-sm); color: var(--ia-text-tertiary); }
.kv dd { font-size: var(--ia-font-size-md); font-weight: 500; font-variant-numeric: tabular-nums; color: var(--ia-text); }
.kv dd span { font-size: 0.65rem; color: var(--ia-text-tertiary); margin-left: 0.2rem; }

/* Alerts */
.alerts { margin-top: var(--ia-space-md); display: flex; flex-direction: column; gap: 0.3rem; }

/* Tech strip */
.tech-strip { display: flex; flex-wrap: wrap; gap: 0.25rem; align-items: stretch; }
.tech-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.2rem;
  padding: 0.5rem 0.8rem;
  border-radius: var(--ia-radius-xs);
  min-width: 72px;
  min-height: 48px;
  background: rgba(255, 255, 255, 0.015);
  border: 1px solid transparent;
  transition: all 0.2s;
}
.tech-item:hover { border-color: var(--ia-border); background: rgba(255, 255, 255, 0.03); }
.tech-label { font-size: var(--ia-font-size-xs); color: var(--ia-text-tertiary); text-transform: uppercase; letter-spacing: 0.04em; }
.tech-val { font-size: var(--ia-font-size-md); font-weight: 600; font-variant-numeric: tabular-nums; }
.tech-sep { width: 1px; background: var(--ia-border); margin: 0 0.25rem; }

/* History */
.history-list { display: flex; flex-direction: column; gap: 0.4rem; }
.history-row {
  display: grid;
  grid-template-columns: 150px 1fr auto 70px 70px 40px;
  align-items: center;
  gap: var(--ia-space-sm);
  padding: 0.65rem 0.8rem;
  background: rgba(255, 255, 255, 0.015);
  border: 1px solid var(--ia-border);
  border-radius: var(--ia-radius-xs);
  cursor: pointer;
  transition: background 0.2s;
  font-size: var(--ia-font-size-sm);
}
.history-row:hover { background: rgba(255, 255, 255, 0.03); }
.h-date { color: var(--ia-text-tertiary); font-variant-numeric: tabular-nums; }
.h-etf { color: var(--ia-text); font-weight: 500; }
.h-prob, .h-pos { font-variant-numeric: tabular-nums; color: var(--ia-text); }
.h-del { background: transparent; border: 1px solid var(--ia-border); border-radius: 4px; color: var(--ia-text-secondary); cursor: pointer; padding: 0.2rem; display: flex; align-items: center; justify-content: center; }
.h-del:hover { background: var(--ia-red-soft); border-color: var(--ia-red); color: var(--ia-red); }

@media (max-width: 768px) {
  .indicator-grid { grid-template-columns: 1fr; }
  .psych-options { grid-template-columns: 1fr; }
  .history-row { grid-template-columns: 1fr; gap: 0.25rem; }
  .action-bar { flex-direction: column; gap: var(--ia-space-md); align-items: stretch; }
  .form-row { flex-direction: column; align-items: flex-start; }
}
</style>
