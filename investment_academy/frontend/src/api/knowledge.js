import api from './index'

export function getSectors() {
  return api.get('/knowledge/sectors')
}

export function getFactors() {
  return api.get('/knowledge/factors')
}

export function getMarketParams() {
  return api.get('/knowledge/market-params')
}

export function getRiskConstraints() {
  return api.get('/knowledge/risk-constraints')
}

export function getSetups() {
  return api.get('/knowledge/setups')
}
