import api from './index'

export function getETFs() {
  return api.get('/market/etfs')
}

export function getETFMetadata() {
  return api.get('/market/etfs/meta')
}

export function getETFName(code) {
  return api.get(`/market/etf/${code}/name`)
}

export function getETFOHLCV(code, tf = 'day', limit = 180, offset = -1) {
  return api.get(`/market/etf/${code}/ohlcv`, { params: { tf, limit, offset } })
}
