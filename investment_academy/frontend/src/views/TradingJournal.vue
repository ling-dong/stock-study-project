<template>
  <div class="journal-page">
    <div class="breadcrumb">
      <router-link to="/">首页</router-link>
      <span> / </span>
      <span><strong>交易日志</strong></span>
    </div>

    <h1>📓 交易日志</h1>
    <p class="page-desc">记录每笔交易，持续复盘改进</p>

    <!-- 新增日志 -->
    <div class="card">
      <h3>✍️ 记录新交易</h3>
      <div class="form-grid">
        <div class="form-group">
          <label>日期</label>
          <input v-model="form.date" type="date" class="styled-input" />
        </div>
        <div class="form-group">
          <label>Setup 类型</label>
          <select v-model="form.setup_type" class="styled-select">
            <option value="">-- 选择 --</option>
            <option v-for="s in SETUP_TYPES" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>盈亏 %</label>
          <input v-model.number="form.pnl_pct" type="number" step="0.01" class="styled-input" placeholder="如 2.35" />
        </div>
        <div class="form-group">
          <label>交易时情绪</label>
          <select v-model="form.emotional_state" class="styled-select">
            <option value="">-- 选择 --</option>
            <option v-for="s in EMOTIONS" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>入场理由</label>
        <textarea v-model="form.entry_reason" class="styled-textarea" rows="2" placeholder="为什么入场？技术信号、基本面、还是直觉？"></textarea>
      </div>
      <div class="form-group">
        <label>出场理由</label>
        <textarea v-model="form.exit_reason" class="styled-textarea" rows="2" placeholder="为什么出场？止损触发、止盈到达、还是临时决定？"></textarea>
      </div>
      <div class="form-group">
        <label>经验教训</label>
        <textarea v-model="form.lesson_learned" class="styled-textarea" rows="2" placeholder="从这笔交易中学到了什么？"></textarea>
      </div>

      <div class="form-bottom">
        <label class="checkbox-label">
          <input type="checkbox" v-model="form.mistake_flag" />
          <span>标记为错误交易 ⚠️</span>
        </label>
        <button class="btn-submit" @click="saveEntry" :disabled="saving">
          {{ saving ? '保存中…' : '保存日志' }}
        </button>
      </div>
    </div>

    <!-- 日志列表 -->
    <div class="divider"></div>
    <h2>📜 历史日志 ({{ journalEntries.length }})</h2>

    <!-- 统计摘要 -->
    <div class="summary-bar" v-if="journalEntries.length">
      <span>总交易 {{ journalEntries.length }} 笔</span>
      <span class="sep">|</span>
      <span class="green">盈利 {{ winCount }} 笔</span>
      <span class="sep">|</span>
      <span class="red">亏损 {{ loseCount }} 笔</span>
      <span class="sep">|</span>
      <span>胜率 {{ winRate }}%</span>
      <span class="sep">|</span>
      <span>错误 {{ mistakeCount }} 笔</span>
      <span class="sep">|</span>
      <span :class="totalPnl >= 0 ? 'green' : 'red'">
        累计 {{ totalPnl >= 0 ? '+' : '' }}{{ totalPnl.toFixed(2) }}%
      </span>
    </div>

    <div v-if="journalEntries.length" class="journal-list">
      <div
        v-for="entry in journalEntries" :key="entry.id"
        class="journal-item card"
        :class="{ 'journal-mistake': entry.mistake_flag }"
      >
        <div class="ji-header">
          <span class="ji-date">{{ entry.date?.substring(0, 10) }}</span>
          <span class="ji-setup">{{ entry.setup_type || '未指定' }}</span>
          <span class="ji-pnl" :class="entry.pnl_pct >= 0 ? 'green' : 'red'">
            {{ entry.pnl_pct >= 0 ? '+' : '' }}{{ entry.pnl_pct }}%
          </span>
          <span class="ji-emotion" v-if="entry.emotional_state">{{ entry.emotional_state }}</span>
          <span class="ji-mistake" v-if="entry.mistake_flag">⚠️ 错误交易</span>
          <div class="ji-actions">
            <button class="btn-edit-sm" @click="editEntry(entry)">✏️</button>
            <button class="btn-del-sm" @click="deleteEntry(entry.id)">🗑️</button>
          </div>
        </div>
        <div class="ji-body">
          <div v-if="entry.entry_reason" class="ji-field">
            <span class="ji-field-label">入场:</span> {{ entry.entry_reason }}
          </div>
          <div v-if="entry.exit_reason" class="ji-field">
            <span class="ji-field-label">出场:</span> {{ entry.exit_reason }}
          </div>
          <div v-if="entry.lesson_learned" class="ji-field">
            <span class="ji-field-label">教训:</span> {{ entry.lesson_learned }}
          </div>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">暂无交易日志，开始记录吧</div>

    <!-- 编辑弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal card">
        <h3>✏️ 编辑交易日志</h3>
        <div class="form-grid">
          <div class="form-group">
            <label>日期</label>
            <input v-model="editForm.date" type="date" class="styled-input" />
          </div>
          <div class="form-group">
            <label>Setup 类型</label>
            <select v-model="editForm.setup_type" class="styled-select">
              <option value="">-- 选择 --</option>
              <option v-for="s in SETUP_TYPES" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>盈亏 %</label>
            <input v-model.number="editForm.pnl_pct" type="number" step="0.01" class="styled-input" />
          </div>
          <div class="form-group">
            <label>交易时情绪</label>
            <select v-model="editForm.emotional_state" class="styled-select">
              <option value="">-- 选择 --</option>
              <option v-for="s in EMOTIONS" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>入场理由</label>
          <textarea v-model="editForm.entry_reason" class="styled-textarea" rows="2"></textarea>
        </div>
        <div class="form-group">
          <label>出场理由</label>
          <textarea v-model="editForm.exit_reason" class="styled-textarea" rows="2"></textarea>
        </div>
        <div class="form-group">
          <label>经验教训</label>
          <textarea v-model="editForm.lesson_learned" class="styled-textarea" rows="2"></textarea>
        </div>
        <div class="form-bottom">
          <label class="checkbox-label">
            <input type="checkbox" v-model="editForm.mistake_flag" />
            <span>标记为错误交易 ⚠️</span>
          </label>
        </div>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showEditModal = false">取消</button>
          <button class="btn-submit" @click="saveEdit" :disabled="saving">
            {{ saving ? '保存中…' : '保存修改' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { addJournalEntry, getJournal, updateJournalEntry, deleteJournalEntry } from '../api/user'

const SETUP_TYPES = ['H2', 'L2', 'FB', '趋势跟随', '突破', '回调', '反转', '其他']
const EMOTIONS = ['冷静', '自信', '焦虑', '兴奋', '恐惧', '贪婪', '后悔', '愤怒', '犹豫']

export default {
  name: 'TradingJournal',
  data() {
    return {
      SETUP_TYPES,
      EMOTIONS,
      form: {
        date: new Date().toISOString().substring(0, 10),
        setup_type: '',
        entry_reason: '',
        exit_reason: '',
        pnl_pct: 0,
        emotional_state: '',
        lesson_learned: '',
        mistake_flag: false,
      },
      journalEntries: [],
      saving: false,
      showEditModal: false,
      editingId: null,
      editForm: {
        date: '', setup_type: '', entry_reason: '', exit_reason: '',
        pnl_pct: 0, emotional_state: '', lesson_learned: '', mistake_flag: false,
      },
    }
  },
  computed: {
    winCount() { return this.journalEntries.filter(j => j.pnl_pct > 0).length },
    loseCount() { return this.journalEntries.filter(j => j.pnl_pct < 0).length },
    mistakeCount() { return this.journalEntries.filter(j => j.mistake_flag).length },
    totalPnl() { return this.journalEntries.reduce((s, j) => s + (j.pnl_pct || 0), 0) },
    winRate() {
      const total = this.winCount + this.loseCount
      return total > 0 ? ((this.winCount / total) * 100).toFixed(0) : 0
    },
  },
  async created() {
    await this.loadJournal()
  },
  methods: {
    async saveEntry() {
      this.saving = true
      try {
        await addJournalEntry(this.form)
        // Reset form
        this.form = {
          date: new Date().toISOString().substring(0, 10),
          setup_type: '',
          entry_reason: '',
          exit_reason: '',
          pnl_pct: 0,
          emotional_state: '',
          lesson_learned: '',
          mistake_flag: false,
        }
        await this.loadJournal()
      } catch (e) {
        alert('保存失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        this.saving = false
      }
    },
    async loadJournal() {
      try {
        const res = await getJournal()
        this.journalEntries = res.data || []
      } catch (e) {
        console.error('加载日志失败:', e)
      }
    },
    editEntry(entry) {
      this.editingId = entry.id
      this.editForm = {
        date: entry.date?.substring(0, 10) || '',
        setup_type: entry.setup_type || '',
        entry_reason: entry.entry_reason || '',
        exit_reason: entry.exit_reason || '',
        pnl_pct: entry.pnl_pct || 0,
        emotional_state: entry.emotional_state || '',
        lesson_learned: entry.lesson_learned || '',
        mistake_flag: !!entry.mistake_flag,
      }
      this.showEditModal = true
    },
    async saveEdit() {
      if (!this.editingId) return
      this.saving = true
      try {
        await updateJournalEntry(this.editingId, this.editForm)
        this.showEditModal = false
        this.editingId = null
        await this.loadJournal()
      } catch (e) {
        alert('保存失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        this.saving = false
      }
    },
    async deleteEntry(id) {
      if (!confirm('确定删除这条交易日志吗？此操作不可撤销。')) return
      try {
        await deleteJournalEntry(id)
        await this.loadJournal()
      } catch (e) {
        alert('删除失败: ' + (e.response?.data?.detail || e.message))
      }
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

.form-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.8rem; margin-bottom: 0.8rem; }
.form-group { display: flex; flex-direction: column; gap: 0.3rem; margin-bottom: 0.8rem; }
.form-group label { font-size: 0.72rem; color: #6B6B7B; letter-spacing: 0.05em; }

.styled-input, .styled-select {
  padding: 0.45rem 0.7rem; background: #0A0A0B; border: 1px solid #151518;
  border-radius: 6px; color: #E8E6E3; font-size: 0.85rem; outline: none; font-family: inherit;
}
.styled-input:focus, .styled-select:focus { border-color: #F0B90B44; }

.styled-textarea {
  width: 100%; padding: 0.5rem 0.7rem; background: #0A0A0B; border: 1px solid #151518;
  border-radius: 6px; color: #E8E6E3; font-size: 0.85rem; outline: none; resize: vertical; font-family: inherit;
}
.styled-textarea:focus { border-color: #F0B90B44; }

.form-bottom { display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; }
.checkbox-label { display: flex; align-items: center; gap: 0.4rem; font-size: 0.85rem; color: #E8E6E3; cursor: pointer; }
.checkbox-label input { accent-color: #F0B90B; }

.btn-submit {
  padding: 0.5rem 1.5rem; background: #F0B90B; color: #0A0A0B;
  border: none; border-radius: 6px; font-size: 0.88rem; cursor: pointer;
}
.btn-submit:disabled { opacity: 0.4; cursor: not-allowed; }

.summary-bar {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.6rem 0.8rem; background: #0D0D10; border: 1px solid #151518;
  border-radius: 8px; font-size: 0.78rem; color: #A0A0A8; margin-bottom: 1rem; flex-wrap: wrap;
}
.sep { color: #2A2A2D; }

.journal-mistake { border-color: #7F1D1D44; }
.ji-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.5rem; flex-wrap: wrap; }
.ji-date { font-size: 0.8rem; color: #6B6B7B; }
.ji-setup { font-size: 0.8rem; color: #F0B90B; }
.ji-pnl { font-size: 0.9rem; font-weight: 500; }
.ji-emotion { font-size: 0.75rem; color: #A0A0A8; }
.ji-mistake { font-size: 0.75rem; color: #EF5350; }

.ji-body { margin-top: 0.4rem; }
.ji-field { font-size: 0.82rem; color: #C8C6C3; margin-bottom: 0.3rem; }
.ji-field-label { color: #6B6B7B; font-size: 0.75rem; }

.green { color: #4ADE80 !important; }
.red { color: #EF5350 !important; }

.ji-actions { display: flex; gap: 0.3rem; margin-left: auto; }
.btn-edit-sm, .btn-del-sm {
  background: transparent; border: 1px solid #2A2A2D; border-radius: 4px;
  padding: 0.2rem 0.4rem; cursor: pointer; font-size: 0.75rem; transition: background 0.2s;
}
.btn-edit-sm:hover { background: #F0B90B22; border-color: #F0B90B44; }
.btn-del-sm:hover { background: #EF535022; border-color: #EF535044; }

.modal-overlay { position: fixed; inset: 0; background: #00000088; display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { max-width: 520px; width: 90%; max-height: 90vh; overflow-y: auto; }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem; }
.btn-cancel { padding: 0.45rem 1rem; background: #1A1A1D; color: #A0A0A8; border: none; border-radius: 6px; font-size: 0.85rem; cursor: pointer; }
.btn-submit { padding: 0.45rem 1.5rem; background: #F0B90B; color: #0A0A0B; border: none; border-radius: 6px; font-size: 0.85rem; cursor: pointer; }
.btn-submit:disabled { opacity: 0.4; cursor: not-allowed; }

.empty-state { padding: 3rem; text-align: center; color: #6B6B7B; }
</style>
