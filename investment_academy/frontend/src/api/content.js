import api from './index'

export function getPhases() {
  return api.get('/content/phases')
}

export function getLabs() {
  return api.get('/content/labs')
}

export function getChapter(phaseId, filename) {
  return api.get(`/content/chapter/${phaseId}/${filename}`)
}

export function getQuiz(phaseId) {
  return api.get(`/content/quiz/${phaseId}`)
}

export function getLab(labId) {
  return api.get(`/content/lab/${labId}`)
}
