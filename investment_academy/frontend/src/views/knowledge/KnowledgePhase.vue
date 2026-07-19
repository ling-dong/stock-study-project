<template>
  <div class="knowledge-page ia-page">
    <IAPageHeader
      :title="phaseTitle"
      :subtitle="phaseDesc"
      :breadcrumbs="[{ label: '首页', to: '/' }, { label: '知识轨道' }, { label: phaseTitle }]"
    />

    <div v-if="loadingChapters" class="ia-loading">
      <IAIcon name="spinner" size="lg" class="ia-anim-spin" />
      <p>加载章节列表…</p>
    </div>

    <template v-else>
      <div v-if="chapters.length" class="chapter-tabs">
        <button
          v-for="ch in chapters" :key="ch.id"
          class="tab-btn"
          :class="{ 'tab-btn--active': activeChapter === ch.id, 'tab-btn--done': chapterDone(ch.id) }"
          @click="selectChapter(ch)"
        >
          {{ ch.title || ch.file }}
          <IAIcon v-if="chapterDone(ch.id)" name="check" size="xs" />
        </button>
      </div>

      <IAPanel v-if="loadingContent" loading title="加载章节中" />

      <div v-else-if="chapterContent" class="chapter-body">
        <IAPanel :title="currentChapter?.title || '章节内容'" icon="book">
          <MarkdownViewer :content="chapterContent" />
        </IAPanel>

        <QuizWidget
          v-if="quizData"
          :questions="quizData.questions"
          :phaseId="phaseId"
          :chapterId="currentChapter ? currentChapter.id : ''"
          @quiz-result="onQuizResult"
        />
      </div>

      <div v-else class="ia-empty">
        <IAIcon name="book" size="xl" class="ia-empty__icon" />
        <p>该章节内容正在编写中…</p>
      </div>
    </template>
  </div>
</template>

<script>
import { IAPageHeader, IAPanel, IAIcon } from '../../components/ui'
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
  name: 'KnowledgePhase',
  components: { IAPageHeader, IAPanel, IAIcon, MarkdownViewer, QuizWidget },
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
    phaseTitle() { return PHASE_LABELS[this.phaseId] || this.phaseId },
    phaseDesc() { return PHASE_DESCS[this.phaseId] || '' },
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
        this.chapters = res.data || []
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
    chapterDone(id) { return this.progressMap[id]?.completed },
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
    async onQuizResult() {
      await this.loadProgress()
    },
  },
}
</script>

<style scoped>
.chapter-tabs {
  display: flex;
  gap: 0.4rem;
  margin-bottom: var(--ia-space-lg);
  flex-wrap: wrap;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.5rem 0.9rem;
  background: var(--ia-surface-glass);
  border: 1px solid var(--ia-glass-border);
  border-radius: var(--ia-radius-xs);
  color: var(--ia-text-secondary);
  font-size: var(--ia-font-size-sm);
  cursor: pointer;
  transition: all var(--ia-transition-fast);
  backdrop-filter: blur(var(--ia-glass-blur));
  -webkit-backdrop-filter: blur(var(--ia-glass-blur));
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--ia-text);
  border-color: var(--ia-border-strong);
}

.tab-btn--active {
  background: var(--ia-gold-soft);
  border-color: rgba(240, 185, 11, 0.25);
  color: var(--ia-gold);
  box-shadow: 0 0 12px rgba(240, 185, 11, 0.06);
}

.tab-btn--done {
  border-color: rgba(14, 203, 129, 0.25);
}

.tab-btn--done svg {
  color: var(--ia-green);
}

.chapter-body {
  display: flex;
  flex-direction: column;
  gap: var(--ia-space-md);
}

@media (max-width: 640px) {
  .chapter-tabs { overflow-x: auto; flex-wrap: nowrap; }
  .tab-btn { white-space: nowrap; }
}
</style>
