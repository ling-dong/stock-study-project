<template>
  <div class="quiz-widget" v-if="questions.length">
    <div class="ia-divider"></div>
    <IASectionTitle icon="check" title="章节测验" />

    <div v-for="(q, qi) in questions" :key="q.id" class="quiz-question ia-card">
      <p class="q-title"><strong>{{ q.id }}.</strong> {{ q.question }}</p>

      <div v-if="q.type === 'single_choice'" class="q-options">
        <label
          v-for="(opt, oi) in q.options" :key="oi"
          class="q-option"
          :class="{ 'q-option--selected': userAnswers[q.id] === oi }"
        >
          <input type="radio" :name="'q_' + q.id" :value="oi" v-model="userAnswers[q.id]" :disabled="submitted" />
          <span>{{ String.fromCharCode(65 + oi) }}. {{ opt }}</span>
        </label>
      </div>

      <div v-if="q.type === 'multi_choice'" class="q-options">
        <label
          v-for="(opt, oi) in q.options" :key="oi"
          class="q-option"
          :class="{ 'q-option--selected': multiSelected(q.id, oi) }"
        >
          <input type="checkbox" :value="oi" :checked="multiSelected(q.id, oi)" @change="toggleMulti(q.id, oi)" :disabled="submitted" />
          <span>{{ String.fromCharCode(65 + oi) }}. {{ opt }}</span>
        </label>
      </div>

      <div v-if="q.type === 'true_false'" class="q-options">
        <label class="q-option" :class="{ 'q-option--selected': userAnswers[q.id] === true }">
          <input type="radio" :name="'q_' + q.id" :value="true" v-model="userAnswers[q.id]" :disabled="submitted" />
          <span>正确</span>
        </label>
        <label class="q-option" :class="{ 'q-option--selected': userAnswers[q.id] === false }">
          <input type="radio" :name="'q_' + q.id" :value="false" v-model="userAnswers[q.id]" :disabled="submitted" />
          <span>错误</span>
        </label>
      </div>
    </div>

    <IAButton v-if="!submitted" variant="primary" :loading="submitting" :disabled="!allAnswered" @click="handleSubmit">
      <IAIcon name="check" size="sm" />提交答案
    </IAButton>
    <p v-if="!allAnswered && !submitted" class="ia-hint">请完成所有题目后再提交</p>

    <div v-if="submitted && result" class="quiz-result ia-card">
      <div class="result-score" :class="result.passed ? 'result-pass' : 'result-fail'">
        <IAIcon :name="result.passed ? 'check' : 'warning'" size="lg" />
        <span>得分: {{ result.correct_count }}/{{ result.total }} ({{ (result.score * 100).toFixed(0) }}%) — {{ result.passed ? '优秀！' : '建议重新学习本章' }}</span>
      </div>

      <div class="result-detail">
        <div
          v-for="exp in result.explanations" :key="exp.question_id"
          class="result-item"
          :class="{ 'result-item--correct': exp.user_correct }"
        >
          <strong>{{ exp.question_id }}</strong>: {{ exp.explanation }}
        </div>
      </div>

      <IAButton variant="secondary" @click="resetQuiz" style="margin-top: var(--ia-space-md)">
        <IAIcon name="arrow-left" size="sm" />重新作答
      </IAButton>
    </div>
  </div>
</template>

<script>
import { IASectionTitle, IAButton, IAIcon } from './ui'
import { submitQuiz } from '../api/quiz'

export default {
  name: 'QuizWidget',
  components: { IASectionTitle, IAButton, IAIcon },
  props: {
    questions: { type: Array, default: () => [] },
    phaseId: { type: String, required: true },
    chapterId: { type: String, required: true },
  },
  data() {
    return {
      userAnswers: {},
      multiAnswers: {},
      submitted: false,
      submitting: false,
      result: null,
    }
  },
  computed: {
    allAnswered() {
      return this.questions.every(q => {
        if (q.type === 'multi_choice') {
          return (this.multiAnswers[q.id] || []).length > 0
        }
        return this.userAnswers[q.id] !== undefined && this.userAnswers[q.id] !== null
      })
    },
  },
  methods: {
    multiSelected(qId, oi) { return (this.multiAnswers[qId] || []).includes(oi) },
    toggleMulti(qId, oi) {
      const arr = this.multiAnswers[qId] || []
      const idx = arr.indexOf(oi)
      if (idx >= 0) arr.splice(idx, 1)
      else arr.push(oi)
      this.$set(this.multiAnswers, qId, [...arr])
    },
    buildAnswers() {
      const answers = {}
      this.questions.forEach(q => {
        if (q.type === 'multi_choice') answers[q.id] = this.multiAnswers[q.id] || []
        else answers[q.id] = this.userAnswers[q.id]
      })
      return answers
    },
    async handleSubmit() {
      if (!this.allAnswered || this.submitting) return
      this.submitting = true
      try {
        const res = await submitQuiz({ phase_id: this.phaseId, chapter_id: this.chapterId, answers: this.buildAnswers() })
        this.result = res.data
        this.submitted = true
        this.$emit('quiz-result', { passed: res.data.passed, score: res.data.score, chapterId: this.chapterId })
      } catch (e) { this.$toast('提交失败: ' + (e.response?.data?.detail || e.message), 'error') }
      finally { this.submitting = false }
    },
    resetQuiz() { this.userAnswers = {}; this.multiAnswers = {}; this.submitted = false; this.result = null },
  },
}
</script>

<style scoped>
.quiz-question { margin-bottom: var(--ia-space-md); padding: var(--ia-space-md); }

.q-title { margin-bottom: var(--ia-space-md); font-size: var(--ia-font-size-md); color: var(--ia-text); }

.q-options { display: flex; flex-direction: column; gap: 0.35rem; }

.q-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.85rem;
  border-radius: var(--ia-radius-xs);
  cursor: pointer;
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text-secondary);
  transition: all var(--ia-transition-fast);
  border: 1px solid var(--ia-glass-border);
  background: rgba(255, 255, 255, 0.02);
  width: 100%;
}

.q-option:hover { background: rgba(255, 255, 255, 0.04); border-color: var(--ia-border-strong); }

.q-option--selected {
  background: var(--ia-gold-soft);
  border-color: rgba(240, 185, 11, 0.3);
  color: var(--ia-gold);
  box-shadow: 0 0 12px rgba(240, 185, 11, 0.06);
}

.q-option input { accent-color: var(--ia-gold); }

.quiz-result { margin-top: var(--ia-space-md); padding: var(--ia-space-md); }

.result-score {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem;
  border-radius: var(--ia-radius-xs);
  margin-bottom: 0.8rem;
  font-size: var(--ia-font-size-md);
  backdrop-filter: blur(var(--ia-glass-blur));
  -webkit-backdrop-filter: blur(var(--ia-glass-blur));
}

.result-pass { background: var(--ia-green-soft); border: 1px solid rgba(14, 203, 129, 0.2); color: var(--ia-green); }
.result-fail { background: var(--ia-red-soft); border: 1px solid rgba(246, 70, 93, 0.2); color: var(--ia-red); }

.result-detail { display: flex; flex-direction: column; gap: 0.5rem; }

.result-item {
  padding: 0.5rem 0.8rem;
  border-radius: var(--ia-radius-xs);
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text-secondary);
  border-left: 3px solid var(--ia-red);
  background: rgba(255, 255, 255, 0.02);
}

.result-item--correct { border-left-color: var(--ia-green); }
</style>
