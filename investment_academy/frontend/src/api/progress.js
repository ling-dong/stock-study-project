import api from './index'

export function getProgress() {
  return api.get('/progress')
}

export function getChapterProgress(chapterId) {
  return api.get(`/progress/${chapterId}`)
}

export function updateProgress(chapterId, data) {
  return api.post(`/progress/${chapterId}`, data)
}
