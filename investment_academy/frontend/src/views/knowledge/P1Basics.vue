<template>
  <div class="knowledge-page">
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <router-link to="/">首页</router-link>
      <span> / </span>
      <span>P1 股市基础</span>
      <span v-if="currentChapter"> / </span>
      <span v-if="currentChapter"><strong>{{ currentChapter.title }}</strong></span>
    </div>

    <h1>📚 {{ phaseTitle }}</h1>
    <p class="phase-desc">{{ phaseDesc }}</p>

    <!-- 章节导航 Tab -->
    <div class="chapter-tabs">
      <button
        v-for="ch in chapters" :key="ch.id"
        class="tab-btn"
        :class="{
          'tab-btn--active': activeChapter === ch.id,
          'tab-btn--done': chapterDone(ch.id),
        }"
        @click="selectChapter(ch)"
      >
        {{ ch.title || ch.file }}
        <span v-if="chapterDone(ch.id)" class="tab-check">✓</span>
      </button>
    </div>

    <!-- 加载中 -->
    <div v-if="loadingChapters" class="loading">加载章节列表…</div>

    <div v-else-if="loadingContent" class="loading">加载中…</div>

    <!-- 章节内容 -->
    <div v-else-if="chapterContent" class="chapter-body">
      <MarkdownViewer :content="chapterContent" />

      <!-- 测验 -->
      <QuizWidget
        v-if="quizData"
        :questions="quizData.questions"
        :phaseId="phaseId"
        :chapterId="currentChapter ? currentChapter.id : ''"
        @quiz-result="onQuizResult"
      />
    </div>

    <!-- 无内容 -->
    <div v-else class="empty-state">
      <p>📝 该章节内容正在编写中…</p>
    </div>
  </div>
</template>

<script>
import { getChapter, getQuiz, getChapters } from '../../api/content'
import { getProgress } from '../../api/progress'
import MarkdownViewer from '../../components/MarkdownViewer.vue'
import QuizWidget from '../../components/QuizWidget.vue'

const PHASE_LABELS = {
  p1_basics: 'P1: 股市基础', p2_technical: 'P2: 技术分析入门',
  p3_sectors: 'P3: 板块与产业链', p4_quant: 'P4: 量化策略思维',
  p5_risk: 'P5: 风险管理', p6_psychology: 'P6: 交易心理与市场情绪',
  p7_integration: 'P7: 实战整合',
}
const PHASE_DESCS = {
  p1_basics: '从零开始，理解股票市场的基本概念',
  p2_technical: '掌握K线微观结构、均线系统与Wyckoff理论',
  p3_sectors: '理解行业分类、产业链传导与板块轮动规律',
  p4_quant: '建立概率思维，学习量化策略设计与ML应用',
  p5_risk: '仓位管理、回撤控制与尾部风险应对',
  p6_psychology: '交易者自我认知、情绪管理与纪律规则',
  p7_integration: 'Walk-Forward回测、前视偏差与完整交易系统',
}

export default {
  name: 'P1Basics',
  components: { MarkdownViewer, QuizWidget },
  created() {
    this.PHASE_LABELS = PHASE_LABELS
    this.PHASE_DESCS = PHASE_DESCS
  },
  props: {
    phaseId: { type: String, default: 'p1_basics' },
  },
  data() {
    return {
      chapters: [],
      activeChapter: '',
      currentChapter: null,
      chapterContent: null,
      quizData: null,
      loadingContent: false,
      loadingChapters: true,
      progressMap: {},
    }
  },
  computed: {
    phaseTitle() {
      return this.PHASE_LABELS[this.phaseId] || this.phaseId
    },
    phaseDesc() {
      return this.PHASE_DESCS[this.phaseId] || ''
    },
  },
  watch: {
    phaseId: {
      immediate: true,
      handler() { this.initPhase() },
    },
  },
  methods: {
    async initPhase() {
      this.chapters = []
      this.currentChapter = null
      this.chapterContent = null
      this.quizData = null
      this.loadingChapters = true
      await this.loadProgress()
      try {
        const res = await getChapters(this.phaseId)
        const rawChapters = res.data || []
        this.chapters = rawChapters
        if (this.chapters.length) {
          this.currentChapter = this.chapters[0]
          this.activeChapter = this.chapters[0].id
          this.selectChapter(this.chapters[0])
        }
      } catch (e) {
        console.error('加载章节列表失败:', e)
      } finally {
        this.loadingChapters = false
      }
    },
    chapterDone(id) {
      return this.progressMap[id]?.completed
    },
    async loadProgress() {
      try {
        const res = await getProgress()
        const map = {}
        ;(res.data || []).forEach(p => { map[p.chapter_id] = p })
        this.progressMap = map
      } catch (e) {
        console.error('加载进度失败:', e)
      }
    },
    async selectChapter(ch) {
      this.activeChapter = ch.id
      this.currentChapter = ch
      this.chapterContent = null
      this.quizData = null
      this.loadingContent = true

      try {
        // 加载章节内容和测验
        const [contentRes, quizRes] = await Promise.allSettled([
          getChapter(this.phaseId, ch.file),
          getQuiz(this.phaseId, ch.id),
        ])

        if (contentRes.status === 'fulfilled') {
          this.chapterContent = contentRes.value.data.content
        }
        if (quizRes.status === 'fulfilled' && quizRes.value.data) {
          this.quizData = quizRes.value.data
        }
      } catch (e) {
        console.error('加载章节失败:', e)
      } finally {
        this.loadingContent = false
      }
    },
    async onQuizResult({ passed, score }) {
      // 测验完成后刷新进度
      await this.loadProgress()
      // 如果通过，显示完成标记
      if (passed && this.currentChapter) {
        this.$forceUpdate()
      }
    },
  },
}
</script>

<style scoped>
.phase-desc {
  font-size: 0.9rem;
  color: #6B6B7B;
  margin-bottom: 1.5rem;
}

.breadcrumb {
  font-size: 0.78rem;
  color: #6B6B7B;
  margin-bottom: 1.2rem;
  letter-spacing: 0.05em;
}

.breadcrumb span {
  color: #F0B90B;
}

.breadcrumb a {
  color: #6B6B7B;
  text-decoration: none;
}

.breadcrumb strong {
  color: #F5F0E0;
}

.chapter-tabs {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 1.8rem;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 0.4rem 0.9rem;
  background: #0D0D10;
  border: 1px solid #151518;
  border-radius: 6px;
  color: #A0A0A8;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.tab-btn:hover {
  background: #141417;
  color: #E8E6E3;
}

.tab-btn--active {
  background: #F0B90B15;
  border-color: #F0B90B44;
  color: #F0B90B;
}

.tab-btn--done {
  border-color: #16653455;
}

.tab-check {
  font-size: 0.7rem;
  color: #4ADE80;
}

.loading {
  padding: 3rem;
  text-align: center;
  color: #6B6B7B;
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #6B6B7B;
}
</style>
