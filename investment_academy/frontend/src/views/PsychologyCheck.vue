<template>
  <div class="psych-page ia-page">
    <IAPageHeader
      title="交易心理自检"
      subtitle="评估当前心理状态，避免情绪化交易"
      :breadcrumbs="[{ label: '首页', to: '/' }, { label: '心理自检' }]"
    />

    <IAPanel title="交易前自检清单" icon="brain" :subtitle="`请根据你当前的状态如实作答（1=完全不符, 5=非常符合）— ${answeredCount}/10`">
      <p class="ia-hint" style="margin-bottom: var(--ia-space-md)">每题选择最符合你当前状态的选项</p>

      <div v-for="(q, i) in questions" :key="i" class="q-row">
        <div class="q-text">{{ i + 1 }}. {{ q.text }}</div>
        <div class="q-slider">
          <label v-for="n in 5" :key="n" class="q-radio" :class="{ picked: scores[q.key] === n }">
            <input type="radio" :value="n" v-model="scores[q.key]" />
            <span>{{ n }}</span>
          </label>
        </div>
      </div>

      <div class="ia-form-group">
        <label class="ia-label">补充备注</label>
        <textarea v-model="notes" class="ia-textarea" rows="2" placeholder="任何想记录的内容…"></textarea>
      </div>

      <IAButton variant="primary" :loading="submitting" :disabled="!allAnswered" @click="submitCheck">
        <IAIcon name="check" size="sm" />提交自检
      </IAButton>
      <p v-if="!allAnswered" class="ia-hint">请完成所有问题</p>
    </IAPanel>

    <IAPanel v-if="showResult" title="自检结果" icon="warning" class="result-panel">
      <h3 :class="riskClass" style="margin-bottom: var(--ia-space-sm)">
        <IAIcon name="warning" size="lg" />风险等级: {{ riskLabel }}
      </h3>
      <p class="risk-desc">{{ riskDesc }}</p>
      <div class="score-summary">
        <IABadge variant="neutral">总分: {{ totalScore }} / {{ questions.length * 5 }}</IABadge>
        <IABadge variant="neutral">均分: {{ avgScore.toFixed(1) }}</IABadge>
      </div>
      <p v-if="notes" class="notes-display">备注: {{ notes }}</p>
      <IAButton variant="secondary" @click="resetCheck">
        <IAIcon name="arrow-left" size="sm" />重新检测
      </IAButton>
    </IAPanel>

    <div class="ia-divider"></div>

    <IASectionTitle icon="clock" title="历史记录" />
    <div v-if="history.length" class="history-list">
      <div v-for="(h, i) in history" :key="i" class="history-item ia-card">
        <span class="h-time">{{ formatTime(h.timestamp) }}</span>
        <IABadge :variant="levelVariant(h.overall_risk_level)">{{ levelLabel(h.overall_risk_level) }}</IABadge>
        <span class="h-notes">{{ h.self_notes || '无备注' }}</span>
      </div>
    </div>
    <div v-else class="ia-empty">暂无历史记录</div>
  </div>
</template>

<script>
import { IAPageHeader, IASectionTitle, IAPanel, IAButton, IABadge, IAIcon } from '../components/ui'
import { addPsychologyCheck, getPsychologyHistory } from '../api/user'

const QUESTIONS = [
  { key: 'sleep', text: '昨晚睡眠充足，精神状态良好' },
  { key: 'focus', text: '能专注交易，不受外界干扰' },
  { key: 'calm', text: '情绪稳定，没有愤怒/焦虑/过度兴奋' },
  { key: 'confidence', text: '对当前策略有信心，不急于证明自己' },
  { key: 'plan', text: '有明确的交易计划，而非临时冲动' },
  { key: 'risk_accept', text: '能接受今天可能亏损，不会因此崩溃' },
  { key: 'no_fomo', text: '没有因为错过行情而产生的追涨冲动 (FOMO)' },
  { key: 'no_revenge', text: '没有想报复市场的念头 (复仇交易)' },
  { key: 'discipline', text: '会严格遵守止损和仓位规则' },
  { key: 'objectivity', text: '能客观看待市场，不固执于某一观点' },
]

export default {
  name: 'PsychologyCheck',
  components: { IAPageHeader, IASectionTitle, IAPanel, IAButton, IABadge, IAIcon },
  data() {
    return {
      questions: QUESTIONS,
      scores: {},
      notes: '',
      submitting: false,
      showResult: false,
      history: [],
    }
  },
  computed: {
    allAnswered() { return this.questions.every(q => this.scores[q.key] !== undefined) },
    answeredCount() { return this.questions.filter(q => this.scores[q.key] !== undefined).length },
    totalScore() { return Object.values(this.scores).reduce((s, v) => s + v, 0) },
    avgScore() { return this.totalScore / this.questions.length },
    riskLevel() {
      if (this.avgScore >= 3.5) return 'green'
      if (this.avgScore >= 2.0) return 'yellow'
      return 'red'
    },
    riskClass() { return 'result-' + this.riskLevel },
    riskLabel() {
      const map = { green: '低风险 — 适合交易', yellow: '中风险 — 谨慎交易', red: '高风险 — 不建议交易' }
      return map[this.riskLevel] || ''
    },
    riskDesc() {
      const map = {
        green: '你的心理状态良好，可以按计划执行交易。',
        yellow: '存在一些心理风险因素，建议降低仓位或仅做观察。',
        red: '当前心理状态不适合交易，建议休息、复盘、等待更好的时机。',
      }
      return map[this.riskLevel] || ''
    },
  },
  async created() { await this.loadHistory() },
  methods: {
    async submitCheck() {
      if (!this.allAnswered) return
      this.submitting = true
      try {
        await addPsychologyCheck({
          scores: this.scores,
          overall_risk_level: this.riskLevel,
          proceeded_to_trade: this.riskLevel !== 'red',
          self_notes: this.notes,
        })
        this.showResult = true
        await this.loadHistory()
      } catch (e) { alert('提交失败: ' + (e.response?.data?.detail || e.message)) }
      finally { this.submitting = false }
    },
    async loadHistory() {
      try {
        const res = await getPsychologyHistory()
        this.history = res.data || []
      } catch (e) { console.error('加载历史失败:', e) }
    },
    resetCheck() { this.scores = {}; this.notes = ''; this.showResult = false },
    formatTime(ts) { return ts ? ts.replace('T', ' ').substring(0, 19) : '' },
    levelLabel(l) {
      const map = { green: '低风险', yellow: '中风险', red: '高风险' }
      return map[l] || l
    },
    levelVariant(l) {
      const map = { green: 'green', yellow: 'gold', red: 'red' }
      return map[l] || 'neutral'
    },
  },
}
</script>

<style scoped>
.q-row { margin-bottom: var(--ia-space-md); padding: var(--ia-space-sm) 0; border-bottom: 1px solid var(--ia-border); }
.q-text { font-size: var(--ia-font-size-md); color: var(--ia-text); margin-bottom: var(--ia-space-sm); line-height: 1.5; }
.q-slider { display: flex; gap: var(--ia-space-sm); }
.q-radio {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  cursor: pointer;
  padding: 0.35rem 0.7rem;
  border-radius: var(--ia-radius-xs);
  border: 1px solid var(--ia-border);
  background: var(--ia-bg);
  transition: all 0.2s;
}
.q-radio span { font-size: var(--ia-font-size-sm); color: var(--ia-text-secondary); }
.q-radio input { accent-color: var(--ia-gold); }
.q-radio:hover { border-color: var(--ia-border-strong); }
.q-radio.picked { border-color: var(--ia-gold); background: var(--ia-gold-soft); color: var(--ia-gold); }
.q-radio.picked span { color: var(--ia-gold); }

.result-panel { margin-top: var(--ia-space-md); }
.result-green h3 { color: var(--ia-green); }
.result-yellow h3 { color: var(--ia-gold); }
.result-red h3 { color: var(--ia-red); }
.risk-desc { font-size: var(--ia-font-size-md); color: var(--ia-text-secondary); margin: var(--ia-space-sm) 0; }
.score-summary { display: flex; gap: var(--ia-space-md); margin-bottom: var(--ia-space-md); }
.notes-display { font-size: var(--ia-font-size-sm); color: var(--ia-text-secondary); margin-top: 0.3rem; }

.history-list { display: flex; flex-direction: column; gap: 0.4rem; }
.history-item { display: flex; align-items: center; gap: var(--ia-space-md); padding: 0.6rem 0.8rem; font-size: var(--ia-font-size-sm); }
.h-time { color: var(--ia-text-tertiary); min-width: 140px; font-variant-numeric: tabular-nums; }
.h-notes { color: var(--ia-text-secondary); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
