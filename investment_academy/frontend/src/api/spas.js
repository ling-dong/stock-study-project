import api from './index'

/** POST /api/spas/analysis/{code} — 核心分析 */
export function analyzeETF(code, data) {
  return api.post(`/spas/analysis/${code}`, data, { timeout: 30000 })
}

/** GET /api/spas/system-info — 系统状态 */
export function getSystemInfo() {
  return api.get('/spas/system-info')
}

/** POST /api/spas/update-data — 更新数据 */
export function triggerDataUpdate() {
  return api.post('/spas/update-data', null, { timeout: 180000 })
}

/** GET /api/spas/history — 历史记录列表 */
export function getHistory(limit = 20) {
  return api.get('/spas/history', { params: { limit } })
}

/** GET /api/spas/history/{id} — 历史记录详情 */
export function getHistoryDetail(id) {
  return api.get(`/spas/history/${id}`)
}

/** DELETE /api/spas/history/{id} — 删除历史记录 */
export function deleteHistory(id) {
  return api.delete(`/spas/history/${id}`)
}
