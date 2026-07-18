import api from './index'

/** GET /api/spas/signal/{code} — SPAS 自动信号 */
export function getSPASSignal(code) {
  return api.get(`/spas/signal/${code}`, { timeout: 30000 })
}

/** GET /api/spas/market/etfs — 可用 ETF 列表 */
export function getSPASETFs() {
  return api.get('/spas/market/etfs')
}

/** GET /api/spas/market/etf/{code}/ohlcv — OHLCV 数据 */
export function getSPASOHLCV(code, freq = 'day', limit = 180) {
  return api.get(`/spas/market/etf/${code}/ohlcv`, {
    params: { freq, limit },
    timeout: 30000,
  })
}

/** GET /api/spas/system/status — SPAS 系统状态 */
export function getSPASSystemStatus() {
  return api.get('/spas/system/status')
}
