<template>
  <div class="journal-page ia-page">
    <IAPageHeader
      title="交易日志"
      subtitle="记录每笔交易，持续复盘改进"
      :breadcrumbs="[{ label: '首页', to: '/' }, { label: '交易日志' }]"
    />

    <IAPanel title="记录新交易" icon="journal">
      <div class="ia-form-grid">
        <div class="ia-form-group">
          <label class="ia-label">日期</label>
          <input v-model="form.date" type="date" class="ia-input" />
        </div>
        <div class="ia-form-group">
          <label class="ia-label">Setup 类型</label>
          <select v-model="form.setup_type" class="ia-select">
            <option value="">-- 选择 --</option>
            <option v-for="s in SETUP_TYPES" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <div class="ia-form-group">
          <label class="ia-label">盈亏 %</label>
          <input v-model.number="form.pnl_pct" type="number" step="0.01" class="ia-input" placeholder="如 2.35" />
        </div>
        <div class="ia-form-group">
          <label class="ia-label">交易时情绪</label>
          <select v-model="form.emotional_state" class="ia-select">
            <option value="">-- 选择 --</option>
            <option v-for="s in EMOTIONS" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>

      <div class="ia-form-group">
        <label class="ia-label">入场理由</label>
        <textarea v-model="form.entry_reason" class="ia-textarea" rows="2" placeholder="为什么入场？技术信号、基本面、还是直觉？"></textarea>
      </div>
      <div class="ia-form-group">
        <label class="ia-label">出场理由</label>
        <textarea v-model="form.exit_reason" class="ia-textarea" rows="2" placeholder="为什么出场？止损触发、止盈到达、还是临时决定？"></textarea>
      </div>
      <div class="ia-form-group">
        <label class="ia-label">经验教训</label>
        <textarea v-model="form.lesson_learned" class="ia-textarea" rows="2" placeholder="从这笔交易中学到了什么？"></textarea>
      </div>

      <div class="form-bottom">
        <label class="ia-checkbox">
          <input type="checkbox" v-model="form.mistake_flag" />
          <span>标记为错误交易</span>
        </label>
        <IAButton variant="primary" :loading="saving" @click="saveEntry">
          <IAIcon name="journal" size="sm" />保存日志
        </IAButton>
      </div>
    </IAPanel>

    <div class="ia-divider"></div>

    <IASectionTitle icon="clock" :title="`历史日志 (${journalEntries.length})`" />

    <div v-if="journalEntries.length" class="ia-card summary-bar">
      <span>总交易 {{ journalEntries.length }} 笔</span>
      <span class="sep">|</span>
      <span class="ia-text-green">盈利 {{ winCount }} 笔</span>
      <span class="sep">|</span>
      <span class="ia-text-red">亏损 {{ loseCount }} 笔</span>
      <span class="sep">|</span>
      <span>胜率 {{ winRate }}%</span>
      <span class="sep">|</span>
      <span>错误 {{ mistakeCount }} 笔</span>
      <span class="sep">|</span>
      <span :class="totalPnl >= 0 ? 'ia-text-green' : 'ia-text-red'">
        累计 {{ totalPnl >= 0 ? '+' : '' }}{{ totalPnl.toFixed(2) }}%
      </span>
    </div>

    <div v-if="journalEntries.length" class="journal-list">
      <div
        v-for="entry in journalEntries" :key="entry.id"
        class="journal-item ia-card"
        :class="{ 'journal-mistake': entry.mistake_flag }"
      >
        <div class="ji-header">
          <span class="ji-date">{{ entry.date?.substring(0, 10) }}</span>
          <IABadge variant="gold">{{ entry.setup_type || '未指定' }}</IABadge>
          <span class="ji-pnl" :class="entry.pnl_pct >= 0 ? 'ia-text-green' : 'ia-text-red'">
            {{ entry.pnl_pct >= 0 ? '+' : '' }}{{ entry.pnl_pct }}%
          </span>
          <IABadge variant="neutral" v-if="entry.emotional_state">{{ entry.emotional_state }}</IABadge>
          <IABadge variant="red" v-if="entry.mistake_flag">错误交易</IABadge>
          <div class="ji-actions">
            <button class="btn-icon" @click="editEntry(entry)"><IAIcon name="edit" size="sm" /></button>
            <button class="btn-icon btn-icon--danger" @click="deleteEntry(entry.id)"><IAIcon name="trash" size="sm" /></button>
          </div>
        </div>
        <div class="ji-body">
          <div v-if="entry.entry_reason" class="ji-field"><span class="ji-field-label">入场:</span> {{ entry.entry_reason }}</div>
          <div v-if="entry.exit_reason" class="ji-field"><span class="ji-field-label">出场:</span> {{ entry.exit_reason }}</div>
          <div v-if="entry.lesson_learned" class="ji-field"><span class="ji-field-label">教训:</span> {{ entry.lesson_learned }}</div>
        </div>
      </div>
    </div>
    <div v-else class="ia-empty">暂无交易日志，开始记录吧</div>

    <!-- 编辑弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal ia-card">
        <h3>编辑交易日志</h3>
        <div class="ia-form-grid">
          <div class="ia-form-group"><label class="ia-label">日期</label><input v-model="editForm.date" type="date" class="ia-input" /></div>
          <div class="ia-form-group">
            <label class="ia-label">Setup 类型</label>
            <select v-model="editForm.setup_type" class="ia-select">
              <option value="">-- 选择 --</option><option v-for="s in SETUP_TYPES" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div class="ia-form-group"><label class="ia-label">盈亏 %</label><input v-model.number="editForm.pnl_pct" type="number" step="0.01" class="ia-input" /></div>
          <div class="ia-form-group">
            <label class="ia-label">交易时情绪</label>
            <select v-model="editForm.emotional_state" class="ia-select">
              <option value="">-- 选择 --</option><option v-for="s in EMOTIONS" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
        </div>
        <div class="ia-form-group"><label class="ia-label">入场理由</label><textarea v-model="editForm.entry_reason" class="ia-textarea" rows="2"></textarea></div>
        <div class="ia-form-group"><label class="ia-label">出场理由</label><textarea v-model="editForm.exit_reason" class="ia-textarea" rows="2"></textarea></div>
        <div class="ia-form-group"><label class="ia-label">经验教训</label><textarea v-model="editForm.lesson_learned" class="ia-textarea" rows="2"></textarea></div>
        <div class="form-bottom">
          <label class="ia-checkbox">
            <input type="checkbox" v-model="editForm.mistake_flag" />
            <span>标记为错误交易</span>
          </label>
        </div>
        <div class="modal-actions">
          <IAButton variant="ghost" @click="showEditModal = false">取消</IAButton>
          <IAButton variant="primary" :loading="saving" @click="saveEdit">保存修改</IAButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { IAPageHeader, IASectionTitle, IAPanel, IAButton, IABadge, IAIcon } from '../components/ui'
import { addJournalEntry, getJournal, updateJournalEntry, deleteJournalEntry } from '../api/user'

const SETUP_TYPES = ['H2', 'L2', 'FB', '趋势跟随', '突破', '回调', '反转', '其他']
const EMOTIONS = ['冷静', '自信', '焦虑', '兴奋', '恐惧', '贪婪', '后悔', '愤怒', '犹豫']

export default {
  name: 'TradingJournal',
  components: { IAPageHeader, IASectionTitle, IAPanel, IAButton, IABadge, IAIcon },
  data() {
    return {
      SETUP_TYPES, EMOTIONS,
      form: {
        date: new Date().toISOString().substring(0, 10),
        setup_type: '', entry_reason: '', exit_reason: '', pnl_pct: 0,
        emotional_state: '', lesson_learned: '', mistake_flag: false,
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
  async created() { await this.loadJournal() },
  methods: {
    async saveEntry() {
      this.saving = true
      try {
        await addJournalEntry(this.form)
        this.form = {
          date: new Date().toISOString().substring(0, 10),
          setup_type: '', entry_reason: '', exit_reason: '', pnl_pct: 0,
          emotional_state: '', lesson_learned: '', mistake_flag: false,
        }
        await this.loadJournal()
      } catch (e) { alert('保存失败: ' + (e.response?.data?.detail || e.message)) }
      finally { this.saving = false }
    },
    async loadJournal() {
      try {
        const res = await getJournal()
        this.journalEntries = res.data || []
      } catch (e) { console.error('加载日志失败:', e) }
    },
    editEntry(entry) {
      this.editingId = entry.id
      this.editForm = {
        date: entry.date?.substring(0, 10) || '', setup_type: entry.setup_type || '',
        entry_reason: entry.entry_reason || '', exit_reason: entry.exit_reason || '',
        pnl_pct: entry.pnl_pct || 0, emotional_state: entry.emotional_state || '',
        lesson_learned: entry.lesson_learned || '', mistake_flag: !!entry.mistake_flag,
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
      } catch (e) { alert('保存失败: ' + (e.response?.data?.detail || e.message)) }
      finally { this.saving = false }
    },
    async deleteEntry(id) {
      if (!confirm('确定删除这条交易日志吗？此操作不可撤销。')) return
      try { await deleteJournalEntry(id); await this.loadJournal() } catch (e) { alert('删除失败: ' + (e.response?.data?.detail || e.message)) }
    },
  },
}
</script>

<style scoped>
.form-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--ia-space-md);
  flex-wrap: wrap;
  gap: var(--ia-space-sm);
}

.summary-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem 1rem;
  margin-bottom: var(--ia-space-md);
  font-size: var(--ia-font-size-sm);
  color: var(--ia-text-secondary);
  flex-wrap: wrap;
}

.summary-bar .sep { color: var(--ia-border-strong); }

.journal-mistake { border-color: rgba(246, 70, 93, 0.25); }
.journal-item { padding: var(--ia-space-md); margin-bottom: var(--ia-space-sm); }
.ji-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.5rem; flex-wrap: wrap; }
.ji-date { font-size: var(--ia-font-size-sm); color: var(--ia-text-tertiary); }
.ji-pnl { font-size: var(--ia-font-size-md); font-weight: 500; font-variant-numeric: tabular-nums; }
.ji-body { margin-top: 0.4rem; }
.ji-field { font-size: var(--ia-font-size-sm); color: var(--ia-text-secondary); margin-bottom: 0.3rem; }
.ji-field-label { color: var(--ia-text-tertiary); font-size: var(--ia-font-size-xs); margin-right: 0.3rem; }
.ji-actions { display: flex; gap: 0.3rem; margin-left: auto; }
.btn-icon {
  background: transparent;
  border: 1px solid var(--ia-border);
  border-radius: 4px;
  padding: 0.25rem;
  cursor: pointer;
  color: var(--ia-text-secondary);
  transition: all 0.2s;
  display: flex;
  align-items: center;
}
.btn-icon:hover { background: var(--ia-gold-soft); border-color: var(--ia-gold); color: var(--ia-gold); }
.btn-icon--danger:hover { background: var(--ia-red-soft); border-color: var(--ia-red); color: var(--ia-red); }

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.modal { max-width: 520px; width: 90%; max-height: 90vh; overflow-y: auto; padding: var(--ia-space-lg); }
.modal-actions { display: flex; justify-content: flex-end; gap: var(--ia-space-sm); margin-top: var(--ia-space-md); }
</style>
