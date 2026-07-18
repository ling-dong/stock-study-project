import api from './index'

/** POST /api/manual-analysis/analysis/{code} — 手动指标合成分析 */
export function analyzeETF(code, data) {
  return api.post(`/manual-analysis/analysis/${code}`, data, { timeout: 30000 })
}

/** GET /api/manual-analysis/system-info — 系统状态 */
export function getSystemInfo() {
  return api.get('/manual-analysis/system-info')
}

/** POST /api/manual-analysis/update-data — 更新数据 */
export function triggerDataUpdate() {
  return api.post('/manual-analysis/update-data', null, { timeout: 180000 })
}

/** GET /api/manual-analysis/history — 历史记录列表 */
export function getHistory(limit = 20) {
  return api.get('/manual-analysis/history', { params: { limit } })
}

/** GET /api/manual-analysis/history/{id} — 历史记录详情 */
export function getHistoryDetail(id) {
  return api.get(`/manual-analysis/history/${id}`)
}

/** DELETE /api/manual-analysis/history/{id} — 删除历史记录 */
export function deleteHistory(id) {
  return api.delete(`/manual-analysis/history/${id}`)
}
