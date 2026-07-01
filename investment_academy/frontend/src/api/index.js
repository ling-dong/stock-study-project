import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// 响应拦截：统一错误处理
api.interceptors.response.use(
  res => res,
  err => {
    const msg = err.response?.data?.detail || err.message || '请求失败'
    console.error('[API Error]', msg)
    return Promise.reject(err)
  }
)

export default api

export function healthCheck() {
  return api.get('/health')
}
