<template>
  <div class="quiz-widget" v-if="questions.length">
    <div class="divider"></div>
    <h2>📝 章节测验</h2>

    <div v-for="(q, qi) in questions" :key="q.id" class="quiz-question">
      <p class="q-title"><strong>{{ q.id }}.</strong> {{ q.question }}</p>

      <!-- 单选题 -->
      <div v-if="q.type === 'single_choice'" class="q-options">
        <label
          v-for="(opt, oi) in q.options" :key="oi"
          class="q-option"
          :class="{ 'q-option--selected': userAnswers[q.id] === oi }"
        >
          <input
            type="radio"
            :name="'q_' + q.id"
            :value="oi"
            v-model="userAnswers[q.id]"
            :disabled="submitted"
          />
          <span>{{ String.fromCharCode(65 + oi) }}. {{ opt }}</span>
        </label>
      </div>

      <!-- 多选题 -->
      <div v-if="q.type === 'multi_choice'" class="q-options">
        <label
          v-for="(opt, oi) in q.options" :key="oi"
          class="q-option"
          :class="{ 'q-option--selected': multiSelected(q.id, oi) }"
        >
          <input
            type="checkbox"
            :value="oi"
            :checked="multiSelected(q.id, oi)"
            @change="toggleMulti(q.id, oi)"
            :disabled="submitted"
          />
          <span>{{ String.fromCharCode(65 + oi) }}. {{ opt }}</span>
        </label>
      </div>

      <!-- 判断题 -->
      <div v-if="q.type === 'true_false'" class="q-options">
        <label
          class="q-option"
          :class="{ 'q-option--selected': userAnswers[q.id] === true }"
        >
          <input
            type="radio"
            :name="'q_' + q.id"
            :value="true"
            v-model="userAnswers[q.id]"
            :disabled="submitted"
          />
          <span>✅ 正确</span>
        </label>
        <label
          class="q-option"
          :class="{ 'q-option--selected': userAnswers[q.id] === false }"
        >
          <input
            type="radio"
            :name="'q_' + q.id"
            :value="false"
            v-model="userAnswers[q.id]"
            :disabled="submitted"
          />
          <span>❌ 错误</span>
        </label>
      </div>
    </div>

    <!-- 提交按钮 -->
    <button
      v-if="!submitted"
      class="btn-submit"
      @click="handleSubmit"
      :disabled="!allAnswered || submitting"
    >
      {{ submitting ? '提交中…' : '提交答案' }}
    </button>
    <p v-if="!allAnswered && !submitted" class="q-hint">
      请完成所有题目后再提交
    </p>

    <!-- 结果面板 -->
    <div v-if="submitted && result" class="quiz-result">
      <div class="result-score" :class="result.passed ? 'result-pass' : 'result-fail'">
        <span class="result-icon">{{ result.passed ? '🎉' : '📖' }}</span>
        <span class="result-text">
          得分: {{ result.correct_count }}/{{ result.total }} ({{ (result.score * 100).toFixed(0) }}%)
          — {{ result.passed ? '优秀！' : '建议重新学习本章' }}
        </span>
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

      <button class="btn-retry" @click="resetQuiz">重新作答</button>
    </div>
  </div>
</template>

<script>
import { submitQuiz } from '../api/quiz'

export default {
  name: 'QuizWidget',
  props: {
    questions: { type: Array, default: () => [] },
    phaseId: { type: String, required: true },
    chapterId: { type: String, required: true },
  },
  data() {
    return {
      userAnswers: {},
      multiAnswers: {},      // {q_id: Set[oi]}
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
    multiSelected(qId, oi) {
      return (this.multiAnswers[qId] || []).includes(oi)
    },
    toggleMulti(qId, oi) {
      const arr = this.multiAnswers[qId] || []
      const idx = arr.indexOf(oi)
      if (idx >= 0) {
        arr.splice(idx, 1)
      } else {
        arr.push(oi)
      }
      this.$set(this.multiAnswers, qId, [...arr])
    },
    buildAnswers() {
      const answers = {}
      this.questions.forEach(q => {
        if (q.type === 'multi_choice') {
          answers[q.id] = this.multiAnswers[q.id] || []
        } else {
          answers[q.id] = this.userAnswers[q.id]
        }
      })
      return answers
    },
    async handleSubmit() {
      if (!this.allAnswered || this.submitting) return
      this.submitting = true
      try {
        const res = await submitQuiz({
          phase_id: this.phaseId,
          chapter_id: this.chapterId,
          answers: this.buildAnswers(),
        })
        this.result = res.data
        this.submitted = true
        this.$emit('quiz-result', {
          passed: res.data.passed,
          score: res.data.score,
          chapterId: this.chapterId,
        })
      } catch (e) {
        alert('提交失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        this.submitting = false
      }
    },
    resetQuiz() {
      this.userAnswers = {}
      this.multiAnswers = {}
      this.submitted = false
      this.result = null
    },
  },
}
</script>

<style scoped>
.quiz-question {
  margin-bottom: 1.2rem;
  padding: 1rem;
  background: #0D0D10;
  border: 1px solid #151518;
  border-radius: 8px;
}

.q-title {
  margin-bottom: 0.6rem;
  font-size: 0.95rem;
}

.q-options {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.q-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.88rem;
  color: #C8C6C3;
  transition: background 0.15s;
}

.q-option:hover {
  background: #141417;
}

.q-option--selected {
  background: #F0B90B12;
  border: 1px solid #F0B90B33;
}

.q-option input {
  accent-color: #F0B90B;
}

.btn-submit {
  margin-top: 1rem;
  padding: 0.6rem 2rem;
  background: #F0B90B;
  color: #0A0A0B;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-submit:hover {
  opacity: 0.9;
}

.btn-submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.q-hint {
  font-size: 0.78rem;
  color: #6B6B7B;
  margin-top: 0.5rem;
}

.quiz-result {
  margin-top: 1rem;
  padding: 1.2rem;
  background: #0D0D10;
  border: 1px solid #151518;
  border-radius: 8px;
}

.result-score {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem;
  border-radius: 6px;
  margin-bottom: 0.8rem;
  font-size: 0.95rem;
}

.result-pass {
  background: #0A2E0A;
  border: 1px solid #166534;
  color: #4ADE80;
}

.result-fail {
  background: #2E0A0A;
  border: 1px solid #7F1D1D;
  color: #FCA5A5;
}

.result-icon {
  font-size: 1.2rem;
}

.result-detail {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.result-item {
  padding: 0.5rem 0.8rem;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #A0A0A8;
  border-left: 3px solid #7F1D1D;
}

.result-item--correct {
  border-left-color: #4ADE80;
}

.btn-retry {
  margin-top: 0.8rem;
  padding: 0.4rem 1.2rem;
  background: transparent;
  color: #F0B90B;
  border: 1px solid #F0B90B44;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.82rem;
  transition: background 0.2s;
}

.btn-retry:hover {
  background: #F0B90B12;
}
</style>
