<template>
  <div class="manual-analysis ia-page">
    <IAPageHeader
      title="SPAS"
      title-highlight="手动指标分析"
      subtitle="输入你从同花顺/东方财富获取的指标，系统合成决策参考"
      :breadcrumbs="[{ label: '首页', to: '/' }, { label: '手动指标分析' }]"
    >
      <template #actions>
        <div class="data-badge" :class="dataAgeClass">
          <IAIcon name="calendar" size="sm" />
          <span>{{ sysInfo.data_latest_date || '数据日期未知' }}</span>
        </div>
        <IATooltip content="从 akshare 下载最新 ETF 日线数据，可能需要 1-2 分钟">
          <IAButton variant="ghost" size="sm" :loading="updating" @click="doUpdateData">
            <IAIcon name="arrow-down" v-if="!updating" size="sm" />
            更新数据
          </IAButton>
        </IATooltip>
      </template>
    </IAPageHeader>

    <!-- Setup -->
    <IAPanel title="分析标的" subtitle="选择 ETF 并填入实时价格" icon="market">
      <div class="setup-bar">
        <div class="setup-field">
          <label class="ia-label">ETF</label>
          <select v-model="selectedETF" class="ia-select">
            <option value="" disabled>选择 ETF</option>
            <option v-for="etf in etfList" :key="etf.code" :value="etf.code">
              {{ etfNameMap[etf.code] || etf.code }}
            </option>
          </select>
        </div>
        <div class="setup-field">
          <label class="ia-label">实时价格</label>
          <input
            type="number"
            v-model.number="form.current_price"
            step="0.001"
            min="0"
            placeholder="同花顺最新价"
            class="ia-input"
          />
        </div>
        <div class="setup-actions">
          <IAButton variant="secondary" size="sm" @click="fillDemo">演示数据</IAButton>
          <IAButton variant="ghost" size="sm" @click="resetForm">清空</IAButton>
          <IAButton
            variant="primary"
            size="sm"
            :loading="analyzing"
            :disabled="!canAnalyze"
            @click="runAnalysis"
          >
            <IAIcon name="activity" v-if="!analyzing" size="sm" />
            运行分析
          </IAButton>
        </div>
      </div>

      <div v-if="validationErrors.length" class="validation-summary ia-alert ia-alert--warning">
        <IAIcon name="warning" size="sm" />
        <div>
          <strong>还有 {{ validationErrors.length }} 项未填写：</strong>
          <span class="error-list">{{ validationErrors.map(e => e.label).join('、') }}</span>
        </div>
      </div>
    </IAPanel>

    <!-- Workspace: indicators + psychology -->
    <div class="workspace">
      <IAPanel
        class="workspace-col"
        title="技术指标"
        :subtitle="`已填 ${filledIndicatorCount}/${totalIndicatorCount}`"
        icon="analysis"
      >
        <div class="indicator-groups">
          <div
            v-for="section in indicatorSections"
            :key="section.title"
            class="indicator-group"
            :class="{ expanded: section.expanded }"
          >
            <button class="group-header" @click="section.expanded = !section.expanded">
              <span class="group-icon"><IAIcon :name="section.icon" size="sm" /></span>
              <span class="group-title">{{ section.title }}</span>
              <span class="group-count">{{ sectionFilledCount(section) }}/{{ section.fields.length }}</span>
              <IAIcon class="group-chevron" :name="section.expanded ? 'arrow-up' : 'arrow-down'" size="sm" />
            </button>
            <div v-show="section.expanded" class="group-body">
              <div class="group-fields">
                <div v-for="field in section.fields" :key="field.key" class="form-field">
                  <label :for="field.key">{{ field.label }}</label>
                  <input
                    v-if="field.type === 'number'"
                    :id="field.key"
                    type="number"
                    v-model.number="form[field.key]"
                    :step="field.step"
                    :min="field.min"
                    :max="field.max"
                    :placeholder="field.placeholder"
                    class="ia-input"
                    :class="{ 'is-filled': form[field.key] !== null && form[field.key] !== '' }"
                  />
                  <select
                    v-else-if="field.type === 'select'"
                    :id="field.key"
                    v-model="form[field.key]"
                    class="ia-select"
                    :class="{ 'is-filled': form[field.key] }"
                  >
                    <option value="" disabled>{{ field.placeholder || '—' }}</option>
                    <option v-for="opt in field.options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </IAPanel>

      <IAPanel
        class="workspace-col"
        title="交易心理"
        :subtitle="`${answeredCount}/10`"
        icon="brain"
      >
        <div class="psych-list">
          <div
            v-for="(q, idx) in psychQuestions"
            :key="idx"
            class="psych-item"
            :class="{ done: psychAnswers[idx] !== null }"
          >
            <div class="psych-header">
              <span class="psych-num">{{ String(idx + 1).padStart(2, '0') }}</span>
              <p class="psych-question">{{ q.text }}</p>
            </div>
            <div class="psych-options">
              <button
                v-for="(opt, oi) in q.options"
                :key="oi"
                :class="['opt-card', { picked: psychAnswers[idx] === oi }]"
                @click="pickAnswer(idx, oi)"
              >
                <span class="opt-key">{{ optionLabel(oi) }}</span>
                <span class="opt-text">{{ opt }}</span>
              </button>
            </div>
          </div>
        </div>
        <div class="psych-legend">
          <span>越靠前的选项代表状态越好</span>
        </div>
      </IAPanel>
    </div>

    <!-- Results -->
    <div v-if="result" class="results ia-anim-fade-in-up">
      <IASectionTitle title="分析结果" subtitle="SPAS 合成决策" icon="chart" />

      <div class="hero-grid ia-grid-4">
        <div class="hero-card glass-card" :class="result.probability.direction">
          <ProbabilityRing :value="result.probability.probability" :size="120" />
          <div class="hero-label">涨跌概率</div>
          <IABadge :variant="result.probability.direction === 'bullish' ? 'green' : result.probability.direction === 'bearish' ? 'red' : 'neutral'">
            {{ directionLabel(result.probability.direction) }}
          </IABadge>
        </div>

        <div class="hero-card glass-card position">
          <div class="hero-big-num">
            <span class="big-value">{{ result.position.suggested_position_pct.toFixed(1) }}</span>
            <span class="big-unit">%</span>
          </div>
          <div class="hero-label">建议仓位</div>
          <IABadge :variant="result.position.suggested_position_pct > 0 ? 'green' : 'neutral'">
            {{ result.position.suggested_position_pct > 0 ? 'Kelly' : '不建议交易' }}
          </IABadge>
        </div>

        <div class="hero-card glass-card danger">
          <div class="hero-big-num">
            <span class="big-value">{{ result.risk.stop_loss_price.toFixed(2) }}</span>
          </div>
          <div class="hero-label">止损</div>
          <IABadge variant="red">{{ result.risk.stop_loss_pct.toFixed(1) }}%</IABadge>
        </div>

        <div class="hero-card glass-card success">
          <div class="hero-big-num">
            <span class="big-value">{{ result.risk.take_profit_price.toFixed(2) }}</span>
          </div>
          <div class="hero-label">止盈</div>
          <IABadge variant="green">+{{ result.risk.take_profit_pct.toFixed(1) }}%</IABadge>
        </div>
      </div>

      <div class="ia-grid-2 detail-grid">
        <IAPanel title="概率因子分解" icon="chart">
          <div class="factor-list">
            <FactorBar
              v-for="f in result.probability.factors"
              :key="f.factor"
              :factor="f.factor"
              :detail="f.detail"
              :contribution="f.contribution"
            />
          </div>
        </IAPanel>

        <IAPanel title="仓位与风控" icon="warning">
          <dl class="kv-grid">
            <div class="kv"><dt>Kelly f*</dt><dd>{{ (result.position.kelly_f_star * 100).toFixed(1) }}%</dd></div>
            <div class="kv"><dt>¼ Kelly</dt><dd>{{ (result.position.kelly_fractional * 100).toFixed(2) }}%</dd></div>
            <div class="kv"><dt>心理评分</dt><dd>{{ result.position.psychology_score }}<span>/{{ psychMaxScore }}</span></dd></div>
            <div class="kv"><dt>心理等级</dt><dd :class="psychLevelClass(result.position.psychology_level)">{{ result.position.psychology_level }}</dd></div>
            <div class="kv"><dt>R:R</dt><dd>{{ result.risk.rr_ratio.toFixed(1) }}:1</dd></div>
            <div class="kv"><dt>ATR(14)</dt><dd>{{ result.risk.atr.toFixed(4) }}</dd></div>
            <div class="kv"><dt>止损幅度</dt><dd class="ia-text-red">{{ result.risk.stop_loss_pct.toFixed(1) }}%</dd></div>
            <div class="kv"><dt>止盈幅度</dt><dd class="ia-text-green">+{{ result.risk.take_profit_pct.toFixed(1) }}%</dd></div>
          </dl>
          <div v-if="result.position.psychology_warnings.length" class="alerts">
            <div v-for="w in result.position.psychology_warnings" :key="w" class="ia-alert ia-alert--warning">
              <IAIcon name="warning" size="sm" />{{ w }}
            </div>
          </div>
          <div v-if="result.risk.atr_warning" class="ia-alert ia-alert--danger">
            <IAIcon name="warning" size="sm" />ATR 值异常，请检查是否填错
          </div>
          <div v-if="result.risk.tp_capped" class="ia-alert ia-alert--warning">
            <IAIcon name="warning" size="sm" />止盈已被安全上限限制
          </div>
          <div v-if="result.risk.stop_capped_by_max_loss" class="ia-alert ia-alert--warning">
            <IAIcon name="warning" size="sm" />止损已被最大亏损 ({{ form.max_loss_pct }}%) 限制
          </div>
        </IAPanel>
      </div>

      <IAPanel title="系统计算" icon="chart" tag="EMA · K线">
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
            <span class="tech-label">{{ klineFeatureLabel(key) }}</span>
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
      <div class="history-cards">
        <div v-for="h in history" :key="h.id" class="history-card" @click="openHistoryModal(h)">
          <div class="history-card__main">
            <div class="history-card__top">
              <span class="history-card__etf">{{ h.etf_name || h.etf_code }}</span>
              <IABadge :variant="h.direction === 'bullish' ? 'green' : h.direction === 'bearish' ? 'red' : 'neutral'">
                {{ directionLabel(h.direction) }}
              </IABadge>
            </div>
            <div class="history-card__meta">
              <span>{{ h.created_at }}</span>
              <span>概率 {{ (h.probability * 100).toFixed(0) }}%</span>
              <span>仓位 {{ h.position_pct.toFixed(1) }}%</span>
            </div>
          </div>
          <button
            class="history-card__del"
            :class="{ 'history-card__del--loading': deletingId === h.id }"
            :disabled="deletingId === h.id"
            @click.stop="doDeleteHistory(h.id)"
            title="删除"
          >
            <IAIcon v-if="deletingId !== h.id" name="trash" size="xs" />
            <IAIcon v-else name="spinner" size="xs" class="ia-anim-spin" />
          </button>
        </div>
      </div>
    </IAPanel>

    <!-- History Detail Modal -->
    <IAModal :visible="historyModalVisible" :title="historyModalTitle" @close="closeHistoryModal">
      <div class="history-detail" v-if="historyModalItem">
        <div class="hd-summary">
          <div class="hd-etf-row">
            <IAIcon name="market" size="md" />
            <span class="hd-etf-name">{{ historyModalItem.etf_name || historyModalItem.etf_code }}</span>
          </div>
          <div class="hd-grid">
            <div class="hd-cell">
              <span class="hd-label">时间</span>
              <span class="hd-value">{{ historyModalItem.created_at }}</span>
            </div>
            <div class="hd-cell">
              <span class="hd-label">方向</span>
              <IABadge :variant="historyModalItem.direction === 'bullish' ? 'green' : historyModalItem.direction === 'bearish' ? 'red' : 'neutral'">
                {{ directionLabel(historyModalItem.direction) }}
              </IABadge>
            </div>
            <div class="hd-cell">
              <span class="hd-label">涨跌概率</span>
              <span class="hd-value">{{ (historyModalItem.probability * 100).toFixed(0) }}%</span>
            </div>
            <div class="hd-cell">
              <span class="hd-label">建议仓位</span>
              <span class="hd-value">{{ historyModalItem.position_pct.toFixed(1) }}%</span>
            </div>
            <div class="hd-cell">
              <span class="hd-label">止损价</span>
              <span class="hd-value">{{ historyModalItem.stop_loss != null ? historyModalItem.stop_loss.toFixed(3) : '-' }}</span>
            </div>
            <div class="hd-cell">
              <span class="hd-label">止盈价</span>
              <span class="hd-value">{{ historyModalItem.take_profit != null ? historyModalItem.take_profit.toFixed(3) : '-' }}</span>
            </div>
            <div class="hd-cell">
              <span class="hd-label">心理评分</span>
              <span class="hd-value">{{ historyModalItem.psychology_score }} · {{ historyModalItem.psychology_level }}</span>
            </div>
            <div v-if="historyModalTurnoverRate != null" class="hd-cell">
              <span class="hd-label">换手率</span>
              <span class="hd-value">{{ historyModalTurnoverRate.toFixed(2) }}%</span>
            </div>
          </div>
        </div>

        <div class="hd-toggle">
          <IAButton variant="ghost" size="sm" @click="showHistoryInputs = !showHistoryInputs">
            <IAIcon :name="showHistoryInputs ? 'arrow-up' : 'arrow-down'" size="xs" />
            {{ showHistoryInputs ? '隐藏输入详情' : '查看输入详情' }}
          </IAButton>
        </div>

        <transition name="fade">
          <div ref="hdInputs" v-if="showHistoryInputs" class="hd-inputs">
            <div v-if="historyInputsDisplay">
              <div v-for="s in historyInputsDisplay.sections" :key="s.title" class="hd-input-section">
                <h4 class="hd-input-title">{{ s.title }}</h4>
                <div class="hd-input-grid">
                  <div v-for="f in s.fields" :key="f.label" class="hd-input-cell">
                    <span class="hd-input-label">{{ f.label }}</span>
                    <span class="hd-input-value">{{ f.value }}</span>
                  </div>
                </div>
              </div>
              <div class="hd-input-section">
                <h4 class="hd-input-title">风控参数</h4>
                <div class="hd-input-grid">
                  <div v-for="f in historyInputsDisplay.extra" :key="f.label" class="hd-input-cell">
                    <span class="hd-input-label">{{ f.label }}</span>
                    <span class="hd-input-value">{{ f.value }}</span>
                  </div>
                </div>
              </div>
              <div class="hd-input-section">
                <h4 class="hd-input-title">交易心理</h4>
                <div class="hd-psych-list">
                  <div v-for="(p, pIdx) in historyInputsDisplay.psych" :key="pIdx" class="hd-psych-item">
                    <div class="hd-psych-q">{{ pIdx + 1 }}. {{ p.question }}</div>
                    <div class="hd-psych-a">{{ p.answer }}</div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="hd-empty">暂无输入详情</div>
          </div>
        </transition>
      </div>
      <template #footer>
        <IAButton variant="ghost" size="lg" @click="closeHistoryModal">关闭</IAButton>
        <IAButton variant="primary" size="lg" @click="loadHistoryModalItem">载入当前分析</IAButton>
      </template>
    </IAModal>
  </div>
</template>

<script>
import { IAPageHeader, IAPanel, IABadge, IAButton, IAIcon, IASectionTitle, IATooltip, IAModal, ProbabilityRing, FactorBar } from '../components/ui'
import { analyzeETF, getSystemInfo, triggerDataUpdate, getHistory, getHistoryDetail, deleteHistory } from '../api/manualAnalysis'
import { getETFs, getETFName } from '../api/market'

const DEFAULT_FORM = {
  current_price: null,
  adx: null, plus_di: null, minus_di: null, atr: null,
  asi_value: null, asi_direction: '',
  dif: null, dea: null, macd_bar: '',
  rsi: null, wr: null,
  volume_ratio: null,
  turnover_rate: null,
  obv_direction: '',
  market_trend: '', market_adx: null,
  rr_ratio: 2.0, max_loss_pct: 5.0,
}

const DEMO_VALUES = {
  current_price: 1.234,
  adx: 28.5, plus_di: 24.3, minus_di: 16.8, atr: 0.045,
  asi_value: 1250, asi_direction: 'up',
  dif: 0.018, dea: -0.012, macd_bar: 'red_increasing',
  rsi: 58.2, wr: 35.0,
  volume_ratio: 1.45,
  turnover_rate: 2.5,
  obv_direction: 'up',
  market_trend: 'bull', market_adx: 32.0,
  rr_ratio: 2.0, max_loss_pct: 5.0,
}

export default {
  name: 'ManualAnalysis',
  components: { IAPageHeader, IAPanel, IABadge, IAButton, IAIcon, IASectionTitle, IATooltip, IAModal, ProbabilityRing, FactorBar },
  data() {
    return {
      sysInfo: {},
      etfList: [],
      etfNameMap: {},
      selectedETF: '',
      form: { ...DEFAULT_FORM },
      psychQuestions: [
        { text: '你进行这笔交易的主要动机是什么？', options: ['执行交易计划中已设定的策略', '基于自己的初步分析，但还不够系统', '看到别人在讨论/推荐这只ETF', '担心错过这波行情', '近期亏损想尽快回本', '没有明确动机，随手下单'] },
        { text: '你对这只ETF的了解程度？', options: ['深入研究过，了解其持仓和行业定位', '看过一些相关报告和新闻', '了解一些，但不够系统', '听说过这只ETF，知道大概方向', '不熟悉，凭感觉选的', '完全不了解'] },
        { text: '最近一周你的情绪状态如何？', options: ['平稳冷静，正常生活不受影响', '略有焦虑，但能自我调节', '有些焦虑，会时不时看盘', '比较焦虑，频繁查看账户', '非常焦虑，影响睡眠或日常', '情绪接近失控，急需暂停'] },
        { text: '如果买入后立即亏损5%，你会怎么做？', options: ['按原定止损计划执行，果断离场', '减仓观察，等确认方向后再决定', '重新分析基本面再决定去留', '加仓摊平成本等待反弹', '死扛不卖，相信总会涨回来', '加仓并取消止损'] },
        { text: '你对这笔交易盈利的信心有多大？', options: ['超过80%，有量化依据支撑', '约60%，信号总体向好', '约50%，胜算不确定', '约30%，把握不大', '不太确定能不能赚钱', '完全没概念，凭感觉'] },
        { text: '你上一次交易的结果怎样？', options: ['盈利了，按计划止盈出场', '盈亏不大，基本按计划执行', '亏损了，但按计划止损了', '盈利了，但没按计划提前卖了', '亏损了，而且没有按计划止损', '连续亏损，心态尚未恢复'] },
        { text: '你有明确的交易计划吗（入场理由/仓位/止损/止盈）？', options: ['有完整的书面计划，每次交易前都写好', '有大致思路，但没有明确数字', '心里有计划，但没有写下来', '大概想了一下，没有详细规划', '没有计划，看行情临时决定', '经常凭冲动下单'] },
        { text: '过去一个月你遵守交易计划了吗？', options: ['完全遵守，每笔交易都按计划执行', '大体遵守，但偶尔临场调整', '大部分遵守，偶尔小偏差', '偶尔遵守，常有临时冲动交易', '经常偏离计划，随心所欲交易', '几乎从未按计划执行'] },
        { text: '你对当前大盘环境的判断？', options: ['有清晰依据（技术面/基本面），方向明确', '有一定判断，但把握不大', '跟主流观点一致，比较有信心', '不太确定，感觉市场方向不明', '没有分析，凭感觉判断', '完全没关注大盘'] },
        { text: '你当前的仓位情况？', options: ['空仓或轻仓（< 总资金20%）', '轻仓（总资金20%-30%）', '中等仓位（总资金30%-50%）', '较重仓位（总资金50%-80%）', '满仓或接近满仓（> 80%）', '已加杠杆或借钱交易'] },
      ],
      psychAnswers: [null, null, null, null, null, null, null, null, null, null],
      indicatorSections: [
        {
          title: 'DMI 趋势',
          icon: 'activity',
          expanded: true,
          fields: [
            { key: 'adx', label: 'ADX', type: 'number', step: 0.1, min: 0, max: 100 },
            { key: 'plus_di', label: '+DI', type: 'number', step: 0.1 },
            { key: 'minus_di', label: '-DI', type: 'number', step: 0.1 },
            { key: 'atr', label: 'ATR(14)', type: 'number', step: 0.001, min: 0, placeholder: '0.000' },
          ],
        },
        {
          title: 'MACD 动量',
          icon: 'chart',
          expanded: true,
          fields: [
            { key: 'dif', label: 'DIF', type: 'number', step: 0.001, placeholder: '0.000' },
            { key: 'dea', label: 'DEA', type: 'number', step: 0.001, placeholder: '0.000' },
            {
              key: 'macd_bar', label: '柱状态', type: 'select', placeholder: '选择',
              options: [
                { value: 'red_increasing', label: '红柱增长' },
                { value: 'red_decreasing', label: '红柱缩短' },
                { value: 'green_increasing', label: '绿柱增长' },
                { value: 'green_decreasing', label: '绿柱缩短' },
              ],
            },
          ],
        },
        {
          title: 'ASI 振动',
          icon: 'analysis',
          expanded: false,
          fields: [
            { key: 'asi_value', label: 'ASI 值', type: 'number', step: 0.1 },
            {
              key: 'asi_direction', label: '方向', type: 'select', placeholder: '选择',
              options: [
                { value: 'up', label: '上升' },
                { value: 'down', label: '下降' },
                { value: 'flat', label: '持平' },
              ],
            },
          ],
        },
        {
          title: '超买超卖',
          icon: 'warning',
          expanded: true,
          fields: [
            { key: 'rsi', label: 'RSI(14)', type: 'number', step: 0.1, min: 0, max: 100 },
            { key: 'wr', label: 'WR(14)', type: 'number', step: 0.1, min: 0, max: 100 },
          ],
        },
        {
          title: '量价',
          icon: 'market',
          expanded: false,
          fields: [
            { key: 'volume_ratio', label: '量比', type: 'number', step: 0.01, min: 0, placeholder: '1.0' },
            { key: 'turnover_rate', label: '换手率 %', type: 'number', step: 0.01, min: 0, placeholder: '2.5' },
            {
              key: 'obv_direction', label: 'OBV 方向', type: 'select', placeholder: '选择',
              options: [
                { value: 'up', label: '上升' },
                { value: 'down', label: '下降' },
                { value: 'flat', label: '持平' },
              ],
            },
          ],
        },
        {
          title: '大盘环境',
          icon: 'market',
          expanded: false,
          fields: [
            {
              key: 'market_trend', label: '趋势', type: 'select', placeholder: '选择',
              options: [
                { value: 'bull', label: '多头' },
                { value: 'range', label: '震荡' },
                { value: 'bear', label: '空头' },
              ],
            },
            { key: 'market_adx', label: 'ADX', type: 'number', step: 0.1, min: 0, max: 100 },
          ],
        },
        {
          title: '偏好',
          icon: 'analysis',
          expanded: false,
          fields: [
            { key: 'rr_ratio', label: 'R:R 比', type: 'number', step: 0.1, min: 1, max: 5 },
            { key: 'max_loss_pct', label: '最大亏损 %', type: 'number', step: 0.1, min: 1, max: 15 },
          ],
        },
      ],
      analyzing: false,
      updating: false,
      result: null,
      history: [],
      historyLoadedId: null,
      historyModalVisible: false,
      historyModalItem: null,
      historyModalDetail: null,
      showHistoryInputs: false,
      activeTab: 'indicators',
      deletingId: null,
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
    psychMaxScore() {
      return this.psychQuestions.reduce((sum, q) => sum + (q.options.length - 1), 0)
    },
    totalIndicatorCount() {
      return this.indicatorSections.reduce((sum, s) => sum + s.fields.length, 0)
    },
    filledIndicatorCount() {
      let c = 0
      for (const s of this.indicatorSections) {
        for (const f of s.fields) {
          const v = this.form[f.key]
          if (v !== null && v !== '') c++
        }
      }
      return c
    },
    validationErrors() {
      const errors = []
      if (!this.selectedETF) errors.push({ key: 'etf', label: 'ETF' })
      let missingIndicators = 0
      for (const s of this.indicatorSections) {
        for (const f of s.fields) {
          const v = this.form[f.key]
          if (v === null || v === '') missingIndicators++
        }
      }
      if (missingIndicators > 0) errors.push({ key: 'indicators', label: `技术指标（${missingIndicators} 项）` })
      if (!this.psychAllAnswered) errors.push({ key: 'psychology', label: '心理测评' })
      return errors
    },
    canAnalyze() {
      return this.selectedETF && this.filledIndicatorCount === this.totalIndicatorCount && this.psychAllAnswered
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
    historyModalTitle() {
      return this.historyModalItem ? (this.historyModalItem.etf_name || this.historyModalItem.etf_code) : '历史记录'
    },
    historyInputsDisplay() {
      if (!this.historyModalDetail || !this.historyModalDetail.inputs) return null
      const inputs = this.historyModalDetail.inputs
      const sections = this.indicatorSections.map(s => {
        const fields = s.fields
          .filter(f => inputs[f.key] !== undefined && inputs[f.key] !== null && inputs[f.key] !== '')
          .map(f => ({ label: f.label, value: f.type === 'select' ? this.selectLabel(f, inputs[f.key]) : inputs[f.key] }))
        return { title: s.title, fields }
      }).filter(s => s.fields.length)
      const extra = [
        { label: '实时价格', value: inputs.current_price },
        { label: '盈亏比', value: inputs.rr_ratio },
        { label: '最大亏损比例', value: inputs.max_loss_pct != null ? inputs.max_loss_pct + '%' : null },
      ].filter(i => i.value !== undefined && i.value !== null)
      const psychAnswers = inputs.psychology_answers || []
      const psych = psychAnswers.map((ans, idx) => {
        const q = this.psychQuestions[idx]
        if (!q) return null
        return { question: q.text, answer: q.options[ans] || '-' }
      }).filter(Boolean)
      return { sections, extra, psych }
    },
    historyModalTurnoverRate() {
      const inputs = this.historyModalDetail && this.historyModalDetail.inputs
      return inputs && inputs.turnover_rate != null ? inputs.turnover_rate : null
    },
  },
  watch: {
    showHistoryInputs(val) {
      if (val) {
        this.$nextTick(() => {
          setTimeout(() => this.scrollHistoryInputsIntoView(), 100)
        })
      }
    },
  },
  async created() {
    try {
      const [etfsRes, infoRes] = await Promise.all([getETFs(), getSystemInfo().catch(() => ({ data: {} }))])
      this.etfList = etfsRes.data || []
      this.sysInfo = infoRes.data || {}
      if (this.etfList.length) {
        for (const etf of this.etfList) {
          try { const nr = await getETFName(etf.code); this.$set(this.etfNameMap, etf.code, nr.data.display_name) } catch (e) {}
        }
      }
    } catch (e) { console.error(e) }
    this.loadHistory()
  },
  methods: {
    sectionFilledCount(section) {
      return section.fields.filter(f => {
        const v = this.form[f.key]
        return v !== null && v !== ''
      }).length
    },
    klineFeatureLabel(key) {
      const map = {
        body_ratio: '实体比',
        close_position: '收盘位置',
        upper_shadow: '上影线',
        lower_shadow: '下影线',
      }
      return map[key] || key
    },
    fillDemo() {
      if (this.etfList.length && !this.selectedETF) this.selectedETF = this.etfList[0].code
      this.form = { ...DEFAULT_FORM, ...DEMO_VALUES }
      this.indicatorSections.forEach(s => { s.expanded = true })
      this.psychAnswers = [0, 0, 1, 0, 1, 0, 0, 1, 0, 1]
    },
    resetForm() {
      this.form = { ...DEFAULT_FORM }
      this.psychAnswers = [null, null, null, null, null, null, null, null, null, null]
      this.result = null
      this.indicatorSections.forEach((s, i) => { s.expanded = i < 3 })
    },
    async doUpdateData() {
      this.updating = true
      try {
        const res = await triggerDataUpdate()
        if (res.data.success) {
          const infoRes = await getSystemInfo()
          this.sysInfo = infoRes.data || {}
          this.$toast(`更新完成：${res.data.updated}/${res.data.total} 只 ETF`, 'success')
        } else {
          this.$toast('更新失败', 'error')
        }
      } catch (e) {
        this.$toast('更新失败: ' + (e.response?.data?.detail || e.message), 'error')
      } finally {
        this.updating = false
      }
    },
    async runAnalysis() {
      this.analyzing = true
      this.result = null
      try {
        const payload = {
          ...this.form,
          psychology_answers: this.psychAnswers.map(a => a === null ? 0 : a),
          psychology_max_score: this.psychMaxScore,
        }
        const res = await analyzeETF(this.selectedETF, payload)
        this.result = res.data
        this.loadHistory()
        this.$nextTick(() => {
          const el = document.querySelector('.results')
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
        })
      } catch (e) {
        this.$toast('分析失败: ' + (e.response?.data?.detail || e.message), 'error')
      } finally {
        this.analyzing = false
      }
    },
    directionLabel(d) { return d === 'bullish' ? '看多' : d === 'bearish' ? '看空' : '中性' },
    selectLabel(field, value) {
      const opt = (field.options || []).find(o => o.value === value)
      return opt ? opt.label : value
    },
    psychLevelClass(l) { return l === '优秀' || l === '良好' ? 'ia-text-green' : l === '一般' ? '' : 'ia-text-red' },
    pickAnswer(idx, oi) { this.$set(this.psychAnswers, idx, oi) },
    optionLabel(oi) {
      return String.fromCharCode(65 + oi)
    },
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
          this.selectedETF = h.etf_code || detail.etf_code || ''
          if (detail.inputs) {
            const keep = ['psychology_answers']
            Object.keys(this.form).forEach(k => {
              if (detail.inputs[k] !== undefined && !keep.includes(k)) {
                this.form[k] = detail.inputs[k]
              }
            })
            if (detail.inputs.psychology_answers) {
              this.psychAnswers = detail.inputs.psychology_answers.map(a => a == null ? null : a)
            }
          }
          this.$nextTick(() => {
            const el = document.querySelector('.results')
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
          })
        }
      } catch (e) {
        this.$toast('加载历史失败: ' + (e.response?.data?.detail || e.message), 'error')
      }
    },
    async doDeleteHistory(id) {
      if (this.deletingId === id) return
      const ok = await this.$confirm({
        title: '删除记录',
        message: '删除这条记录？此操作不可撤销。',
        confirmText: '删除',
        cancelText: '取消',
      })
      if (!ok) return
      this.deletingId = id
      try {
        await deleteHistory(id)
        this.history = this.history.filter(h => h.id !== id)
        this.$toast('已删除', 'success')
      } catch (e) {
        this.$toast('删除失败', 'error')
      } finally {
        this.deletingId = null
      }
    },
    openHistoryModal(h) {
      this.historyModalItem = h
      this.historyModalDetail = null
      this.showHistoryInputs = false
      this.historyModalVisible = true
      this.$nextTick(() => {
        setTimeout(() => this.scrollHistoryModalToTop(), 100)
      })
      getHistoryDetail(h.id)
        .then(res => {
          this.historyModalDetail = res.data
          this.$nextTick(() => {
            setTimeout(() => this.scrollHistoryModalToTop(), 100)
          })
        })
        .catch(() => { this.$toast('加载详情失败', 'error') })
    },
    closeHistoryModal() {
      this.historyModalVisible = false
      this.historyModalItem = null
      this.historyModalDetail = null
      this.showHistoryInputs = false
    },
    loadHistoryModalItem() {
      if (!this.historyModalItem) return
      this.loadHistoryItem(this.historyModalItem)
      this.closeHistoryModal()
    },
    scrollHistoryModalToTop() {
      const modal = this.$el.querySelector('.ia-modal__body')
      if (modal) modal.scrollTop = 0
    },
    scrollHistoryInputsIntoView() {
      const el = this.$refs.hdInputs
      if (!el) return
      const body = el.closest('.ia-modal__body')
      if (!body) return
      const bodyRect = body.getBoundingClientRect()
      const elRect = el.getBoundingClientRect()
      const relativeTop = elRect.top - bodyRect.top + body.scrollTop
      body.scrollTo({ top: Math.max(0, relativeTop - 16), behavior: 'smooth' })
    },
  },
}
</script>

<style scoped>
.manual-analysis {
  padding-bottom: var(--ia-space-xl);
}

/* Data badge */
.data-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.75rem;
  border-radius: var(--ia-radius-full);
  font-size: var(--ia-font-size-xs);
  font-weight: 500;
  background: var(--ia-surface-glass);
  border: 1px solid var(--ia-glass-border);
  color: var(--ia-text-secondary);
  backdrop-filter: blur(var(--ia-glass-blur));
  -webkit-backdrop-filter: blur(var(--ia-glass-blur));
  box-shadow: var(--ia-shadow-inset);
}

.data-badge.fresh { color: var(--ia-green); border-color: rgba(14, 203, 129, 0.25); box-shadow: 0 0 14px rgba(14, 203, 129, 0.10); }
.data-badge.warn { color: var(--ia-gold); border-color: rgba(240, 185, 11, 0.25); box-shadow: 0 0 14px rgba(240, 185, 11, 0.10); }
.data-badge.stale { color: var(--ia-red); border-color: rgba(246, 70, 93, 0.25); box-shadow: 0 0 14px rgba(246, 70, 93, 0.10); }

/* Setup */
.setup-bar {
  display: flex;
  align-items: flex-end;
  gap: var(--ia-space-md);
  flex-wrap: wrap;
}

.setup-field {
  display: flex;
  flex-direction: column;
  gap: var(--ia-space-xs);
  min-width: 180px;
}

.setup-field .ia-select {
  min-width: 220px;
}

.setup-field .ia-input {
  width: 160px;
}

.setup-actions {
  display: flex;
  align-items: center;
  gap: var(--ia-space-sm);
  margin-left: auto;
}

.validation-summary {
  margin-top: var(--ia-space-md);
}

.error-list {
  color: var(--ia-text-secondary);
}

/* Workspace */
.workspace {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--ia-space-md);
  margin-bottom: var(--ia-space-xl);
}

.workspace-col {
  min-width: 0;
}

/* Indicator groups */
.indicator-groups {
  display: flex;
  flex-direction: column;
  gap: var(--ia-space-sm);
}

.indicator-group {
  border: 1px solid var(--ia-glass-border);
  border-radius: var(--ia-radius-sm);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.015);
  transition: border-color var(--ia-transition-fast), box-shadow var(--ia-transition-fast);
}

.indicator-group:hover {
  border-color: var(--ia-border-strong);
}

.group-header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: var(--ia-space-sm);
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  color: var(--ia-text);
  cursor: pointer;
  font-size: var(--ia-font-size-sm);
  font-family: inherit;
  transition: background var(--ia-transition-fast);
}

.group-header:hover {
  background: rgba(255, 255, 255, 0.025);
}

.group-icon {
  width: 30px;
  height: 30px;
  border-radius: var(--ia-radius-xs);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--ia-gold-soft);
  color: var(--ia-gold);
  border: 1px solid rgba(240, 185, 11, 0.12);
  flex-shrink: 0;
}

.group-title {
  flex: 1;
  text-align: left;
  font-weight: 500;
}

.group-count {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
  background: rgba(255, 255, 255, 0.03);
  padding: 0.15rem 0.45rem;
  border-radius: var(--ia-radius-xs);
}

.group-chevron {
  color: var(--ia-text-tertiary);
  transition: transform var(--ia-transition-fast);
}

.indicator-group.expanded .group-chevron {
  transform: rotate(180deg);
}

.group-body {
  padding: 0.6rem 1rem 1rem;
  border-top: 1px solid var(--ia-glass-border);
}

.group-fields {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--ia-space-sm);
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.form-field label {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-secondary);
  letter-spacing: 0.04em;
}

.form-field .ia-input,
.form-field .ia-select {
  width: 100%;
}

.form-field .is-filled {
  border-color: var(--ia-border-strong);
}

/* Psychology */
.psych-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.psych-item {
  padding: 1rem;
  border: 1px solid var(--ia-glass-border);
  border-radius: var(--ia-radius-sm);
  background: rgba(255, 255, 255, 0.015);
  transition: border-color var(--ia-transition-fast), box-shadow var(--ia-transition-fast), background var(--ia-transition-fast);
}

.psych-item:hover {
  border-color: var(--ia-border-strong);
  background: rgba(255, 255, 255, 0.025);
}

.psych-item.done {
  border-color: rgba(14, 203, 129, 0.25);
  background: rgba(14, 203, 129, 0.04);
  box-shadow: 0 0 14px rgba(14, 203, 129, 0.08);
}

.psych-header {
  display: flex;
  gap: 0.65rem;
  margin-bottom: 0.65rem;
}

.psych-num {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--ia-text-tertiary);
  font-family: var(--ia-font-mono);
  min-width: 22px;
  text-align: center;
  padding-top: 0.15rem;
}

.psych-item.done .psych-num {
  color: var(--ia-green);
}

.psych-question {
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text);
  margin: 0;
  line-height: 1.45;
}

.psych-options {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.opt-card {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.7rem 0.9rem;
  background: var(--ia-bg);
  border: 1px solid var(--ia-glass-border);
  border-radius: var(--ia-radius-sm);
  color: var(--ia-text-secondary);
  cursor: pointer;
  font-size: var(--ia-font-size-sm);
  text-align: left;
  transition: all var(--ia-transition-fast);
  width: 100%;
  position: relative;
  overflow: hidden;
  box-shadow: var(--ia-shadow-inset);
}

.opt-card:hover {
  border-color: var(--ia-glass-border-warm);
  background: var(--ia-surface-hover);
  transform: translateY(-2px);
  box-shadow: var(--ia-shadow-inset), var(--ia-shadow-sm);
}

.opt-card.picked {
  border-color: var(--ia-gold);
  background: var(--ia-gold-soft);
  color: var(--ia-gold);
  box-shadow: 0 0 18px rgba(240, 185, 11, 0.14), var(--ia-shadow-inset);
  font-weight: 500;
}

.opt-key {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--ia-radius-xs);
  background: rgba(255, 255, 255, 0.06);
  font-weight: 700;
  font-family: var(--ia-font-mono);
  font-size: var(--ia-font-size-xs);
  transition: background var(--ia-transition-fast);
}

.opt-card:hover .opt-key {
  background: rgba(255, 255, 255, 0.09);
}

.opt-card.picked .opt-key {
  background: rgba(240, 185, 11, 0.22);
  color: var(--ia-gold);
}

.opt-text {
  flex: 1;
  line-height: 1.4;
}

.psych-legend {
  display: flex;
  gap: var(--ia-space-md);
  margin-top: var(--ia-space-md);
  padding-top: var(--ia-space-md);
  border-top: 1px solid var(--ia-glass-border);
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
}

/* Results */
.results {
  margin-bottom: var(--ia-space-xl);
}

.hero-grid {
  margin-bottom: var(--ia-space-md);
}

.glass-card {
  background: var(--ia-surface-glass);
  border: 1px solid var(--ia-glass-border);
  border-radius: var(--ia-radius);
  padding: var(--ia-space-lg);
  box-shadow: var(--ia-shadow-inset), var(--ia-shadow-sm);
  backdrop-filter: blur(var(--ia-glass-blur));
  -webkit-backdrop-filter: blur(var(--ia-glass-blur));
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  position: relative;
  overflow: hidden;
  transition: border-color var(--ia-transition-base), box-shadow var(--ia-transition-base), transform var(--ia-transition-base);
}

.glass-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: transparent;
  transition: background var(--ia-transition-base);
}

.glass-card:hover {
  transform: translateY(-4px);
  border-color: var(--ia-glass-border-warm);
  box-shadow: var(--ia-shadow-md), var(--ia-shadow-inset), 0 0 24px rgba(240, 185, 11, 0.08);
}

.glass-card.bullish::before { background: var(--ia-green); }
.glass-card.bearish::before { background: var(--ia-red); }
.glass-card.position::before { background: var(--ia-blue); }
.glass-card.danger::before { background: var(--ia-red); }
.glass-card.success::before { background: var(--ia-green); }

.glass-card.bullish:hover { box-shadow: var(--ia-shadow-md), var(--ia-glow-green); }
.glass-card.bearish:hover { box-shadow: var(--ia-shadow-md), var(--ia-glow-red); }
.glass-card.position:hover { box-shadow: var(--ia-shadow-md), var(--ia-glow-blue); }
.glass-card.danger:hover { box-shadow: var(--ia-shadow-md), var(--ia-glow-red); }
.glass-card.success:hover { box-shadow: var(--ia-shadow-md), var(--ia-glow-green); }

.hero-label {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin: var(--ia-space-sm) 0 var(--ia-space-xs);
}

.hero-big-num {
  margin: var(--ia-space-sm) 0;
}

.big-value {
  font-size: var(--ia-font-size-3xl);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
  color: var(--ia-text);
}

.big-unit {
  font-size: 0.85rem;
  color: var(--ia-text-tertiary);
  margin-left: 0.15rem;
}

.detail-grid {
  margin-bottom: var(--ia-space-md);
}

.kv-grid {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.kv {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.45rem 0.6rem;
  border-radius: var(--ia-radius-xs);
}

.kv:nth-child(even) {
  background: rgba(255, 255, 255, 0.015);
}

.kv dt {
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text-tertiary);
}

.kv dd {
  font-size: var(--ia-font-size-md);
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  color: var(--ia-text);
}

.kv dd span {
  font-size: 0.65rem;
  color: var(--ia-text-tertiary);
  margin-left: 0.2rem;
}

.alerts {
  margin-top: var(--ia-space-md);
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.factor-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.tech-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: stretch;
}

.tech-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.55rem 0.85rem;
  border-radius: var(--ia-radius-xs);
  min-width: 72px;
  min-height: 52px;
  background: rgba(255, 255, 255, 0.015);
  border: 1px solid var(--ia-glass-border);
  transition: all var(--ia-transition-fast);
  box-shadow: var(--ia-shadow-inset);
}

.tech-item:hover {
  border-color: var(--ia-border-strong);
  background: rgba(255, 255, 255, 0.03);
  transform: translateY(-2px);
  box-shadow: var(--ia-shadow-sm);
}

.tech-label {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tech-val {
  font-size: var(--ia-font-size-md);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.tech-sep {
  width: 1px;
  background: var(--ia-glass-border);
  margin: 0 0.25rem;
}

/* History */
.history-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--ia-space-lg);
}

.history-card {
  display: flex;
  align-items: flex-start;
  gap: var(--ia-space-sm);
  padding: var(--ia-space-md);
  background: var(--ia-surface-glass);
  border: 1px solid var(--ia-glass-border);
  border-radius: var(--ia-radius);
  cursor: pointer;
  transition: all var(--ia-transition-fast);
  backdrop-filter: blur(var(--ia-glass-blur));
  -webkit-backdrop-filter: blur(var(--ia-glass-blur));
  box-shadow: var(--ia-shadow-inset);
}

.history-card:hover {
  border-color: var(--ia-glass-border-warm);
  background: var(--ia-gold-soft);
  transform: translateY(-3px);
  box-shadow: var(--ia-shadow-gold);
}

.history-card__main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--ia-space-sm);
}

.history-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--ia-space-sm);
}

.history-card__etf {
  font-size: var(--ia-font-size-md);
  font-weight: 600;
  color: var(--ia-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text-secondary);
}

.history-card__del {
  width: 34px;
  height: 34px;
  border-radius: var(--ia-radius-xs);
  border: 1px solid var(--ia-glass-border);
  background: transparent;
  color: var(--ia-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--ia-transition-fast);
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.history-card__del:hover:not(:disabled) {
  background: var(--ia-red-soft);
  border-color: var(--ia-red);
  color: var(--ia-red);
  box-shadow: 0 0 14px rgba(246, 70, 93, 0.12);
}

.history-card__del:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.history-card__del--loading {
  color: var(--ia-gold);
  border-color: var(--ia-gold);
  background: var(--ia-gold-soft);
}

/* History Detail Modal */
.history-detail {
  display: flex;
  flex-direction: column;
  gap: var(--ia-space-lg);
}

.hd-summary {
  background: var(--ia-surface-glass);
  border: 1px solid var(--ia-glass-border);
  border-radius: var(--ia-radius);
  padding: var(--ia-space-lg);
  box-shadow: var(--ia-shadow-inset);
}

.hd-etf-row {
  display: flex;
  align-items: center;
  gap: var(--ia-space-sm);
  margin-bottom: var(--ia-space-md);
  padding-bottom: var(--ia-space-md);
  border-bottom: 1px solid var(--ia-glass-border);
}

.hd-etf-row svg,
.hd-etf-row .ia-icon {
  color: var(--ia-gold);
}

.hd-etf-name {
  font-size: var(--ia-font-size-xl);
  font-weight: 600;
  color: var(--ia-text);
}

.hd-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--ia-space-md);
}

.hd-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.hd-label {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
  letter-spacing: 0.05em;
}

.hd-value {
  font-size: var(--ia-font-size-md);
  color: var(--ia-text);
  font-weight: 500;
}

.hd-toggle {
  display: flex;
  justify-content: center;
}

.hd-inputs {
  background: var(--ia-surface-glass);
  border: 1px solid var(--ia-glass-border);
  border-radius: var(--ia-radius);
  padding: var(--ia-space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--ia-space-lg);
  box-shadow: var(--ia-shadow-inset);
}

.hd-input-section {
  display: flex;
  flex-direction: column;
  gap: var(--ia-space-sm);
}

.hd-input-title {
  font-size: var(--ia-font-size-sm);
  color: var(--ia-gold);
  font-weight: 600;
  margin: 0;
  letter-spacing: 0.05em;
}

.hd-input-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--ia-space-sm);
}

.hd-input-cell {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--ia-radius-xs);
}

.hd-input-label {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
}

.hd-input-value {
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text);
  word-break: break-all;
}

.hd-psych-list {
  display: flex;
  flex-direction: column;
  gap: var(--ia-space-sm);
}

.hd-psych-item {
  padding: 0.65rem 0.8rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--ia-radius-xs);
  border: 1px solid var(--ia-glass-border);
}

.hd-psych-q {
  font-size: var(--ia-font-size-xs);
  color: var(--ia-text-tertiary);
  margin-bottom: 0.25rem;
  line-height: 1.4;
}

.hd-psych-a {
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text);
  line-height: 1.5;
}

.hd-empty {
  text-align: center;
  color: var(--ia-text-tertiary);
  font-size: var(--ia-font-size-sm);
  padding: var(--ia-space-md);
}

/* Responsive */
@media (max-width: 1100px) {
  .workspace {
    grid-template-columns: 1fr;
  }

  .workspace-col >>> .ia-panel__body {
    display: block;
  }

  .group-fields {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .setup-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .setup-field,
  .setup-field .ia-select,
  .setup-field .ia-input {
    width: 100%;
  }

  .setup-actions {
    margin-left: 0;
    justify-content: flex-end;
  }

  .group-fields {
    grid-template-columns: 1fr;
  }

  .psych-options {
    grid-template-columns: 1fr;
  }

  .opt-card {
    flex: 1 1 100%;
    width: 100%;
  }

  .history-cards {
    grid-template-columns: 1fr;
  }

  .hd-grid,
  .hd-input-grid {
    grid-template-columns: 1fr;
  }
}
</style>
