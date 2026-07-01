import api from './index'

export function sandboxInit(etfCode, timeframe = 'day', initialCash = 100000) {
  return api.post('/sandbox/init', { etf_code: etfCode, timeframe, initial_cash: initialCash })
}

export function getSandboxState(sid) {
  return api.get(`/sandbox/${sid}/state`)
}

export function getSandboxBar(sid) {
  return api.get(`/sandbox/${sid}/bar`)
}

export function sandboxAdvance(sid) {
  return api.post(`/sandbox/${sid}/advance`)
}

export function sandboxBuy(sid, shares, reason = '') {
  return api.post(`/sandbox/${sid}/buy`, { shares, reason })
}

export function sandboxSell(sid, shares = 0, reason = '') {
  return api.post(`/sandbox/${sid}/sell`, { shares, reason })
}

export function getSandboxPortfolio(sid) {
  return api.get(`/sandbox/${sid}/portfolio`)
}

export function getSandboxPerformance(sid) {
  return api.get(`/sandbox/${sid}/performance`)
}

export function getSandboxEquityCurve(sid) {
  return api.get(`/sandbox/${sid}/equity-curve`)
}
