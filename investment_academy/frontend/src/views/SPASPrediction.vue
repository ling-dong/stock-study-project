<template>
  <div class="spas">
    <!-- ═══ Header ═══ -->
    <header class="spas-header">
      <div class="header-left">
        <nav class="breadcrumb">
          <router-link to="/">Home</router-link>
          <span class="sep">/</span>
          <span class="current">SPAS</span>
        </nav>
        <h1 class="title">SPAS <span class="title-dim">交易分析</span></h1>
      </div>
      <div class="header-right">
        <div class="data-badge" :class="dataAgeClass">
          <span class="badge-dot"></span>
          <span class="badge-text">{{ sysInfo.data_latest_date || '—' }}</span>
        </div>
        <button class="btn-ghost" @click="doUpdateData" :disabled="updating">
          <span class="btn-icon">{{ updating ? '⟳' : '↻' }}</span>
          {{ updating ? '更新中' : '更新数据' }}
        </button>
      </div>
    </header>

    <!-- ═══ Step Progress ═══ -->
    <div class="stepper">
      <div class="stepper-track">
        <div class="stepper-fill" :style="{ width: stepperPercent + '%' }"></div>
      </div>
      <div class="stepper-stops">
        <div class="stepper-stop" :class="{ done: !!selectedETF, current: selectedETF && !psychAllAnswered && !result }">
          <div class="stop-node"><span v-if="selectedETF">✓</span><span v-else>1</span></div>
          <span class="stop-label">ETF</span>
        </div>
        <div class="stepper-stop" :class="{ done: selectedETF, current: selectedETF && !psychAllAnswered && !result }">
          <div class="stop-node"><span v-if="psychAllAnswered">✓</span><span v-else>2</span></div>
          <span class="stop-label">指标</span>
        </div>
        <div class="stepper-stop" :class="{ done: psychAllAnswered, current: psychAllAnswered && !result }">
          <div class="stop-node"><span v-if="result">✓</span><span v-else>3</span></div>
          <span class="stop-label">心理</span>
        </div>
        <div class="stepper-stop" :class="{ done: !!result, current: !!result }">
          <div class="stop-node">4</div>
          <span class="stop-label">结果</span>
        </div>
      </div>
    </div>

    <!-- ═══ Panel: Step 1 — ETF ═══ -->
    <section class="panel">
      <div class="panel-header">
        <div class="panel-icon">Ⅰ</div>
        <div class="panel-title-group">
          <h2 class="panel-title">选择标的</h2>
          <p class="panel-sub">从数据池中选择 ETF，填入实时价格</p>
        </div>
      </div>
      <div class="panel-body">
        <div class="etf-row">
          <select v-model="selectedETF" class="select-main">
            <option value="" disabled>— 选择 ETF —</option>
            <option v-for="etf in etfList" :key="etf.code" :value="etf.code">
              {{ etfNameMap[etf.code] || etf.code }}
            </option>
          </select>
          <span class="etf-confirm" v-if="selectedETF">
            ✓ {{ etfNameMap[selectedETF] || selectedETF }}
          </span>
        </div>
        <div class="etf-row price-row">
          <label class="price-label">实时价格</label>
          <input type="number" v-model.number="form.current_price" step="0.001" min="0"
                 placeholder="同花顺最新价" class="price-input" />
          <span class="price-hint" v-if="!form.current_price">不填则用数据最新收盘价</span>
          <span class="price-hint ok" v-else>已填入实时价 ¥{{ form.current_price.toFixed(3) }}</span>
        </div>
      </div>
    </section>

    <!-- ═══ Panel: Step 2 — Indicators ═══ -->
    <section class="panel" v-if="selectedETF">
      <div class="panel-header">
        <div class="panel-icon">Ⅱ</div>
        <div class="panel-title-group">
          <h2 class="panel-title">技术指标</h2>
          <p class="panel-sub">从同花顺 / 东方财富对应面板抄入数值</p>
        </div>
        <div class="panel-badge">{{ filledCount }} / 15</div>
      </div>
      <div class="panel-body">
        <div class="indicator-grid">

          <!-- DMI -->
          <fieldset class="field-group">
            <legend><span class="legend-dot dmi"></span>DMI 趋势 <span class="legend-hint">同花顺 → DMI 面板</span></legend>
            <div class="field">
              <label>ADX</label>
              <input type="number" v-model.number="form.adx" step="0.1" min="0" max="100" placeholder="28.5" />
            </div>
            <div class="field">
              <label>+DI</label>
              <input type="number" v-model.number="form.plus_di" step="0.1" placeholder="32.1" />
            </div>
            <div class="field">
              <label>−DI</label>
              <input type="number" v-model.number="form.minus_di" step="0.1" placeholder="18.3" />
            </div>
          </fieldset>

          <!-- ATR -->
          <fieldset class="field-group">
            <legend><span class="legend-dot atr"></span>ATR 波幅 <span class="legend-hint">同花顺 → 反趋向指标 → ATR</span></legend>
            <div class="field">
              <label>ATR(14) <span class="hint-sm">正常 0.01~0.50</span></label>
              <input type="number" v-model.number="form.atr" step="0.001" min="0" placeholder="0.085" />
            </div>
          </fieldset>

          <!-- ASI -->
          <fieldset class="field-group">
            <legend><span class="legend-dot asi"></span>ASI 振动</legend>
            <div class="field">
              <label>ASI 值</label>
              <input type="number" v-model.number="form.asi_value" step="0.1" placeholder="156.3" />
            </div>
            <div class="field">
              <label>方向</label>
              <select v-model="form.asi_direction">
                <option value="">—</option>
                <option value="up">↗ 上升</option>
                <option value="down">↘ 下降</option>
                <option value="flat">→ 持平</option>
              </select>
            </div>
          </fieldset>

          <!-- MACD -->
          <fieldset class="field-group">
            <legend><span class="legend-dot macd"></span>MACD 动量</legend>
            <div class="field">
              <label>DIF</label>
              <input type="number" v-model.number="form.dif" step="0.001" placeholder="0.032" />
            </div>
            <div class="field">
              <label>DEA</label>
              <input type="number" v-model.number="form.dea" step="0.001" placeholder="0.018" />
            </div>
            <div class="field">
              <label>柱状态</label>
              <select v-model="form.macd_bar">
                <option value="">—</option>
                <option value="red_increasing">▮ 红柱增长</option>
                <option value="red_decreasing">▯ 红柱缩短</option>
                <option value="green_increasing">▮ 绿柱增长</option>
                <option value="green_decreasing">▯ 绿柱缩短</option>
              </select>
            </div>
          </fieldset>

          <!-- RSI + WR -->
          <fieldset class="field-group">
            <legend><span class="legend-dot heat"></span>超买超卖</legend>
            <div class="field">
              <label>RSI(14)</label>
              <input type="number" v-model.number="form.rsi" step="0.1" min="0" max="100" placeholder="45.2" />
            </div>
            <div class="field">
              <label>WR(14)</label>
              <input type="number" v-model.number="form.wr" step="0.1" min="0" max="100" placeholder="65.0" />
            </div>
          </fieldset>

          <!-- Volume -->
          <fieldset class="field-group">
            <legend><span class="legend-dot vol"></span>量价</legend>
            <div class="field">
              <label>量比</label>
              <input type="number" v-model.number="form.volume_ratio" step="0.01" min="0" placeholder="1.35" />
            </div>
            <div class="field">
              <label>换手率 %</label>
              <input type="number" v-model.number="form.turnover_rate" step="0.01" min="0" placeholder="3.50" />
            </div>
          </fieldset>

          <!-- OBV -->
          <fieldset class="field-group">
            <legend><span class="legend-dot obv"></span>OBV 能量潮</legend>
            <div class="field">
              <label>方向</label>
              <select v-model="form.obv_direction">
                <option value="">—</option>
                <option value="up">↗ 上升</option>
                <option value="down">↘ 下降</option>
                <option value="flat">→ 持平</option>
              </select>
            </div>
          </fieldset>

          <!-- Market -->
          <fieldset class="field-group">
            <legend><span class="legend-dot market"></span>大盘环境</legend>
            <div class="field">
              <label>趋势</label>
              <select v-model="form.market_trend">
                <option value="">—</option>
                <option value="bull">◉ 多头</option>
                <option value="range">◉ 震荡</option>
                <option value="bear">◉ 空头</option>
              </select>
            </div>
            <div class="field">
              <label>ADX</label>
              <input type="number" v-model.number="form.market_adx" step="0.1" min="0" max="100" placeholder="22.0" />
            </div>
          </fieldset>

          <!-- Preferences -->
          <fieldset class="field-group field-group-prefs">
            <legend><span class="legend-dot prefs"></span>偏好</legend>
            <div class="field">
              <label>R:R 比</label>
              <input type="number" v-model.number="form.rr_ratio" step="0.1" min="1.0" max="5.0" placeholder="2.0" />
            </div>
            <div class="field">
              <label>最大亏损 %</label>
              <input type="number" v-model.number="form.max_loss_pct" step="0.1" min="1" max="15" placeholder="5.0" />
            </div>
          </fieldset>

        </div>
      </div>
    </section>

    <!-- ═══ Panel: Step 3 — Psychology ═══ -->
    <section class="panel" v-if="selectedETF">
      <div class="panel-header">
        <div class="panel-icon">Ⅲ</div>
        <div class="panel-title-group">
          <h2 class="panel-title">交易心理测评</h2>
          <p class="panel-sub">每题选择最符合你当前状态的选项</p>
        </div>
        <div class="panel-badge" :class="{ done: psychAllAnswered }">{{ answeredCount }} / 10</div>
      </div>
      <div class="panel-body">
        <div class="psych-list">
          <div v-for="(q, idx) in psychQuestions" :key="idx"
               :class="['psych-card', { done: psychAnswers[idx] !== null }]">
            <div class="psych-num">{{ String(idx + 1).padStart(2, '0') }}</div>
            <div class="psych-content">
              <p class="psych-question">{{ q.text }}</p>
              <div class="psych-options">
                <button
                  v-for="(opt, oi) in q.options"
                  :key="oi"
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
      </div>
    </section>

    <!-- ═══ Action Bar ═══ -->
    <div class="action-bar" v-if="selectedETF && psychAllAnswered">
      <div class="action-status">
        <span class="status-dot active"></span>
        所有数据已就绪，可以进行 SPAS 分析
      </div>
      <button class="btn-analyze" @click="runAnalysis" :disabled="analyzing">
        <span v-if="!analyzing">▶ 运行 SPAS 分析</span>
        <span v-else class="spinner"></span>
        <span v-else>分析中</span>
      </button>
    </div>

    <!-- ═══ Results ═══ -->
    <div class="results" v-if="result">

      <!-- Hero Cards -->
      <div class="hero-grid">
        <div :class="['hero-card', result.probability.direction]">
          <div class="hero-ring">
            <svg viewBox="0 0 120 120" class="ring-svg">
              <circle cx="60" cy="60" r="52" class="ring-bg" />
              <circle cx="60" cy="60" r="52" class="ring-fill"
                      :stroke-dasharray="326.7"
                      :stroke-dashoffset="326.7 * (1 - result.probability.probability)" />
            </svg>
            <div class="ring-center">
              <span class="ring-value">{{ (result.probability.probability * 100).toFixed(0) }}</span>
              <span class="ring-unit">%</span>
            </div>
          </div>
          <div class="hero-label">涨跌概率</div>
          <div class="hero-badge" :class="result.probability.direction">
            {{ directionLabel(result.probability.direction) }}
          </div>
        </div>

        <div class="hero-card position">
          <div class="hero-big-num">
            <span class="big-value">{{ result.position.suggested_position_pct.toFixed(1) }}</span>
            <span class="big-unit">%</span>
          </div>
          <div class="hero-label">建议仓位</div>
          <div class="hero-badge" :class="result.position.suggested_position_pct > 0 ? 'good' : 'bad'">
            {{ result.position.suggested_position_pct > 0 ? 'Kelly · Fractional' : '不建议交易' }}
          </div>
        </div>

        <div class="hero-card danger">
          <div class="hero-big-num">
            <span class="big-value">{{ result.risk.stop_loss_price.toFixed(2) }}</span>
          </div>
          <div class="hero-label">止损</div>
          <div class="hero-badge bad">{{ result.risk.stop_loss_pct.toFixed(1) }}%</div>
        </div>

        <div class="hero-card success">
          <div class="hero-big-num">
            <span class="big-value">{{ result.risk.take_profit_price.toFixed(2) }}</span>
          </div>
          <div class="hero-label">止盈</div>
          <div class="hero-badge good">+{{ result.risk.take_profit_pct.toFixed(1) }}%</div>
        </div>
      </div>

      <!-- Factor Breakdown -->
      <section class="panel">
        <div class="panel-header">
          <div class="panel-icon sm">⚙</div>
          <h2 class="panel-title">概率因子分解</h2>
        </div>
        <div class="panel-body">
          <div class="factor-list">
            <div v-for="f in result.probability.factors" :key="f.factor"
                 :class="['factor-row', f.contribution > 0 ? 'pos' : f.contribution < 0 ? 'neg' : '']">
              <div class="factor-left">
                <span class="factor-name">{{ f.factor }}</span>
                <span class="factor-detail">{{ f.detail }}</span>
              </div>
              <div class="factor-bar-wrap">
                <div class="factor-bar" :style="{ width: Math.abs(f.contribution * 100) * 4 + 'px' }"
                     :class="f.contribution > 0 ? 'bar-pos' : f.contribution < 0 ? 'bar-neg' : 'bar-neutral'"></div>
              </div>
              <span class="factor-val" :class="f.contribution > 0 ? 'text-pos' : f.contribution < 0 ? 'text-neg' : ''">
                {{ f.contribution > 0 ? '+' : '' }}{{ (f.contribution * 100).toFixed(0) }}%
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Position + Risk (side by side) -->
      <div class="two-col">
        <section class="panel">
          <div class="panel-header">
            <div class="panel-icon sm">☰</div>
            <h2 class="panel-title">仓位计算</h2>
          </div>
          <div class="panel-body">
            <dl class="kv-grid">
              <div class="kv"><dt>Kelly f*</dt><dd>{{ (result.position.kelly_f_star * 100).toFixed(1) }}%</dd></div>
              <div class="kv"><dt>¼ Kelly</dt><dd>{{ (result.position.kelly_fractional * 100).toFixed(2) }}%</dd></div>
              <div class="kv"><dt>心理评分</dt><dd>{{ result.position.psychology_score }}<span class="kv-dim">/30</span></dd></div>
              <div class="kv"><dt>心理因子</dt><dd>×{{ result.position.psychology_factor.toFixed(2) }}</dd></div>
              <div class="kv"><dt>心理等级</dt><dd :class="psychLevelClass(result.position.psychology_level)">{{ result.position.psychology_level }}</dd></div>
              <div class="kv highlight"><dt>最终仓位</dt><dd class="text-pos">{{ result.position.suggested_position_pct.toFixed(1) }}%</dd></div>
            </dl>
            <div v-if="result.position.psychology_warnings.length" class="alerts">
              <div v-for="w in result.position.psychology_warnings" :key="w" class="alert">⚠ {{ w }}</div>
            </div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-header">
            <div class="panel-icon sm">◎</div>
            <h2 class="panel-title">风险控制</h2>
          </div>
          <div class="panel-body">
            <dl class="kv-grid">
              <div class="kv"><dt>当前价格</dt><dd>¥{{ result.risk.current_price.toFixed(2) }}</dd></div>
              <div class="kv"><dt>ATR(14)</dt><dd>{{ result.risk.atr.toFixed(4) }}</dd></div>
              <div class="kv"><dt>2×ATR 止损带</dt><dd>{{ (result.risk.atr * 2).toFixed(4) }}</dd></div>
              <div class="kv"><dt>止损价</dt><dd class="text-neg">¥{{ result.risk.stop_loss_price.toFixed(2) }}</dd></div>
              <div class="kv"><dt>止盈价</dt><dd class="text-pos">¥{{ result.risk.take_profit_price.toFixed(2) }}</dd></div>
              <div class="kv"><dt>R:R</dt><dd>{{ result.risk.rr_ratio.toFixed(1) }}:1</dd></div>
            </dl>
            <div v-if="result.risk.atr_warning" class="alert" style="background:rgba(246,70,93,0.08);border-color:rgba(246,70,93,0.2);color:var(--red)">⚠ ATR 值异常 ({{ result.risk.atr }})，ETF 正常 ATR 应为 0.01~0.50，请检查是否填错</div>
            <div v-if="result.risk.tp_capped" class="alert">⚠ 止盈已被安全上限 (3×当前价) 限制，请检查 ATR 值是否正确</div>
            <div v-if="result.risk.stop_capped_by_max_loss" class="alert">⚠ 止损已被最大亏损 ({{ form.max_loss_pct }}%) 限制</div>
          </div>
        </section>
      </div>

      <!-- Technical (auto-computed) -->
      <section class="panel">
        <div class="panel-header">
          <div class="panel-icon sm">⌬</div>
          <h2 class="panel-title">系统自动计算</h2>
          <span class="panel-tag">EMA · K-line · MA Alignment</span>
        </div>
        <div class="panel-body">
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
              <span :class="['tech-val', result.technical.kline_pattern === 'bullish' ? 'text-pos' : result.technical.kline_pattern === 'bearish' ? 'text-neg' : '']">
                {{ result.technical.kline_pattern === 'bullish' ? '看涨' : result.technical.kline_pattern === 'bearish' ? '看跌' : '中性' }}
              </span>
            </div>
          </div>
        </div>
      </section>

    </div>

    <!-- ═══ History Panel ═══ -->
    <section class="panel" v-if="history.length">
      <div class="panel-header">
        <div class="panel-icon sm">☰</div>
        <h2 class="panel-title">历史记录</h2>
        <span class="panel-badge">{{ history.length }}</span>
      </div>
      <div class="panel-body" style="padding:0">
        <div v-for="h in history" :key="h.id" class="history-row" @click="loadHistoryItem(h)">
          <div class="h-date">{{ h.created_at }}</div>
          <div class="h-etf">{{ h.etf_name || h.etf_code }}</div>
          <span :class="['h-dir', h.direction === 'bullish' ? 'text-pos' : h.direction === 'bearish' ? 'text-neg' : '']">
            {{ h.direction === 'bullish' ? '看多' : h.direction === 'bearish' ? '看空' : '中性' }}
          </span>
          <span class="h-prob">{{ (h.probability * 100).toFixed(0) }}%</span>
          <span class="h-pos">{{ h.position_pct.toFixed(1) }}%</span>
          <button class="h-del" @click.stop="doDeleteHistory(h.id)">✕</button>
        </div>
      </div>
    </section>

  </div>
</template>

<script>
import { analyzeETF, getSystemInfo, triggerDataUpdate, getHistory, getHistoryDetail, deleteHistory } from '../api/spas'
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
      historyLoadedId: null,  // 当前查看的历史记录 ID
    }
  },
  computed: {
    dataAgeClass() {
      const d = this.sysInfo.data_latest_date
      if (!d || d === '未知') return 'stale'
      // 兼容 "2026-07-18" 和 "20260718" 两种格式
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
    psychLevelClass(l) { return l === '优秀' || l === '良好' ? 'text-pos' : l === '一般' ? '' : 'text-neg' },
    maClass() { if (!this.result) return ''; const a = this.result.technical.ma_alignment; return a === 'BULL' ? 'text-pos' : a === 'BEAR' ? 'text-neg' : '' },
    pickAnswer(idx, oi) { this.$set(this.psychAnswers, idx, oi) },
    async loadHistory() {
      try { const res = await getHistory(); this.history = res.data || [] } catch (e) { /* ignore */ }
    },
    async loadHistoryItem(h) {
      try {
        const res = await getHistoryDetail(h.id)
        const detail = res.data
        if (detail && detail.result) {
          this.result = detail.result
          this.historyLoadedId = h.id
          // 回填输入值到表单（供参考）
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
/* ═══════════════════════════════════════════
   SPAS — Premium Trading Analysis UI
   Inspired by TradingView · Binance · Bloomberg
   ═══════════════════════════════════════════ */

/* ── Tokens ── */
.spas {
  --bg: #08080C;
  --surface: #0C0C12;
  --surface-hover: #111118;
  --border: rgba(255,255,255,0.06);
  --border-active: rgba(240,185,11,0.25);
  --gold: #F0B90B;
  --gold-soft: rgba(240,185,11,0.10);
  --green: #0ECB81;
  --red: #F6465D;
  --blue: #3B82F6;
  --text: #EAECEF;
  --text2: #848E9C;
  --text3: #5E6673;
  --radius: 12px;
  --radius-sm: 8px;
  font-family: -apple-system, 'Inter', 'Segoe UI', sans-serif;
  color: var(--text);
  max-width: 1100px;
}

/* ── Header ── */
.spas-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 2rem; padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}
.breadcrumb { font-size: 0.72rem; color: var(--text3); margin-bottom: 0.6rem; letter-spacing: 0.04em; text-transform: uppercase; }
.breadcrumb a { color: var(--text3); text-decoration: none; }
.breadcrumb a:hover { color: var(--gold); }
.breadcrumb .sep { margin: 0 0.4rem; }
.breadcrumb .current { color: var(--gold); }
.title { font-size: 1.65rem; font-weight: 700; letter-spacing: -0.02em; margin: 0; }
.title-dim { color: var(--text3); font-weight: 400; }
.header-right { display: flex; align-items: center; gap: 0.8rem; }

.data-badge {
  display: flex; align-items: center; gap: 0.4rem;
  padding: 0.35rem 0.7rem; border-radius: 20px;
  font-size: 0.7rem; font-weight: 500; letter-spacing: 0.03em;
  background: var(--surface); border: 1px solid var(--border);
}
.badge-dot { width: 6px; height: 6px; border-radius: 50%; }
.data-badge.fresh .badge-dot { background: var(--green); box-shadow: 0 0 6px rgba(14,203,129,0.4); }
.data-badge.warn .badge-dot { background: var(--gold); box-shadow: 0 0 6px rgba(240,185,11,0.4); }
.data-badge.stale .badge-dot { background: var(--red); box-shadow: 0 0 6px rgba(246,70,93,0.4); }
.data-badge.fresh .badge-text { color: var(--green); }
.data-badge.warn .badge-text { color: var(--gold); }
.data-badge.stale .badge-text { color: var(--red); }

.btn-ghost {
  display: flex; align-items: center; gap: 0.35rem;
  padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.7rem;
  background: transparent; border: 1px solid var(--border);
  color: var(--text2); cursor: pointer; transition: all 0.2s;
  letter-spacing: 0.03em;
}
.btn-ghost:hover { border-color: var(--gold); color: var(--gold); background: var(--gold-soft); }
.btn-ghost:disabled { opacity: 0.3; cursor: not-allowed; }
.btn-icon { font-size: 0.85rem; }

/* ── Stepper ── */
.stepper {
  margin-bottom: 2.5rem; padding: 0 0.5rem;
}
.stepper-track {
  position: relative; height: 2px; background: rgba(255,255,255,0.08);
  border-radius: 1px; margin: 0 22px 0.8rem;
}
.stepper-fill {
  height: 100%; border-radius: 1px;
  background: linear-gradient(90deg, var(--gold), #FCD535);
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 6px rgba(240,185,11,0.3);
}
.stepper-stops {
  display: flex; justify-content: space-between;
}
.stepper-stop {
  display: flex; flex-direction: column; align-items: center; gap: 0.4rem;
  opacity: 0.35; transition: opacity 0.35s;
}
.stepper-stop.done, .stepper-stop.current { opacity: 1; }
.stop-node {
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.68rem; font-weight: 700;
  background: var(--surface); border: 2px solid rgba(255,255,255,0.10);
  color: var(--text3); transition: all 0.3s;
}
.stepper-stop.current .stop-node {
  border-color: var(--gold); color: var(--gold);
  background: var(--gold-soft); box-shadow: 0 0 10px rgba(240,185,11,0.15);
}
.stepper-stop.done .stop-node {
  border-color: var(--green); background: rgba(14,203,129,0.12);
  color: var(--green);
}
.stop-label {
  font-size: 0.62rem; font-weight: 500; color: var(--text2);
  text-transform: uppercase; letter-spacing: 0.06em;
}
.stepper-stop.current .stop-label { color: var(--gold); }
.stepper-stop.done .stop-label { color: var(--green); }

/* ── Panel ── */
.panel {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); margin-bottom: 1rem;
  overflow: hidden; transition: border-color 0.3s;
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
.panel-badge {
  font-size: 0.68rem; color: var(--text3); background: rgba(255,255,255,0.04);
  padding: 0.25rem 0.6rem; border-radius: 12px; letter-spacing: 0.03em;
}
.panel-badge.done { color: var(--green); background: rgba(14,203,129,0.08); }
.panel-tag {
  font-size: 0.65rem; color: var(--text3); padding: 0.2rem 0.5rem;
  background: rgba(255,255,255,0.03); border-radius: 6px; letter-spacing: 0.04em;
  text-transform: uppercase;
}
.panel-body { padding: 1.3rem; }

/* ── ETF Selector ── */
.select-main {
  width: 100%; max-width: 480px; padding: 0.7rem 0.9rem;
  background: var(--bg); border: 1px solid var(--border);
  border-radius: var(--radius-sm); color: var(--gold); font-size: 0.9rem;
  outline: none; cursor: pointer; transition: border-color 0.2s;
  appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23848E9C' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 0.8rem center;
}
.select-main:focus { border-color: var(--gold); box-shadow: 0 0 0 3px rgba(240,185,11,0.06); }
.etf-row { display: flex; align-items: center; gap: 0.8rem; }
.price-row { margin-top: 0.8rem; padding-top: 0.7rem; border-top: 1px solid var(--border); }
.price-label { font-size: 0.74rem; color: var(--text2); white-space: nowrap; }
.price-input {
  width: 150px; padding: 0.45rem 0.55rem;
  background: var(--bg); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text); font-size: 0.85rem;
  font-family: 'SF Mono', 'JetBrains Mono', monospace;
  outline: none; transition: border-color 0.2s;
}
.price-input:focus { border-color: var(--gold); box-shadow: 0 0 0 3px rgba(240,185,11,0.05); }
.price-input::placeholder { color: var(--text3); font-family: -apple-system, sans-serif; font-size: 0.75rem; }
.price-hint { font-size: 0.7rem; color: var(--text3); }
.price-hint.ok { color: var(--green); }
.etf-confirm { font-size: 0.78rem; color: var(--green); margin-left: 0.8rem; }

/* ── Indicator Grid ── */
.indicator-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 0.8rem; align-items: stretch; }
.field-group {
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  padding: 0.8rem 1rem; margin: 0; background: rgba(255,255,255,0.015);
  transition: border-color 0.25s;
  display: flex; flex-direction: column;
}
.field-group:hover { border-color: rgba(255,255,255,0.12); }
.field-group-prefs { border-color: rgba(240,185,11,0.12); background: rgba(240,185,11,0.02); }
.field-group legend {
  font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.08em; color: var(--text3); padding: 0 0.4rem;
  display: flex; align-items: center; gap: 0.4rem;
}
.legend-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
.legend-dot.dmi { background: var(--blue); }
.legend-dot.atr { background: #06B6D4; }
.legend-dot.asi { background: #A855F7; }
.legend-dot.macd { background: #F59E0B; }
.legend-dot.heat { background: #EF4444; }
.legend-dot.vol { background: #10B981; }
.legend-dot.obv { background: #EC4899; }
.legend-dot.market { background: #6366F1; }
.legend-dot.prefs { background: var(--gold); }
.legend-hint { font-size: 0.6rem; color: var(--text3); font-weight: 400; margin-left: 0.3rem; }

.field {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.35rem 0; gap: 0.5rem; min-height: 2rem;
}
.field:first-of-type { margin-top: auto; }
.field label {
  font-size: 0.74rem; color: var(--text2); white-space: nowrap;
  min-width: 70px; font-variant-numeric: tabular-nums;
}
.hint-sm {
  display: block; font-size: 0.58rem; color: var(--text3);
  font-weight: 400; letter-spacing: 0.02em;
}
.field input, .field select {
  width: 130px; padding: 0.4rem 0.55rem;
  background: var(--bg); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text); font-size: 0.8rem;
  font-family: 'SF Mono', 'JetBrains Mono', 'Consolas', monospace;
  text-align: right; outline: none; transition: all 0.2s;
  appearance: none;
}
.field select {
  text-align: left; cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 10 10'%3E%3Cpath fill='%23848E9C' d='M5 7L1 3h8z'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 0.5rem center;
}
.field input:focus, .field select:focus {
  border-color: var(--gold);
  box-shadow: 0 0 0 3px rgba(240,185,11,0.05);
}
.field input::placeholder { color: var(--text3); }

/* ── Psychology ── */
.psych-list { display: flex; flex-direction: column; gap: 0.6rem; }
.psych-card {
  display: flex; gap: 1rem; padding: 1rem;
  background: rgba(255,255,255,0.015); border: 1px solid var(--border);
  border-radius: var(--radius-sm); transition: all 0.3s;
}
.psych-card.done { border-color: rgba(14,203,129,0.2); background: rgba(14,203,129,0.03); }
.psych-num {
  font-size: 1.1rem; font-weight: 700; color: var(--text3);
  font-variant-numeric: tabular-nums; min-width: 28px;
  font-family: 'SF Mono', 'JetBrains Mono', monospace;
}
.psych-card.done .psych-num { color: var(--green); }
.psych-content { flex: 1; }
.psych-question { font-size: 0.85rem; color: var(--text); margin: 0 0 0.5rem; line-height: 1.5; }
.psych-options { display: grid; grid-template-columns: 1fr 1fr; gap: 0.35rem; }
.opt-chip {
  display: flex; align-items: flex-start; gap: 0.5rem;
  padding: 0.55rem 0.7rem; text-align: left;
  background: var(--bg); border: 1px solid var(--border);
  border-radius: 8px; cursor: pointer; transition: all 0.2s;
  font-size: 0.73rem; color: var(--text2); line-height: 1.35;
  font-family: inherit;
}
.opt-chip:hover { border-color: rgba(255,255,255,0.15); background: var(--surface-hover); }
.opt-chip.picked {
  border-color: var(--gold); background: var(--gold-soft);
  color: var(--gold);
}
.chip-key {
  font-size: 0.62rem; font-weight: 700; padding: 0.1rem 0.3rem;
  border-radius: 4px; background: rgba(255,255,255,0.06); color: var(--text3);
  flex-shrink: 0; margin-top: 0.1rem;
}
.opt-chip.picked .chip-key { background: rgba(240,185,11,0.2); color: var(--gold); }
.chip-text { flex: 1; }

/* ── Action Bar ── */
.action-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.2rem 1.5rem; margin-bottom: 2rem;
  background: linear-gradient(135deg, rgba(240,185,11,0.03), rgba(240,185,11,0.06));
  border: 1px solid rgba(240,185,11,0.15); border-radius: var(--radius);
}
.action-status { display: flex; align-items: center; gap: 0.6rem; font-size: 0.82rem; color: var(--text2); }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.active { background: var(--green); box-shadow: 0 0 8px rgba(14,203,129,0.5); animation: pulse-dot 2s infinite; }
@keyframes pulse-dot { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

.btn-analyze {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.7rem 1.8rem; border: none; border-radius: 10px;
  font-size: 0.88rem; font-weight: 600; cursor: pointer;
  letter-spacing: 0.02em;
  background: linear-gradient(135deg, #F0B90B, #FCD535);
  color: #0A0A0B; transition: all 0.25s;
  box-shadow: 0 2px 12px rgba(240,185,11,0.25);
}
.btn-analyze:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(240,185,11,0.35); }
.btn-analyze:active { transform: translateY(0); }
.btn-analyze:disabled { opacity: 0.4; cursor: not-allowed; transform: none; box-shadow: none; }
.spinner {
  width: 16px; height: 16px; border: 2px solid transparent;
  border-top-color: #0A0A0B; border-radius: 50%;
  animation: spin 0.7s linear infinite; display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Results Hero ── */
.hero-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; margin-bottom: 1rem; }
.hero-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.5rem 1rem;
  text-align: center; transition: all 0.3s; position: relative; overflow: hidden;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 200px;
}
.hero-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: transparent; transition: background 0.3s;
}
.hero-card.bullish::before { background: var(--green); }
.hero-card.bearish::before { background: var(--red); }
.hero-card.position::before { background: var(--blue); }
.hero-card.danger::before { background: var(--red); }
.hero-card.success::before { background: var(--green); }
.hero-label { font-size: 0.7rem; color: var(--text3); text-transform: uppercase; letter-spacing: 0.08em; margin: 0.6rem 0 0.4rem; }
.hero-badge {
  font-size: 0.65rem; padding: 0.2rem 0.5rem; border-radius: 10px; display: inline-block;
  letter-spacing: 0.04em;
}
.hero-badge.bullish, .hero-badge.good { background: rgba(14,203,129,0.1); color: var(--green); }
.hero-badge.bearish, .hero-badge.bad { background: rgba(246,70,93,0.1); color: var(--red); }
.hero-big-num { margin: 0.5rem 0; }
.big-value { font-size: 2rem; font-weight: 700; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }
.big-unit { font-size: 0.85rem; color: var(--text3); margin-left: 0.15rem; }

/* Ring chart */
.hero-ring { position: relative; width: 120px; height: 120px; margin: 0 auto; }
.ring-svg { width: 120px; height: 120px; transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: rgba(255,255,255,0.05); stroke-width: 6; }
.ring-fill { fill: none; stroke: var(--gold); stroke-width: 6; stroke-linecap: round; transition: stroke-dashoffset 1s ease-out; }
.ring-center { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ring-value { font-size: 1.6rem; font-weight: 700; line-height: 1; letter-spacing: -0.03em; }
.ring-unit { font-size: 0.65rem; color: var(--text3); }

/* ── Factor List ── */
.factor-list { display: flex; flex-direction: column; gap: 0.3rem; }
.factor-row {
  display: flex; align-items: center; gap: 1rem;
  padding: 0.5rem 0.7rem; border-radius: 6px;
  transition: background 0.2s;
}
.factor-row:hover { background: rgba(255,255,255,0.02); }
.factor-row.pos { background: linear-gradient(90deg, rgba(14,203,129,0.04), transparent); }
.factor-row.neg { background: linear-gradient(90deg, rgba(246,70,93,0.04), transparent); }
.factor-left { flex: 0 0 160px; min-width: 0; }
.factor-name { font-size: 0.78rem; font-weight: 500; color: var(--text); display: block; }
.factor-detail { font-size: 0.65rem; color: var(--text3); display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.factor-bar-wrap { flex: 1; height: 4px; background: rgba(255,255,255,0.04); border-radius: 2px; overflow: hidden; }
.factor-bar { height: 100%; border-radius: 2px; transition: width 0.8s ease-out; }
.bar-pos { background: var(--green); }
.bar-neg { background: var(--red); }
.bar-neutral { background: var(--text3); }
.factor-val { flex: 0 0 45px; text-align: right; font-size: 0.75rem; font-weight: 600; font-variant-numeric: tabular-nums; }
.text-pos { color: var(--green) !important; }
.text-neg { color: var(--red) !important; }

/* ── Two Column Layout ── */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; align-items: stretch; }
.two-col .panel { display: flex; flex-direction: column; margin-bottom: 0; }
.two-col .panel-body { flex: 1; }

/* ── KV Grid ── */
.kv-grid { display: flex; flex-direction: column; gap: 0.25rem; }
.kv { display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0.6rem; border-radius: 6px; }
.kv:nth-child(even) { background: rgba(255,255,255,0.015); }
.kv.highlight { background: rgba(240,185,11,0.05); border: 1px solid rgba(240,185,11,0.12); border-radius: 8px; }
.kv dt { font-size: 0.72rem; color: var(--text3); }
.kv dd { font-size: 0.85rem; font-weight: 500; font-variant-numeric: tabular-nums; }
.kv-dim { font-size: 0.65rem; color: var(--text3); }

/* ── Alerts ── */
.alerts { margin-top: 0.6rem; display: flex; flex-direction: column; gap: 0.3rem; }
.alert {
  font-size: 0.72rem; padding: 0.4rem 0.7rem;
  background: rgba(240,185,11,0.06); border: 1px solid rgba(240,185,11,0.15);
  border-radius: 6px; color: var(--gold);
}

/* ── Tech Strip ── */
.tech-strip {
  display: flex; flex-wrap: wrap; gap: 0.25rem; align-items: stretch;
}
.tech-item {
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.2rem;
  padding: 0.5rem 0.8rem; border-radius: 6px; min-width: 72px; min-height: 48px;
  background: rgba(255,255,255,0.015); border: 1px solid transparent;
  transition: all 0.2s;
}
.tech-item:hover { border-color: var(--border); background: rgba(255,255,255,0.03); }
.tech-label { font-size: 0.58rem; color: var(--text3); text-transform: uppercase; letter-spacing: 0.06em; }
.tech-val { font-size: 0.82rem; font-weight: 600; font-variant-numeric: tabular-nums; font-family: 'SF Mono', 'JetBrains Mono', monospace; }
.tech-sep { width: 1px; height: 20px; background: var(--border); margin: 0 0.2rem; }

/* ── History ── */
.history-row {
  display: flex; align-items: center; gap: 0.8rem;
  padding: 0.65rem 1.3rem; border-bottom: 1px solid var(--border);
  cursor: pointer; transition: background 0.15s;
}
.history-row:last-child { border-bottom: none; }
.history-row:hover { background: rgba(255,255,255,0.025); }
.h-date { font-size: 0.7rem; color: var(--text3); min-width: 110px; font-family: 'SF Mono', monospace; }
.h-etf { flex: 1; font-size: 0.78rem; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.h-dir { font-size: 0.7rem; font-weight: 500; min-width: 36px; text-align: center; }
.h-prob { font-size: 0.82rem; font-weight: 600; min-width: 40px; text-align: right; font-variant-numeric: tabular-nums; }
.h-pos { font-size: 0.78rem; color: var(--text2); min-width: 45px; text-align: right; }
.h-del {
  width: 22px; height: 22px; border-radius: 50%; border: 1px solid transparent;
  background: transparent; color: var(--text3); font-size: 0.6rem;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.15s; flex-shrink: 0;
}
.h-del:hover { border-color: var(--red); color: var(--red); background: rgba(246,70,93,0.08); }

/* ── Responsive ── */
@media (max-width: 768px) {
  .hero-grid { grid-template-columns: 1fr 1fr; }
  .two-col { grid-template-columns: 1fr; }
  .psych-options { grid-template-columns: 1fr; }
  .indicator-grid { grid-template-columns: 1fr; }
  .factor-left { flex: 0 0 100px; }
  .progress-line { width: 30px; }
}
</style>
