<template>
  <div class="psych-page">
    <div class="breadcrumb">
      <router-link to="/">首页</router-link>
      <span> / </span>
      <span><strong>交易心理自检</strong></span>
    </div>

    <h1>🧠 交易心理自检</h1>
    <p class="page-desc">评估当前心理状态，避免情绪化交易</p>

    <!-- 自检问卷 -->
    <div class="card">
      <h3>📋 交易前自检清单</h3>
      <p class="hint">请根据你当前的状态如实作答（1=完全不符, 5=非常符合）</p>

      <div v-for="(q, i) in questions" :key="i" class="q-row">
        <div class="q-text">{{ i + 1 }}. {{ q.text }}</div>
        <div class="q-slider">
          <label v-for="n in 5" :key="n" class="q-radio">
            <input type="radio" :value="n" v-model="scores[q.key]" />
            <span>{{ n }}</span>
          </label>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">补充备注</label>
        <textarea v-model="notes" class="styled-textarea" rows="2" placeholder="任何想记录的内容…"></textarea>
      </div>

      <button class="btn-submit" @click="submitCheck" :disabled="!allAnswered || submitting">
        {{ submitting ? '提交中…' : '提交自检' }}
      </button>
      <p v-if="!allAnswered" class="hint">请完成所有问题</p>
    </div>

    <!-- 结果弹窗 -->
    <div v-if="showResult" class="result-panel card">
      <h3 :class="riskClass">{{ resultIcon }} 风险等级: {{ riskLabel }}</h3>
      <p class="risk-desc">{{ riskDesc }}</p>
      <div class="score-summary">
        <span>总分: {{ totalScore }} / {{ questions.length * 5 }}</span>
        <span>均分: {{ avgScore.toFixed(1) }}</span>
      </div>
      <p v-if="notes" class="notes-display">备注: {{ notes }}</p>
      <button class="btn-reset" @click="resetCheck">重新检测</button>
    </div>

    <!-- 历史记录 -->
    <div class="divider"></div>
    <h2>📜 历史记录</h2>
    <div v-if="history.length" class="history-list">
      <div v-for="(h, i) in history" :key="i" class="history-item">
        <span class="h-time">{{ formatTime(h.timestamp) }}</span>
        <span class="h-level" :class="levelClass(h.overall_risk_level)">{{ levelLabel(h.overall_risk_level) }}</span>
        <span class="h-notes">{{ h.self_notes || '无备注' }}</span>
      </div>
    </div>
    <div v-else class="empty-state">暂无历史记录</div>
  </div>
</template>

<script>
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
  data() {
    return {
      questions: QUESTIONS,
      scores: {},
      notes: '',
      submitting: false,
      showResult: false,
      riskLevel: '',
      history: [],
    }
  },
  computed: {
    allAnswered() {
      return this.questions.every(q => this.scores[q.key] !== undefined)
    },
    totalScore() {
      return Object.values(this.scores).reduce((s, v) => s + v, 0)
    },
    avgScore() {
      return this.totalScore / this.questions.length
    },
    riskLevel() {
      if (this.avgScore >= 3.5) return 'green'
      if (this.avgScore >= 2.0) return 'yellow'
      return 'red'
    },
    riskClass() {
      return 'result-' + this.riskLevel
    },
    riskLabel() {
      const map = { green: '🟢 低风险 — 适合交易', yellow: '🟡 中风险 — 谨慎交易', red: '🔴 高风险 — 不建议交易' }
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
    resultIcon() {
      const map = { green: '✅', yellow: '⚠️', red: '🚫' }
      return map[this.riskLevel] || ''
    },
  },
  async created() {
    await this.loadHistory()
  },
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
      } catch (e) {
        alert('提交失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        this.submitting = false
      }
    },
    async loadHistory() {
      try {
        const res = await getPsychologyHistory()
        this.history = res.data || []
      } catch (e) {
        console.error('加载历史失败:', e)
      }
    },
    resetCheck() {
      this.scores = {}
      this.notes = ''
      this.showResult = false
    },
    formatTime(ts) {
      if (!ts) return ''
      return ts.replace('T', ' ').substring(0, 19)
    },
    levelLabel(l) {
      const map = { green: '🟢 低风险', yellow: '🟡 中风险', red: '🔴 高风险' }
      return map[l] || l
    },
    levelClass(l) {
      return 'level-' + l
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

.hint { font-size: 0.78rem; color: #6B6B7B; margin-bottom: 1rem; }

.q-row { margin-bottom: 1rem; padding: 0.5rem 0; border-bottom: 1px solid #151518; }
.q-text { font-size: 0.88rem; color: #E8E6E3; margin-bottom: 0.4rem; }
.q-slider { display: flex; gap: 0.8rem; }
.q-radio { display: flex; flex-direction: column; align-items: center; gap: 0.15rem; cursor: pointer; }
.q-radio span { font-size: 0.72rem; color: #6B6B7B; }
.q-radio input { accent-color: #F0B90B; }

.form-row { margin: 1rem 0; }
.form-label { display: block; font-size: 0.78rem; color: #6B6B7B; margin-bottom: 0.3rem; }
.styled-textarea {
  width: 100%; padding: 0.5rem 0.7rem; background: #0A0A0B; border: 1px solid #151518;
  border-radius: 6px; color: #E8E6E3; font-size: 0.85rem; outline: none; resize: vertical; font-family: inherit;
}
.styled-textarea:focus { border-color: #F0B90B44; }

.btn-submit {
  padding: 0.5rem 1.5rem; background: #F0B90B; color: #0A0A0B;
  border: none; border-radius: 6px; font-size: 0.88rem; cursor: pointer;
}
.btn-submit:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-reset {
  margin-top: 0.8rem; padding: 0.4rem 1.2rem; background: transparent;
  color: #F0B90B; border: 1px solid #F0B90B44; border-radius: 6px; cursor: pointer; font-size: 0.82rem;
}

.result-panel { margin-top: 1rem; }
.result-green h3 { color: #4ADE80; }
.result-yellow h3 { color: #F0B90B; }
.result-red h3 { color: #EF5350; }
.risk-desc { font-size: 0.85rem; color: #C8C6C3; margin: 0.5rem 0; }
.score-summary { display: flex; gap: 1.5rem; font-size: 0.82rem; color: #6B6B7B; }
.notes-display { font-size: 0.82rem; color: #A0A0A8; margin-top: 0.3rem; }

.history-list { display: flex; flex-direction: column; gap: 0.4rem; }
.history-item {
  display: flex; align-items: center; gap: 1rem; padding: 0.45rem 0.7rem;
  background: #0D0D10; border: 1px solid #151518; border-radius: 6px; font-size: 0.8rem;
}
.h-time { color: #6B6B7B; min-width: 140px; }
.h-notes { color: #A0A0A8; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.level-green { color: #4ADE80; }
.level-yellow { color: #F0B90B; }
.level-red { color: #EF5350; }

.empty-state { padding: 3rem; text-align: center; color: #6B6B7B; }
</style>
